import logging
import whatsapp_notifier

logging.basicConfig(level=logging.INFO)

phone = "+917780731663"
print(f"Testing whatsapp_notifier with phone number {phone}...")

result = whatsapp_notifier.send_custom_reminder(
    phone=phone, 
    student_name="Student", 
    custom_message="This is a test reminder from Exam Coach AI."
)

if result:
    print("Test passed: function returned True.")
else:
    print("Test failed: function returned False.")
