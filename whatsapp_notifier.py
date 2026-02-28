"""
WhatsApp notifier using pywhatkit (no API keys required).
WhatsApp Web must be open and logged-in in Chrome before calling these functions.
"""
import logging
import datetime

logger = logging.getLogger(__name__)


def _send(phone: str, message: str) -> bool:
    """Core send function. Returns True on success."""
    try:
        import pywhatkit
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone,
            message=message,
            wait_time=12,
            tab_close=True,
            close_time=4
        )
        logger.info(f"✅ WhatsApp sent to {phone}")
        return True
    except ImportError:
        logger.warning("pywhatkit not installed. Run: pip install pywhatkit")
        return False
    except Exception as e:
        logger.error(f"❌ WhatsApp failed for {phone}: {e}")
        return False


def send_daily_reminder(phone: str, student_name: str, topics: list, exam_type: str) -> bool:
    today = datetime.date.today().strftime("%A, %d %B")
    topics_text = "\n".join([f"  • {t}" for t in topics])
    message = (
        f"📚 Good morning {student_name}!\n\n"
        f"Your {exam_type} study tasks for {today}:\n"
        f"{topics_text}\n\n"
        f"Stay focused — you've got this! 💪\n"
        f"Open Exam Coach AI to start studying."
    )
    return _send(phone, message)


def send_plan_ready(phone: str, student_name: str, exam_type: str) -> bool:
    message = (
        f"✅ {student_name}, your personalised 7-day {exam_type} "
        f"revision plan is ready!\n\n"
        f"Open Exam Coach AI to view your full schedule 📅"
    )
    return _send(phone, message)


def send_analysis_done(phone: str, student_name: str, weak_topics: list) -> bool:
    topics_text = "\n".join([f"  ⚠️ {t}" for t in weak_topics[:5]])
    message = (
        f"📊 {student_name}, your test analysis is complete!\n\n"
        f"Focus areas:\n{topics_text}\n\n"
        f"Visit the Resources page for free study materials 📖"
    )
    return _send(phone, message)


def send_error_pattern_report(phone: str, student_name: str, top_errors: list) -> bool:
    errors_text = "\n".join([f"  🔴 {e.get('topic','?')} — {e.get('error_type','?')}" for e in top_errors[:4]])
    message = (
        f"🧠 {student_name}, multi-sheet error analysis done!\n\n"
        f"Top recurring errors:\n{errors_text}\n\n"
        f"Check your Error Pattern page to fix these 🎯"
    )
    return _send(phone, message)


def send_custom_reminder(phone: str, student_name: str, custom_message: str) -> bool:
    message = f"🔔 Hi {student_name}!\n\n{custom_message}\n\n— Exam Coach AI"
    return _send(phone, message)


def send_discussion_reply(phone: str, student_name: str, post_title: str) -> bool:
    message = (
        f"💬 {student_name}, your discussion post received a new reply!\n\n"
        f"Post: \"{post_title[:60]}\"\n\n"
        f"Open the Discussions page to see the response 👥"
    )
    return _send(phone, message)
