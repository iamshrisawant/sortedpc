# [src/core/utils/notifier.py] — With Modern Toast Notifications

import logging
from pathlib import Path

# Action: Import a modern, dedicated library for Windows notifications.
# This is more reliable and simpler than using a general-purpose wrapper
# like plyer and eliminates the need for a complex PowerShell fallback.
try:
    from windows_toasts import Toast, WindowsToaster
    TOASTS_ENABLED = True
except ImportError:
    # If the library isn't installed, gracefully disable notifications
    # without crashing the application.
    TOASTS_ENABLED = False

logger = logging.getLogger(__name__)

# Action: Create a single, reusable toaster instance for the application.
# This is more efficient than creating a new notifier process for every toast.
if TOASTS_ENABLED:
    toaster = WindowsToaster('SortedPC')

def notify_file_sorted(file_path: str, final_folder: str, similar_folders: list):
    """
    Notifies the user that a file has been successfully sorted.
    This function is now simpler and more direct.
    """
    # The logger remains for internal tracking.
    logger.info(f"File sorted: {Path(file_path).name} -> {final_folder}")

    if not TOASTS_ENABLED:
        return

    # Action: Create and display a toast using simple object methods.
    try:
        new_toast = Toast()
        new_toast.text_fields = [f"Sorted: {Path(file_path).name}", f"Destination: {final_folder}"]
        
        # This approach makes it easy to add more features in the future,
        # such as icons or buttons, without complex string manipulation.
        # Example:
        # from src.core.utils.paths import get_icon_path
        # if get_icon_path().exists():
        #     new_toast.AddImage(ToastDisplayImage.fromPath(str(get_icon_path())))

        toaster.show_toast(new_toast)
    except Exception as e:
        # The error handling is now simpler, as we only have one notification method.
        logger.warning(f"Failed to send toast notification: {e}")

def notify_system_event(title: str, message: str):
    """Notifies the user of a high-level system event (e.g., startup, shutdown)."""
    logger.info(f"System Event: {title} - {message}")

    if not TOASTS_ENABLED:
        return

    try:
        new_toast = Toast()
        new_toast.text_fields = [title, message]
        toaster.show_toast(new_toast)
    except Exception as e:
        logger.warning(f"Failed to send system event toast: {e}")
