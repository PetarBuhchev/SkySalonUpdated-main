from __future__ import annotations

import logging

from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string

from datetime import datetime, timedelta, date as date_cls, time as time_cls
import calendar

from .forms import BookingForm
from .models import Worker, WorkerServicePrice, Service, Booking


logger = logging.getLogger(__name__)


def home(request):
    workers = Worker.objects.filter(is_active=True)
    return render(request, "bookings/home.html", {"workers": workers})


def book(request):
    if request.method == "GET":
        logger.info(
            "Booking page viewed",
            extra={
                "path": request.get_full_path(),
                "method": request.method,
                "user": getattr(request.user, "id", None),
            },
        )

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            logger.info(
                "Booking created",
                extra={
                    "booking_id": booking.id,
                    "worker_id": booking.worker_id,
                    "service_id": booking.service_id,
                    "date": str(booking.date),
                    "time": booking.time.isoformat(),
                },
            )
            # Send confirmation email if provided
            if booking.email:
                logger.info(
                    "Sending booking confirmation email",
                    extra={
                        "booking_id": booking.id,
                        "email": booking.email,
                    },
                )
                subject = "Your salon booking is confirmed"
                
                # Generate cancellation token
                cancellation_token = booking.get_cancellation_token()
                cancellation_url = request.build_absolute_uri(
                    reverse("cancel_booking", args=[cancellation_token])
                )
                
                # Prepare email context
                email_context = {
                    "booking": booking,
                    "worker": booking.worker,
                    "service": booking.service,
                    "date": booking.date,
                    "time": booking.time,
                    "cancellation_url": cancellation_url,
                }
                
                # Render plain text version
                text_content = render_to_string("bookings/emails/booking_confirmation.txt", email_context)
                
                # Render HTML version
                html_content = render_to_string("bookings/emails/booking_confirmation.html", email_context)
                
                # Create email message
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.email],
                )
                msg.attach_alternative(html_content, "text/html")
                
                try:
                    msg.send(fail_silently=True)
                except Exception:
                    logger.exception(
                        "Failed to send booking confirmation email",
                        extra={"booking_id": booking.id, "email": booking.email},
                    )
            messages.success(request, "Your booking is confirmed.")
            logger.info(
                "Booking process completed successfully",
                extra={
                    "booking_id": booking.id,
                    "redirect_to": reverse("booking_success"),
                },
            )
            return redirect(reverse("booking_success") + f"?id={booking.id}")
        else:
            logger.warning(
                "Booking form invalid",
                extra={
                    "errors": form.errors,
                    "path": request.get_full_path(),
                },
            )
    else:
        # Prefill from query parameters if provided
        initial: dict[str, object] = {}
        worker_id = request.GET.get("worker")
        date_param = request.GET.get("date")
        time_param = request.GET.get("time")
        service_id = request.GET.get("service")
        if worker_id:
            initial["worker"] = worker_id
        if service_id:
            initial["service"] = service_id
        if date_param:
            initial["date"] = date_param
        if time_param:
            initial["time"] = time_param
        form = BookingForm(initial=initial)

    # Derive selected worker/service/date/time for summary display
    selected_worker = None
    selected_service = None
    selected_date = None
    selected_time = None
    calendar_month = None

    try:
        worker_value = form["worker"].value()
        if worker_value:
            selected_worker = Worker.objects.filter(id=worker_value).first()
        service_value = form["service"].value()
        if service_value:
            selected_service = Service.objects.filter(id=service_value).first()
        date_value = form["date"].value()
        if date_value:
            selected_date = datetime.fromisoformat(date_value).date()
        time_value = form["time"].value()
        if time_value:
            # time input is HH:MM[:ss]
            selected_time = datetime.fromisoformat(f"2000-01-01T{time_value}").time()
        if selected_date:
            calendar_month = selected_date.replace(day=1).strftime("%Y-%m")
    except Exception:
        # If anything goes wrong with parsing, just skip the summary
        selected_worker = None
        selected_service = None
        selected_date = None
        selected_time = None
        calendar_month = None

    return render(
        request,
        "bookings/book.html",
        {
            "form": form,
            "selected_worker": selected_worker,
            "selected_service": selected_service,
            "selected_date": selected_date,
            "selected_time": selected_time,
            "calendar_month": calendar_month,
        },
    )


