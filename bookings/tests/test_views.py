"""
Unit tests for booking system views.
"""
from __future__ import annotations

from datetime import date, time, datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from django.core import mail

from bookings.models import Worker, Service, Booking, WorkerServicePrice


class HomeViewTest(TestCase):
    """Test cases for home view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.active_worker = Worker.objects.create(
            full_name="Active Worker",
            is_active=True,
        )
        self.inactive_worker = Worker.objects.create(
            full_name="Inactive Worker",
            is_active=False,
        )

    def test_home_view_get(self):
        """Test home view GET request."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/home.html")

    def test_home_view_only_active_workers(self):
        """Test that only active workers are shown."""
        response = self.client.get(reverse("home"))
        workers = response.context["workers"]
        self.assertIn(self.active_worker, workers)
        self.assertNotIn(self.inactive_worker, workers)


class BookViewTest(TestCase):
    """Test cases for book view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
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

    def test_book_view_get(self):
        """Test book view GET request."""
        response = self.client.get(reverse("book"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/book.html")
        self.assertIn("form", response.context)

    def test_book_view_get_with_query_params(self):
        """Test book view GET with query parameters."""
        url = reverse("book") + f"?worker={self.worker.id}&date={self.future_date}&time={self.future_time}&service={self.service.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        # Form values are strings, so compare as strings
        self.assertEqual(str(form["worker"].value()), str(self.worker.id))
        self.assertEqual(str(form["service"].value()), str(self.service.id))
        self.assertEqual(form["date"].value(), str(self.future_date))
        self.assertEqual(form["time"].value(), str(self.future_time))

    def test_book_view_post_valid(self):
        """Test book view POST with valid data."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
            "email": "customer@example.com",
        }
        response = self.client.post(reverse("book"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.url.startswith(reverse("booking_success")))
        
        # Check booking was created
        booking = Booking.objects.get(worker=self.worker, date=self.future_date, time=self.future_time)
        self.assertEqual(booking.email, "customer@example.com")
        self.assertEqual(booking.phone, "+1234567890")

    def test_book_view_post_invalid(self):
        """Test book view POST with invalid data."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": date.today() - timedelta(days=1),  # Past date
            "time": self.future_time,
            "phone": "+1234567890",
        }
        response = self.client.post(reverse("book"), data=form_data)
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertTemplateUsed(response, "bookings/book.html")
        self.assertFalse(response.context["form"].is_valid())

    def test_book_view_post_conflict(self):
        """Test book view POST with conflicting booking."""
        # Create existing booking
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=time(14, 0),
            phone="+1234567890",
        )
        # Try to create conflicting booking
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": time(14, 15),  # Overlaps
            "phone": "+9876543210",
        }
        response = self.client.post(reverse("book"), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

    @patch("bookings.views.EmailMultiAlternatives.send")
    def test_book_view_post_sends_email(self, mock_send):
        """Test that booking confirmation email is sent."""
        mock_send.return_value = 1
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
            "email": "customer@example.com",
        }
        response = self.client.post(reverse("book"), data=form_data)
        self.assertEqual(response.status_code, 302)
        mock_send.assert_called_once()

    def test_book_view_post_no_email(self):
        """Test booking without email doesn't send email."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
        }
        with patch("bookings.views.EmailMultiAlternatives.send") as mock_send:
            response = self.client.post(reverse("book"), data=form_data)
            self.assertEqual(response.status_code, 302)
            mock_send.assert_not_called()

    def test_book_view_post_email_failure(self):
        """Test that email failure doesn't prevent booking."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
            "email": "customer@example.com",
        }
        with patch("bookings.views.EmailMultiAlternatives.send", side_effect=Exception("Email error")):
            response = self.client.post(reverse("book"), data=form_data)
            self.assertEqual(response.status_code, 302)  # Still redirects
            # Booking should still be created
            self.assertTrue(Booking.objects.filter(worker=self.worker, date=self.future_date).exists())

    def test_book_view_success_message(self):
        """Test that success message is displayed."""
        form_data = {
            "worker": self.worker.id,
            "service": self.service.id,
            "date": self.future_date,
            "time": self.future_time,
            "phone": "+1234567890",
        }
        response = self.client.post(reverse("book"), data=form_data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("confirmed" in str(m.message).lower() for m in messages))


class BookingSuccessViewTest(TestCase):
    """Test cases for booking_success view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()

    def test_booking_success_view(self):
        """Test booking success view."""
        response = self.client.get(reverse("booking_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/success.html")

    def test_booking_success_view_with_id(self):
        """Test booking success view with booking ID."""
        url = reverse("booking_success") + "?id=123"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/success.html")


class PricelistViewTest(TestCase):
    """Test cases for pricelist view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
        )
        self.inactive_worker = Worker.objects.create(
            full_name="Inactive Worker",
            is_active=False,
        )
        self.service = Service.objects.create(name="Haircut")
        self.price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=30,
        )

    def test_pricelist_view(self):
        """Test pricelist view."""
        response = self.client.get(reverse("pricelist"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/pricelist.html")

    def test_pricelist_view_only_active_workers(self):
        """Test that only active workers are shown."""
        response = self.client.get(reverse("pricelist"))
        workers = response.context["workers"]
        self.assertIn(self.worker, workers)
        self.assertNotIn(self.inactive_worker, workers)

    def test_pricelist_view_services(self):
        """Test that services are included in context."""
        response = self.client.get(reverse("pricelist"))
        services = response.context["services"]
        self.assertIn(self.service, services)


class CalendarViewTest(TestCase):
    """Test cases for calendar_view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
            working_hours_start=time(9, 0),
            working_hours_end=time(18, 0),
        )
        self.service = Service.objects.create(
            name="Haircut",
            duration_minutes=30,
        )
        self.price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=45,
        )

    def test_calendar_view_no_params(self):
        """Test calendar view without parameters."""
        response = self.client.get(reverse("calendar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/calendar.html")

    def test_calendar_view_with_worker(self):
        """Test calendar view with worker parameter."""
        url = reverse("calendar") + f"?worker={self.worker.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["worker"], self.worker)

    def test_calendar_view_with_worker_and_service(self):
        """Test calendar view with worker and service."""
        url = reverse("calendar") + f"?worker={self.worker.id}&service={self.service.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["worker"], self.worker)
        self.assertEqual(response.context["selected_service"], self.service)

    def test_calendar_view_with_date(self):
        """Test calendar view with selected date."""
        test_date = date.today() + timedelta(days=5)
        url = reverse("calendar") + f"?worker={self.worker.id}&service={self.service.id}&date={test_date}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_date"], test_date)

    def test_calendar_view_with_month(self):
        """Test calendar view with month parameter."""
        test_month = "2024-06"
        url = reverse("calendar") + f"?worker={self.worker.id}&month={test_month}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["month_start"], date(2024, 6, 1))

    def test_calendar_view_invalid_worker(self):
        """Test calendar view with invalid worker ID."""
        url = reverse("calendar") + "?worker=99999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_calendar_view_availability_calculation(self):
        """Test that calendar calculates availability correctly."""
        # Create a booking
        booking_date = date.today() + timedelta(days=3)
        Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=booking_date,
            time=time(10, 0),
            phone="+1234567890",
        )
        url = reverse("calendar") + f"?worker={self.worker.id}&service={self.service.id}&date={booking_date}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that slots are calculated
        self.assertIn("selected_slots", response.context)

    def test_calendar_view_past_dates(self):
        """Test that past dates are marked correctly."""
        past_date = date.today() - timedelta(days=1)
        url = reverse("calendar") + f"?worker={self.worker.id}&service={self.service.id}&month={past_date.strftime('%Y-%m')}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that past dates have "past" status
        calendar_days = response.context["calendar_days"]
        for week in calendar_days:
            for day_info in week:
                if day_info["date"] < date.today():
                    self.assertEqual(day_info["status"], "past")


