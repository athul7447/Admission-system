from django.utils import timezone
from datetime import timedelta
from admissions.models import OfferLetter, AuditLog, UserProfile
from django.core.mail import EmailMessage
from django.conf import settings

def send_reminder_and_escalate():
    """
    Sends a reminder email to students and consultants if an offer letter
    remains unsigned for 3 days, and escalates the case if it remains unsigned
    for 5 days.

    This function is intended to be run as a cron job every 15 minutes.
    """
    now = timezone.now()
    all_offers = OfferLetter.objects.filter(status="sent", escalated=False)
    print("Entered send_reminder_and_escalate function")

    for offer in all_offers:
        try:
            days_passed = (now - offer.sent_at).days
            
            if days_passed >= 3  and not offer.is_remider_sent:
                subject = "Reminder: Offer Letter Not Signed"
                message = "Please sign the offer letter sent to you. This is a gentle reminder."
                recipients = [offer.student.email, offer.user.email]
                send_notification_email(
                    subject,
                    message, 
                    recipients)
                offer.is_remider_sent = True
                offer.save()
                log_action(
                    f"Reminder sent to {offer.student.email}", 
                    user=offer.student.id,
                    offer=offer.id,
                )

            if days_passed >= 5:
                offer.status = "escalated"
                offer.escalated = True
                offer.save()

                subject = "Escalation: Offer Letter Still Not Signed"
                message = f"The offer letter for {offer.user.email} has not been signed in 5 days. Please take action."
                
                users = UserProfile.objects.filter(role="team_lead")
                recipients = [team_lead.user.email for team_lead in users]

                if recipients:
                    send_notification_email(subject, message, recipients)
                log_action(
                    f"Escalated offer for {offer.user.email} to team lead", 
                    user=offer.user,
                    offer=offer)
        except Exception as e:
            print(e)

    print("Exited send_reminder_and_escalate function")

def send_notification_email(subject, message, recipients):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )

    email.send(fail_silently=False)

def log_action(action, user=None, offer=None):
    AuditLog.objects.create(
        offer_letter=offer,
        action=action,
        user=user,
    )
