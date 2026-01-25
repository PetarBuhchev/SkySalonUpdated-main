"""
Unit tests for booking system forms.
"""
from __future__ import annotations

from datetime import date, time, datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django import forms

from bookings.forms import BookingForm
from bookings.models import Worker, Service, Booking


class BookingFormTest(TestCase):
    """Test cases for BookingForm."""

    def setUp(self):
        """Set up test fixtures."""
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
        )
        self.inactive_worker = Worker.objects.create(
            full_name="Inactive Worker",
            is_active=False,
        )
        self.service = Service.objects.create(
            name="Haircut",
            duration_minutes=30,
        )
        self.future_date = date.today() + timedelta(days=1)
        self.future_time = time(14, 0)
        self.past_date = date.today() - timedelta(days=1)
        self.past_time = time(10, 0)

    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
            "email": "customer@example.com",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_required_fields(self):
        """Test that required fields are enforced."""
        form = BookingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("worker", form.errors)
        self.assertIn("service", form.errors)
        self.assertIn("date", form.errors)
        self.assertIn("time", form.errors)
        self.assertIn("phone", form.errors)

    def test_form_email_optional(self):
        """Test that email is optional."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_only_active_workers(self):
        """Test that only active workers are available in form."""
        form = BookingForm()
        worker_queryset = form.fields["worker"].queryset
        self.assertIn(self.worker, worker_queryset)
        self.assertNotIn(self.inactive_worker, worker_queryset)

    def test_form_past_date_validation(self):
        """Test that past dates are rejected."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.past_date,
            "time": self.past_time,
            "phone": "+1234567890",
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_past_datetime_validation(self):
        """Test that past date/time combinations are rejected."""
        # Use today's date but a past time
        today = date.today()
        past_time = (timezone.now() - timedelta(hours=1)).time()
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": today,
            "time": past_time,
            "phone": "+1234567890",
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_future_datetime_validation(self):
        """Test that future date/time combinations are accepted."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_conflict_validation(self):
        """Test that conflicting bookings are rejected."""
        # Create an existing booking
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(14, 0),
            phone="+1234567890",
        )
        # Try to create a conflicting booking
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": time(14, 15),  # Overlaps with existing booking
            "phone": "+9876543210",
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_no_conflict_validation(self):
        """Test that non-conflicting bookings are accepted."""
        # Create an existing booking
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # Try to create a non-conflicting booking
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": time(11, 0),  # No overlap (10:00-10:30 vs 11:00-11:30)
            "phone": "+9876543210",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_conflict_different_worker(self):
        """Test that conflicts only apply to same worker."""
        other_worker = Worker.objects.create(full_name="Jane Smith", is_active=True)
        # Create an existing booking for first worker
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(14, 0),
            phone="+1234567890",
        )
        # Try to create booking for different worker at same time
        form_data = {
            "worker": other_worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": time(14, 0),
            "phone": "+9876543210",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_conflict_different_date(self):
        """Test that conflicts only apply to same date."""
        other_date = self.future_date + timedelta(days=1)
        # Create an existing booking
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(14, 0),
            phone="+1234567890",
        )
        # Try to create booking for different date at same time
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": other_date,
            "time": time(14, 0),
            "phone": "+9876543210",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form can save a booking."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
            "email": "customer@example.com",
        }
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())
        booking = form.save()
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.worker, self.worker)
        self.assertEqual(booking.service, self.service)
        self.assertEqual(booking.date, self.future_date)
        self.assertEqual(booking.time, self.future_time)
        self.assertEqual(booking.email, "customer@example.com")
        self.assertEqual(booking.phone, "+1234567890")

    def test_form_phone_validation(self):
        """Test phone number validation."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "invalid",
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_form_phone_valid_formats(self):
        """Test various valid phone formats."""
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "123 456 7890",
            "+1 234 567 890",
        ]
        for phone in valid_phones:
            form_data = {
                "worker": self.worker.id,
                "service": self.service.id,
                "date": self.future_date,
                "time": self.future_time,
                "phone": phone,
            }
            form = BookingForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Phone {phone} should be valid")

    def test_form_initial_data(self):
        """Test form with initial data."""
        initial = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
        }
        form = BookingForm(initial=initial)
        self.assertEqual(form["worker"].value(), self.worker.id)
        self.assertEqual(form["service"].value(), self.service.id)
        self.assertEqual(form["date"].value(), self.future_date)
        self.assertEqual(form["time"].value(), self.future_time)