class WorkerDetailViewTest(TestCase):
    """Test cases for worker_detail view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.worker = Worker.objects.create(
            full_name="John Doe",
            is_active=True,
        )
        self.inactive_worker = Worker.objects.create(
            full_name="Inactive Worker",
            is_active=False,
        )
        self.service = Service.objects.create(name="Haircut")
        self.price = WorkerServicePrice.objects.create(
            worker=self.worker,
            service=self.service,
            price=50.00,
            duration_minutes=30,
        )

    def test_worker_detail_view(self):
        """Test worker detail view."""
        url = reverse("worker_detail", args=[self.worker.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/worker_detail.html")
        self.assertEqual(response.context["worker"], self.worker)

    def test_worker_detail_view_inactive_worker(self):
        """Test that inactive workers return 404."""
        url = reverse("worker_detail", args=[self.inactive_worker.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_worker_detail_view_invalid_id(self):
        """Test worker detail view with invalid ID."""
        url = reverse("worker_detail", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_worker_detail_view_prices(self):
        """Test that worker prices are included in context."""
        url = reverse("worker_detail", args=[self.worker.id])
        response = self.client.get(url)
        prices = response.context["prices"]
        self.assertIn(self.price, prices)

    def test_worker_detail_view_today(self):
        """Test that today's date is included in context."""
        url = reverse("worker_detail", args=[self.worker.id])
        response = self.client.get(url)
        self.assertIn("today", response.context)
        self.assertEqual(response.context["today"], timezone.localdate())


class CancelBookingViewTest(TestCase):
    """Tests for token-based cancellation flow."""

    def setUp(self):
        self.worker = Worker.objects.create(full_name="John Doe", is_active=True)
        self.service = Service.objects.create(name="Haircut", duration_minutes=30)
        self.future_date = timezone.localdate() + timedelta(days=1)
        self.future_time = time(14, 0)

    def test_cancel_booking_post_without_csrf_succeeds(self):
        """Cancel should work even if the client/browser doesn't support cookies/CSRF."""
        booking = Booking.objects.create(
            worker=self.worker,
            service=self.service,
            date=self.future_date,
            time=self.future_time,
            phone="+1234567890",
            email="customer@example.com",
        )
        token = booking.get_cancellation_token()
        url = reverse("cancel_booking", args=[token])

        # Enforce CSRF checks to prove the view is CSRF-exempt
        client = Client(enforce_csrf_checks=True)

        # GET should render confirmation page
        resp_get = client.get(url)
        self.assertEqual(resp_get.status_code, 200)

        # POST without CSRF token should still succeed and delete booking
        resp_post = client.post(url, data={})
        self.assertEqual(resp_post.status_code, 302)
        self.assertFalse(Booking.objects.filter(id=booking.id).exists())

