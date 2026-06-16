import subprocess
import logging

logger = logging.getLogger("AURA.notify")

def send_notification(title: str, message: str )-> bool:
    """ show a macOS  banner notification . Return True on success """
    safe_title = title.replace('"','\\"')
    safe_message = message.replace('"','\\"')
    script = (
        f' display notification "{safe_message}" '
        f' with title "{safe_title}" sound name "Glass"'

    )
    try :
        subprocess.run(["osascript", "-e" , script],
                       check = False,
                       timeout=5,)
        return True
    except Exception as e:
        logger.error("unable to send notification: %s", e)
        return False
