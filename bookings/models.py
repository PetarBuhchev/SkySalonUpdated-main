from __future__ import annotations

import datetime

from django.core.validators import RegexValidator
from django.core.signing import Signer
from django.db import models
from django.conf import settings


class Worker(models.Model):
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="workers/", blank=True, null=True)
    working_hours_start = models.TimeField(default=datetime.time(9, 0))
    working_hours_end = models.TimeField(default=datetime.time(18, 0))

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:  # pragma: no cover - admin/readability only
        return self.full_name


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Duration in minutes")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Booking(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    email = models.EmailField(blank=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^[0-9+\-\s]{7,20}$", "Enter a valid phone number.")],
        help_text="Contact phone number",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("worker", "date", "time")
        ordering = ["-date", "-time"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.date} {self.time} - {self.worker}"

    @property
    def end_time(self):
        """Calculate the end time of this booking based on service duration."""
        from datetime import datetime, timedelta
        start_datetime = datetime.combine(self.date, self.time)
        duration = self.get_duration_minutes()
        return start_datetime + timedelta(minutes=duration)

    def get_duration_minutes(self) -> int:
        """Return duration for this booking using worker-specific price if present."""
        if self.worker and self.service:
            price = WorkerServicePrice.objects.filter(worker=self.worker, service=self.service).first()
            if price:
                return price.duration_minutes
            return self.service.duration_minutes
        return 60

    @classmethod
    def has_conflict(cls, worker, date, time, service, exclude_booking=None):
        """Check if there's a time conflict for the given worker, date, time, and service."""
        from datetime import datetime, timedelta

        # Calculate the end time for the new booking
        start_datetime = datetime.combine(date, time)
        # Use worker-specific duration when possible
        duration = cls._duration_for_worker_service(worker, service)
        end_datetime = start_datetime + timedelta(minutes=duration)

        # Get all existing bookings for this worker on this date
        existing_bookings = cls.objects.filter(worker=worker, date=date)
        if exclude_booking:
            existing_bookings = existing_bookings.exclude(id=exclude_booking.id)

        # Check for conflicts
        for booking in existing_bookings:
            existing_start = datetime.combine(booking.date, booking.time)
            existing_duration = cls._duration_for_worker_service(worker, booking.service)
            existing_end = existing_start + timedelta(minutes=existing_duration)

            # Check if the new booking overlaps with any existing booking
            if (start_datetime < existing_end and end_datetime > existing_start):
                return True

        return False

    @staticmethod
    def _duration_for_worker_service(worker: Worker, service: Service | None) -> int:
        """Return duration minutes using worker-specific price when available."""
        if worker and service:
            price = WorkerServicePrice.objects.filter(worker=worker, service=service).first()
            if price:
                return price.duration_minutes
            return service.duration_minutes
        return 60

    def get_cancellation_token(self) -> str:
        """Generate a secure cancellation token for this booking."""
        signer = Signer()
        return signer.sign(f"booking_{self.id}")

    @classmethod
    def from_cancellation_token(cls, token: str):
        """Retrieve a booking from a cancellation token."""
        try:
            signer = Signer()
            unsigned = signer.unsign(token)
            if unsigned.startswith("booking_"):
                booking_id = int(unsigned.split("_")[1])
                return cls.objects.get(id=booking_id)
        except (ValueError, cls.DoesNotExist, Exception):
            return None


class WorkerServicePrice(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="service_prices")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="worker_prices")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)

    class Meta:
        unique_together = ("worker", "service")
        ordering = ["worker__full_name", "service__name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.worker} - {self.service}: {self.price}"



