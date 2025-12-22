from __future__ import annotations

from datetime import timedelta
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from bookings.models import Booking

try:
    from twilio.rest import Client  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Client = None  # type: ignore


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send email/SMS reminders for appointments happening within the next 24 hours"

    def handle(self, *args, **options):
        now = timezone.now()
        start = now
        end = now + timedelta(hours=24)

        qs = Booking.objects.filter(
            date__gte=start.date(),
            date__lte=end.date(),
        )

        logger.info(
            "Preparing reminders",
            extra={
                "window_start": start.isoformat(),
                "window_end": end.isoformat(),
                "count": qs.count(),
            },
        )

        # Build aware datetimes for comparison
        reminders = []
        for b in qs.select_related("worker"):
            dt = timezone.make_aware(timezone.datetime.combine(b.date, b.time))
            if start <= dt <= end:
                reminders.append((b, dt))

        # Email reminders
        for booking, dt in reminders:
            if booking.email:
                subject = "Appointment reminder"
                body = f"Reminder: Your appointment with {booking.worker.full_name} is on {booking.date} at {booking.time}."
                try:
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [booking.email], fail_silently=True)
                    logger.info(
                        "Sent reminder email",
                        extra={"booking_id": booking.id, "email": booking.email},
                    )
                except Exception:
                    logger.exception(
                        "Failed to send reminder email",
                        extra={"booking_id": booking.id, "email": booking.email},
                    )

        # SMS reminders via Twilio
        if Client and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            for booking, dt in reminders:
                if booking.phone:
                    msg = f"Reminder: appointment {booking.date} {booking.time} with {booking.worker.full_name}."
                    try:
                        client.messages.create(
                            body=msg,
                            from_=settings.TWILIO_FROM_NUMBER,
                            to=booking.phone,
                        )
                        logger.info(
                            "Sent reminder SMS",
                            extra={"booking_id": booking.id, "phone": booking.phone},
                        )
                    except Exception:
                        logger.exception(
                            "Failed to send reminder SMS",
                            extra={"booking_id": booking.id, "phone": booking.phone},
                        )
        else:
            logger.info("Skipping SMS reminders; Twilio not configured or client unavailable")

        self.stdout.write(self.style.SUCCESS(f"Processed {len(reminders)} reminders"))





