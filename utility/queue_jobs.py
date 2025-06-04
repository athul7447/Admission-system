from celery import shared_task
from django.core.mail import EmailMessage
import os

# @shared_task
def send_offer_letter_email(student_email, subject, message, attachment_path):
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            to=[student_email]
        )
        
        if attachment_path and os.path.exists(attachment_path):
            email.attach_file(attachment_path)

        email.send()
        return f"Email sent to {student_email}"
    except Exception as e:
        return f"Failed to send email to {student_email}: {str(e)}"


@shared_task
def test_email_task():
    print("Test email task executed")
    return "Done"