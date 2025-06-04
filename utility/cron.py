from django.utils import timezone
from datetime import timedelta
from admissions.models import OfferLetter, AuditLog

def send_reminder_and_escalate():
    now = timezone.now()
    all_offers = OfferLetter.objects.filter(status="sent")

    for offer in all_offers:
        days_passed = (now - offer.sent_at).days

        if days_passed >= 3 and not offer.escalated:
            # Send reminder
            # email_student_and_consultant(offer)
            AuditLog.objects.create(
                offer_letter=offer,
                action="Reminder sent",
                user=offer.consultant,
            )

        if days_passed >= 5 and not offer.escalated:
            offer.status = "escalated"
            offer.escalated = True
            offer.save()
            AuditLog.objects.create(
                offer_letter=offer,
                action="Escalated to Team Lead",
                user=offer.consultant,
            )
