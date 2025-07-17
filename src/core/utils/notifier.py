import logging
import platform
import subprocess
from pathlib import Path
from typing import List, Optional

from plyer import notification

# --- Logger Setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --- File Event Notification (used by actor) ---
def notify_file_sorted(
    file_path: str,
    final_folder: str,
    similar_folders: Optional[List[str]] = None
) -> None:
    file_name = Path(file_path).name
    title = "File Sorted"
    message = f"{file_name} was sorted into:\n{final_folder}"

    if similar_folders:
        sim_text = ", ".join(similar_folders[:3])
        message += f"\nSimilar folders: {sim_text}"

    _notify(title, message)


# --- System Events (used by watcher, builder, initializer) ---
def notify_system_event(event: str, detail: Optional[str] = None) -> None:
    title = f"[SortedPC] {event}"
    message = detail or ""
    _notify(title, message)


# --- Internal notification handler ---
def _notify(title: str, message: str) -> None:
    truncated_msg = message[:247] + "..." if len(message) > 250 else message

    try:
        notification.notify(
            title=title,
            message=truncated_msg,
            timeout=5  # seconds
        )
        logger.info(f"[Notifier] Toast sent using plyer: {title}")
    except Exception as e:
        logger.warning(f"[Notifier] plyer failed: {e}")
        _powershell_fallback(title, truncated_msg)


# --- PowerShell Fallback (in case plyer fails) ---
def _powershell_fallback(title: str, message: str) -> None:
    if platform.system() == "Windows":
        try:
            escaped_title = title.replace('"', '`"')
            escaped_msg = message.replace('"', '`"')

            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $template.SelectSingleNode("//text[@id=1]").InnerText = "{escaped_title}"
            $template.SelectSingleNode("//text[@id=2]").InnerText = "{escaped_msg}"
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SortedPC")
            $notifier.Show($toast)
            '''

            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
            logger.info("[Notifier] PowerShell fallback toast sent.")
        except Exception as fallback_error:
            logger.warning(f"[Notifier] PowerShell fallback failed: {fallback_error}")
