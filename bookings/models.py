from __future__ import annotations

from django.db import models
from django.core.validators import RegexValidator


class Worker(models.Model):
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="workers/", blank=True, null=True)

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
        # Use service duration if available, otherwise default to 60 minutes
        duration = self.service.duration_minutes if self.service else 60
        return start_datetime + timedelta(minutes=duration)

    @classmethod
    def has_conflict(cls, worker, date, time, service, exclude_booking=None):
        """Check if there's a time conflict for the given worker, date, time, and service."""
        from datetime import datetime, timedelta
        
        # Calculate the end time for the new booking
        start_datetime = datetime.combine(date, time)
        # Use service duration if available, otherwise default to 60 minutes
        duration = service.duration_minutes if service else 60
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Get all existing bookings for this worker on this date
        existing_bookings = cls.objects.filter(worker=worker, date=date)
        if exclude_booking:
            existing_bookings = existing_bookings.exclude(id=exclude_booking.id)
        
        # Check for conflicts
        for booking in existing_bookings:
            existing_start = datetime.combine(booking.date, booking.time)
            existing_end = booking.end_time
            
            # Check if the new booking overlaps with any existing booking
            if (start_datetime < existing_end and end_datetime > existing_start):
                return True
        
        return False


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



