from django.utils import timezone
from datetime import timedelta
from admissions.models import OfferLetter, AuditLog, UserProfile
from django.core.mail import send_mail
from django.conf import settings

def send_reminder_and_escalate():
    now = timezone.now()
    all_offers = OfferLetter.objects.filter(status="sent",escalated=False)

    for offer in all_offers:
        days_passed = (now - offer.sent_at).days

        if days_passed >= 3:
            # Reminder email to student and consultant
            subject = "Reminder: Offer Letter Not Signed"
            message = "Please sign the offer letter sent to you. This is a gentle reminder."
            recipients = [offer.user.email]
            offer.is_remider_sent = True
            offer.save()
            send_notification_email(subject, message, recipients)
            _log_action(f"Reminder sent to {offer.user.email}", user=offer.user)

        if days_passed >= 5:
            # Escalate the case
            offer.status = "escalated"
            offer.escalated = True
            offer.save()

            # Escalation email to team lead
            subject = "Escalation: Offer Letter Still Not Signed"
            message = f"The offer letter for {offer.user.email} has not been signed in 5 days. Please take action."
            
            users = UserProfile.objects.filter(role="team_lead")
            recipients = [team_lead.user.email for team_lead in users]

            if recipients:
                send_notification_email(subject, message, recipients)
            _log_action(f"Escalated offer for {offer.user.email}", user=offer.user)


def send_notification_email(subject, message, recipients):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False
    )


def _log_action(action, user=None):
    AuditLog.objects.create(
        action=action,
        user=user,
        timestamp=timezone.now()
    )
