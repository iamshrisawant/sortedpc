# learner.py
from collections import Counter, defaultdict
from db import (
    fetch_all_files,
    fetch_unorganized_files,
    update_organization_status_for_folder,
    fetch_folder_summary
)

def extract_folder_features(files):
    """
    Given a list of file records, extract features per folder.
    """
    folder_features = defaultdict(lambda: {
        'extensions': Counter(),
        'sizes': [],
        'file_count': 0,
        'hidden_count': 0
    })

    for file in files:
        folder = file[7]  # parent_folder
        ext = file[3] or 'unknown'
        size = file[4] or 0
        is_hidden = file[9]

        folder_features[folder]['extensions'][ext] += 1
        folder_features[folder]['sizes'].append(size)
        folder_features[folder]['file_count'] += 1
        if is_hidden:
            folder_features[folder]['hidden_count'] += 1

    return folder_features

def is_organized(features):
    """
    Heuristic function to determine if folder is organized.
    """
    exts = features['extensions']
    total = features['file_count']

    if total == 0:
        return False

    dominant_ratio = max(exts.values()) / total
    unique_exts = len(exts)

    if dominant_ratio >= 0.7 and unique_exts <= 3:
        return True

    return False

def infer_folder_organization():
    """
    Main entry point for learner.
    Analyzes all folders and updates organization status.
    """
    files = fetch_all_files()
    folder_data = extract_folder_features(files)

    for folder, features in folder_data.items():
        status = 'organized' if is_organized(features) else 'unorganized'
        update_organization_status_for_folder(folder, status)

def relearn():
    """
    Re-learns using existing metadata + user feedback.
    Currently same as `infer_folder_organization`.
    Future: adapt using feedback to refine heuristics or train ML.
    """
    infer_folder_organization()