def booking_success(request):
    booking_id = request.GET.get("id")
    logger.info(
        "Booking success page viewed",
        extra={
            "booking_id": booking_id,
            "path": request.get_full_path(),
        },
    )
    return render(request, "bookings/success.html")


def pricelist(request):
    workers = Worker.objects.filter(is_active=True).prefetch_related("service_prices__service")
    services = Service.objects.all()
    return render(request, "bookings/pricelist.html", {"workers": workers, "services": services})


def calendar_view(request):
    """Month view calendar with worker/service availability coloring."""
    today = timezone.localdate()
    workers = Worker.objects.filter(is_active=True)

    worker_id = request.GET.get("worker")
    service_id = request.GET.get("service")
    selected_date_str = request.GET.get("date")
    month_param = request.GET.get("month")

    worker = None
    selected_service = None
    service_options = Service.objects.none()

    if worker_id:
        worker = get_object_or_404(workers, id=worker_id)
        logger.info(
            "Calendar viewed for worker",
            extra={
                "worker_id": worker.id,
                "service_id": service_id,
                "selected_date": selected_date_str,
                "month_param": month_param,
            },
        )
        # Only services the worker offers (fall back to all if none configured)
        worker_prices = WorkerServicePrice.objects.filter(worker=worker).select_related("service")
        service_options = [wp.service for wp in worker_prices] or list(Service.objects.all())
        if service_id:
            try:
                selected_service = next((svc for svc in service_options if str(svc.id) == service_id), None)
            except StopIteration:
                selected_service = None

    # Resolve month
    if month_param:
        try:
            year, month = month_param.split("-")
            year = int(year)
            month = int(month)
            month_start = date_cls(year, month, 1)
        except Exception:
            month_start = today.replace(day=1)
    else:
        month_start = today.replace(day=1)

    # Build weeks for display
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdatescalendar(month_start.year, month_start.month)

    service_duration = None
    if worker and selected_service:
        service_duration = Booking._duration_for_worker_service(worker, selected_service)

    # Preload bookings for the month for the selected worker
    bookings_by_date = {}
    if worker:
        month_end_day = calendar.monthrange(month_start.year, month_start.month)[1]
        month_end = date_cls(month_start.year, month_start.month, month_end_day)
        qs = (
            Booking.objects.filter(worker=worker, date__gte=month_start, date__lte=month_end)
            .select_related("service")
            .order_by("time")
        )
        for booking in qs:
            bookings_by_date.setdefault(booking.date, []).append(booking)

    def _working_hours():
        start = worker.working_hours_start if worker else time_cls(9, 0)
        end = worker.working_hours_end if worker else time_cls(18, 0)
        return start, end

    def _slots_for_day(day: date_cls, duration: int):
        """Return all potential start times for a day with 15-min granularity and availability flag."""
        start_time, end_time = _working_hours()
        start_dt = datetime.combine(day, start_time)
        end_dt = datetime.combine(day, end_time)
        if end_dt <= start_dt:
            return []

        last_start = end_dt - timedelta(minutes=duration)
        if last_start < start_dt:
            return []

        local_now = timezone.localtime().replace(tzinfo=None)
        slots: list[dict[str, object]] = []
        slot = start_dt
        day_bookings = bookings_by_date.get(day, [])

        while slot <= last_start:
            candidate_end = slot + timedelta(minutes=duration)
            # Skip past times for current day
            if slot.date() == local_now.date() and candidate_end <= local_now:
                slot += timedelta(minutes=15)
                continue

            conflict = False
            for booking in day_bookings:
                existing_start = datetime.combine(day, booking.time)
                existing_duration = Booking._duration_for_worker_service(worker, booking.service)
                existing_end = existing_start + timedelta(minutes=existing_duration)
                if slot < existing_end and candidate_end > existing_start:
                    conflict = True
                    break

            slots.append(
                {
                    "time": slot.time().strftime("%H:%M"),
                    "available": not conflict,
                }
            )
            slot += timedelta(minutes=15)

        return slots

    # Build availability for each day in the month grid
    calendar_days = []
    for week in month_weeks:
        week_days = []
        for day in week:
            in_month = day.month == month_start.month
            status = "past"
            if day < today:
                status = "past"
            elif worker and selected_service and in_month:
                day_slots = _slots_for_day(day, service_duration)
                has_slots = any(s["available"] for s in day_slots)
                status = "available" if has_slots else "full"
            else:
                status = "idle"

            week_days.append(
                {
                    "date": day,
                    "in_month": in_month,
                    "status": status,
                    "is_today": day == today,
                }
            )
        calendar_days.append(week_days)

    # Selected date slots (optional detail below calendar)
    selected_date = None
    selected_slots: list[dict[str, object]] = []
    if selected_date_str and worker and selected_service:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            selected_slots = _slots_for_day(selected_date, service_duration)
            logger.info(
                "Calendar slots calculated",
                extra={
                    "worker_id": worker.id,
                    "service_id": selected_service.id,
                    "selected_date": str(selected_date),
                    "available_slots_count": len([s for s in selected_slots if s["available"]]),
                },
            )
        except ValueError:
            selected_date = None

    # Determine prev/next month params
    prev_month = (month_start.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)

    return render(
        request,
        "bookings/calendar.html",
        {
            "workers": workers,
            "worker": worker,
            "services": service_options,
            "selected_service": selected_service,
            "calendar_days": calendar_days,
            "month_start": month_start,
            "today": today,
            "selected_date": selected_date,
            "selected_slots": selected_slots,
            "prev_month": prev_month,
            "next_month": next_month,
        },
    )


