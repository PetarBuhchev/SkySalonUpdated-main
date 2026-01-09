"""
Unit tests for booking system models.
"""
from __future__ import annotations

from datetime import date, time, datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Worker, Service, Booking, WorkerServicePrice


class WorkerModelTest(TestCase):
    """Test cases for Worker model."""

    def setUp(self):
        """Set up test fixtures."""
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
            role="Hair Stylist",
            bio="Experienced stylist",
            working_hours_start=time(9, 0),
            working_hours_end=time(18, 0),
        )

    def test_worker_creation(self):
        """Test creating a worker."""
        self.assertEqual(self.worker.full_name, "John Doe")
        self.assertTrue(self.worker.is_active)
        self.assertEqual(self.worker.role, "Hair Stylist")
        self.assertEqual(self.worker.bio, "Experienced stylist")
        self.assertEqual(self.worker.working_hours_start, time(9, 0))
        self.assertEqual(self.worker.working_hours_end, time(18, 0))

    def test_worker_str(self):
        """Test worker string representation."""
        self.assertEqual(str(self.worker), "John Doe")

    def test_worker_defaults(self):
        """Test worker default values."""
        worker = Worker.objects.create(full_name="Jane Smith")
        self.assertTrue(worker.is_active)
        self.assertEqual(worker.working_hours_start, time(9, 0))
        self.assertEqual(worker.working_hours_end, time(18, 0))

    def test_worker_ordering(self):
        """Test worker ordering by full_name."""
        worker1 = Worker.objects.create(full_name="Alice")
        worker2 = Worker.objects.create(full_name="Bob")
        workers = list(Worker.objects.all())
        self.assertEqual(workers[0].full_name, "Alice")
        self.assertEqual(workers[1].full_name, "Bob")


class ServiceModelTest(TestCase):
    """Test cases for Service model."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = Service.objects.create(
            name="Haircut",
            description="Professional haircut",
            duration_minutes=30,
        )

    def test_service_creation(self):
        """Test creating a service."""
        self.assertEqual(self.service.name, "Haircut")
        self.assertEqual(self.service.description, "Professional haircut")
        self.assertEqual(self.service.duration_minutes, 30)

    def test_service_str(self):
        """Test service string representation."""
        self.assertEqual(str(self.service), "Haircut")

    def test_service_default_duration(self):
        """Test service default duration."""
        service = Service.objects.create(name="Massage")
        self.assertEqual(service.duration_minutes, 60)

    def test_service_unique_name(self):
        """Test that service names must be unique."""
        Service.objects.create(name="Unique Service")
        with self.assertRaises(Exception):  # IntegrityError
            Service.objects.create(name="Unique Service")

    def test_service_ordering(self):
        """Test service ordering by name."""
        service1 = Service.objects.create(name="A Service")
        service2 = Service.objects.create(name="B Service")
        services = list(Service.objects.all())
        self.assertEqual(services[0].name, "A Service")
        self.assertEqual(services[1].name, "B Service")


class BookingModelTest(TestCase):
    """Test cases for Booking model."""

    def setUp(self):
        """Set up test fixtures."""
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
        )
        self.service = Service.objects.create(
            name="Haircut",
            duration_minutes=30,
        )
        self.future_date = date.today() + timedelta(days=1)
        self.future_time = time(14, 0)

    def test_booking_creation(self):
        """Test creating a booking."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            email="customer@example.com",
            phone="+1234567890",
        )
        self.assertEqual(booking.worker, self.worker)
        self.assertEqual(booking.service, self.service)
        self.assertEqual(booking.date, self.future_date)
        self.assertEqual(booking.time, self.future_time)
        self.assertEqual(booking.email, "customer@example.com")
        self.assertEqual(booking.phone, "+1234567890")

    def test_booking_str(self):
        """Test booking string representation."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        expected = f"{self.future_date} {self.future_time} - {self.worker}"
        self.assertEqual(str(booking), expected)

    def test_booking_unique_together(self):
        """Test that worker, date, and time combination must be unique."""
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        with self.assertRaises(Exception):  # IntegrityError
            Booking.objects.create(
                worker=self.worker,
                service=self.service,
                date=self.future_date,
                time=self.future_time,
                phone="+9876543210",
            )

    def test_booking_phone_validation(self):
        """Test phone number validation."""
        booking = Booking(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="invalid",
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_booking_get_duration_minutes_with_service(self):
        """Test getting duration when service has default duration."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        self.assertEqual(booking.get_duration_minutes(), 30)

    def test_booking_get_duration_minutes_with_worker_service_price(self):
        """Test getting duration from worker-specific price."""
        WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        self.assertEqual(booking.get_duration_minutes(), 45)

    def test_booking_get_duration_minutes_no_service(self):
        """Test getting default duration when no service."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=None,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        self.assertEqual(booking.get_duration_minutes(), 60)

    def test_booking_end_time(self):
        """Test calculating booking end time."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        expected_end = datetime.combine(self.future_date, self.future_time) + timedelta(minutes=30)
        self.assertEqual(booking.end_time, expected_end)

    def test_booking_end_time_with_worker_price(self):
        """Test calculating end time with worker-specific duration."""
        WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=90,
        )
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
        )
        expected_end = datetime.combine(self.future_date, self.future_time) + timedelta(minutes=90)
        self.assertEqual(booking.end_time, expected_end)

    def test_booking_has_conflict_no_conflict(self):
        """Test conflict detection when no conflict exists."""
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # New booking at 11:00 (30 min duration, ends at 11:30) shouldn't conflict
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(11, 0),
            self.service,
        )
        self.assertFalse(has_conflict)

    def test_booking_has_conflict_overlapping_start(self):
        """Test conflict detection with overlapping start time."""
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # New booking at 10:15 (30 min duration, ends at 10:45) conflicts with existing (10:00-10:30)
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(10, 15),
            self.service,
        )
        self.assertTrue(has_conflict)

    def test_booking_has_conflict_overlapping_end(self):
        """Test conflict detection with overlapping end time."""
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # New booking at 9:45 (30 min duration, ends at 10:15) conflicts with existing (10:00-10:30)
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(9, 45),
            self.service,
        )
        self.assertTrue(has_conflict)

    def test_booking_has_conflict_exact_overlap(self):
        """Test conflict detection with exact overlap."""
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # New booking at same time conflicts
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(10, 0),
            self.service,
        )
        self.assertTrue(has_conflict)

    def test_booking_has_conflict_exclude_booking(self):
        """Test conflict detection excluding a specific booking."""
        existing_booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # Should not conflict with itself when excluded
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(10, 0),
            self.service,
            exclude_booking=existing_booking,
        )
        self.assertFalse(has_conflict)

    def test_booking_has_conflict_different_worker(self):
        """Test that conflicts only check same worker."""
        other_worker = Worker.objects.create(full_name="Jane Smith")
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # Different worker, same time - no conflict
        has_conflict = Booking.has_conflict(
            other_worker,
            self.future_date,
            time(10, 0),
            self.service,
        )
        self.assertFalse(has_conflict)

    def test_booking_has_conflict_different_date(self):
        """Test that conflicts only check same date."""
        other_date = self.future_date + timedelta(days=1)
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # Same worker, different date - no conflict
        has_conflict = Booking.has_conflict(
            self.worker,
            other_date,
            time(10, 0),
            self.service,
        )
        self.assertFalse(has_conflict)

    def test_booking_has_conflict_different_durations(self):
        """Test conflict detection with different service durations."""
        long_service = Service.objects.create(name="Long Service", duration_minutes=120)
        Booking.objects.create(
            worker=self.worker,
            service=long_service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        # New booking at 11:30 (30 min, ends at 12:00) conflicts with existing (10:00-12:00)
        has_conflict = Booking.has_conflict(
            self.worker,
            self.future_date,
            time(11, 30),
            self.service,
        )
        self.assertTrue(has_conflict)

    def test_booking_duration_for_worker_service_with_price(self):
        """Test duration calculation with worker-specific price."""
        WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )
        duration = Booking._duration_for_worker_service(self.worker, self.service)
        self.assertEqual(duration, 45)

    def test_booking_duration_for_worker_service_without_price(self):
        """Test duration calculation without worker-specific price."""
        duration = Booking._duration_for_worker_service(self.worker, self.service)
        self.assertEqual(duration, 30)  # Service default

    def test_booking_duration_for_worker_service_no_service(self):
        """Test duration calculation with no service."""
        duration = Booking._duration_for_worker_service(self.worker, None)
        self.assertEqual(duration, 60)  # Default

    def test_booking_ordering(self):
        """Test booking ordering by date and time (descending)."""
        booking1 = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        booking2 = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date + timedelta(days=1),
            time=time(14, 0),
            phone="+1234567890",
        )
        bookings = list(Booking.objects.all())
        self.assertEqual(bookings[0], booking2)  # More recent first
        self.assertEqual(bookings[1], booking1)


