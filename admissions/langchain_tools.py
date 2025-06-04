from admissions.models import OfferLetter, UserProfile
from django.utils import timezone
from datetime import timedelta

def get_pending_offers_over_3_days():
    threshold = timezone.now() - timedelta(days=3)
    offers = OfferLetter.objects.filter(status="sent", sent_at__lt=threshold)
    return "\n".join([f"{o.user.email} - Sent at {o.sent_at}" for o in offers])

def count_escalated_offers():
    count = OfferLetter.objects.filter(status="escalated").count()
    return f"{count} offer letters have been escalated."

def list_pending_offer_emails():
    offers = OfferLetter.objects.filter(status="sent")
    return "\n".join([o.user.email for o in offers])

def list_consultants_with_pending_offers():
    consultants = set(o.consultant.email for o in OfferLetter.objects.filter(status="sent") if o.consultant)
    return "\n".join(consultants)

def count_sent_offers_this_week():
    start = timezone.now() - timedelta(days=7)
    count = OfferLetter.objects.filter(status="sent", sent_at__gte=start).count()
    return f"{count} offers were sent in the last 7 days."

def students_with_escalated_offers():
    offers = OfferLetter.objects.filter(status="escalated")
    return "\n".join([o.user.email for o in offers])