def worker_detail(request, worker_id: int):
    worker = get_object_or_404(Worker.objects.filter(is_active=True), id=worker_id)
    # Prefetch prices and related services for display
    prices = WorkerServicePrice.objects.filter(worker=worker).select_related("service")
    from django.utils import timezone
    return render(request, "bookings/worker_detail.html", {
        'worker': worker,
        'prices': prices,
        'today': timezone.localdate(),
    })


def cancel_booking(request, token: str):
    """Cancel a booking using a secure token."""
    booking = Booking.from_cancellation_token(token)
    
    if not booking:
        logger.warning(
            "Invalid cancellation token attempted",
            extra={"token": token[:20] + "..." if len(token) > 20 else token},
        )
        messages.error(request, "Invalid cancellation link. Please contact us if you need to cancel your booking.")
        return redirect(reverse("home"))
    
    # Check if booking is in the past
    booking_datetime = timezone.make_aware(datetime.combine(booking.date, booking.time))
    if booking_datetime < timezone.now():
        messages.error(request, "This booking is in the past and cannot be cancelled.")
        return redirect(reverse("home"))
    
    if request.method == "POST":
        # Save booking details before deletion
        booking_details = {
            "booking_id": booking.id,
            "worker": booking.worker.full_name,
            "date": str(booking.date),
            "time": booking.time.isoformat(),
            "email": booking.email,
        }
        
        # Delete the booking
        booking.delete()
        
        logger.info(
            "Booking cancelled",
            extra=booking_details,
        )
        
        # Send cancellation confirmation email if email was provided
        if booking_details["email"]:
            try:
                subject = "Your salon booking has been cancelled"
                text_content = f"Your booking with {booking_details['worker']} on {booking_details['date']} at {booking_details['time']} has been cancelled."
                html_content = f"""
                <html>
                <body>
                    <p>Your booking with {booking_details['worker']} on {booking_details['date']} at {booking_details['time']} has been cancelled.</p>
                    <p>If you have any questions, please contact us.</p>
                </body>
                </html>
                """
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking_details["email"]],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
            except Exception:
                logger.exception(
                    "Failed to send cancellation confirmation email",
                    extra={"email": booking_details["email"]},
                )
        
        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect(reverse("home"))
    
    # GET request - show confirmation page
    return render(request, "bookings/cancel_booking.html", {
        "booking": booking,
    })