class WorkerServicePriceModelTest(TestCase):
    """Test cases for WorkerServicePrice model."""

    def setUp(self):
        """Set up test fixtures."""
        self.worker = Worker.objects.create(full_name="John Doe")
        self.service = Service.objects.create(name="Haircut", duration_minutes=30)

    def test_worker_service_price_creation(self):
        """Test creating a worker service price."""
        price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )
        self.assertEqual(price.worker, self.worker)
        self.assertEqual(price.service, self.service)
        self.assertEqual(price.price, 50.00)
        self.assertEqual(price.duration_minutes, 45)

    def test_worker_service_price_str(self):
        """Test worker service price string representation."""
        price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )
        expected = f"{self.worker} - {self.service}: {price.price}"
        self.assertEqual(str(price), expected)

    def test_worker_service_price_unique_together(self):
        """Test that worker and service combination must be unique."""
        WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )
        with self.assertRaises(Exception):  # IntegrityError
            WorkerServicePrice.objects.create(
                worker=self.worker,
                service=self.service,
                price=60.00,
                duration_minutes=60,
            )

    def test_worker_service_price_default_duration(self):
        """Test default duration for worker service price."""
        price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
        )
        self.assertEqual(price.duration_minutes, 60)

    def test_worker_service_price_ordering(self):
        """Test worker service price ordering."""
        worker1 = Worker.objects.create(full_name="Alice")
        worker2 = Worker.objects.create(full_name="Bob")
        service1 = Service.objects.create(name="Service A")
        service2 = Service.objects.create(name="Service B")
        
        price1 = WorkerServicePrice.objects.create(worker=worker1, service=service1, price=50.00)
        price2 = WorkerServicePrice.objects.create(worker=worker1, service=service2, price=60.00)
        price3 = WorkerServicePrice.objects.create(worker=worker2, service=service1, price=70.00)
        
        prices = list(WorkerServicePrice.objects.all())
        self.assertEqual(prices[0], price1)
        self.assertEqual(prices[1], price2)
        self.assertEqual(prices[2], price3)

