from plyer import notification
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def notify_user(
    file_path: str,
    final_folder: str,
    similar_folders: Optional[List[str]] = None
) -> None:
    """
    Sends a desktop notification about a file move.

    Args:
        file_path (str): Path of the file that was moved.
        final_folder (str): Folder where file was moved.
        similar_folders (List[str], optional): List of similar folders found during sort.
    """
    file_name = Path(file_path).name
    title = "File Sorted"
    message = f"{file_name} was sorted to:\n{final_folder}"

    if similar_folders:
        sim_text = ", ".join(similar_folders[:3])  # Show top 3 similar folders
        message += f"\nSimilar folders: {sim_text}"

    _notify(title, message)


def notify_system_event(event: str, detail: Optional[str] = None):
    """
    Sends a desktop notification for system-level events.

    Args:
        event (str): Title of the event.
        detail (str, optional): Additional detail message.
    """
    title = f"[SortedPC] {event}"
    message = detail or ""
    _notify(title, message)


def _notify(title: str, message: str):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="SortedPC",
            timeout=10
        )
        logger.info(f"[Notifier] Notification sent: {title}")
    except Exception as e:
        logger.warning(f"[Notifier] Failed to send notification: {e}")
