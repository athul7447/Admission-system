from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admissions'

    def ready(self):
        import admissions.signals
        
        from utility.appscheduler import send_reminder_and_escalate

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            send_reminder_and_escalate,
            trigger=IntervalTrigger(minutes=5),  # adjust as needed
            id="offer_letter_reminder",
            name="Send offer letter reminders and escalations",
            replace_existing=True
        )
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())