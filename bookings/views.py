from __future__ import annotations

import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import BookingForm
from .models import Worker, WorkerServicePrice, Service, Booking


logger = logging.getLogger(__name__)


def home(request):
    workers = Worker.objects.filter(is_active=True)
    return render(request, "bookings/home.html", {"workers": workers})


def book(request):
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
                subject = "Your salon booking is confirmed"
                body = f"Thank you! Your booking with {booking.worker.full_name} is on {booking.date} at {booking.time}."
                try:
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [booking.email], fail_silently=True)
                except Exception:
                    logger.exception(
                        "Failed to send booking confirmation email",
                        extra={"booking_id": booking.id, "email": booking.email},
                    )
            messages.success(request, "Your booking is confirmed.")
            return redirect(reverse("booking_success") + f"?id={booking.id}")
        else:
            logger.warning("Booking form invalid", extra={"errors": form.errors})
    else:
        # Prefill from query parameters if provided
        initial = {}
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

    return render(request, "bookings/book.html", {"form": form})


def booking_success(request):
    return render(request, "bookings/success.html")


def pricelist(request):
    workers = Worker.objects.filter(is_active=True).prefetch_related("service_prices__service")
    services = Service.objects.all()
    return render(request, "bookings/pricelist.html", {"workers": workers, "services": services})


def calendar_view(request):
    """Show available time slots for booking."""
    from datetime import datetime, timedelta, time
    from django.utils import timezone
    import json
    
    # Get selected date and worker from request
    selected_date = request.GET.get('date')
    selected_worker_id = request.GET.get('worker')
    
    if selected_date and selected_worker_id:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            today = timezone.localdate()
            # Do not allow viewing schedules for past dates
            if selected_date < today:
                selected_date = today
            worker = Worker.objects.get(id=selected_worker_id, is_active=True)
            
            # Generate time slots (9 AM to 6 PM, 30-minute intervals)
            time_slots = []
            start_time = time(9, 0)  # 9:00 AM
            end_time = time(18, 0)   # 6:00 PM
            
            current_time = start_time
            while current_time < end_time:
                time_slots.append(current_time)
                # Add 30 minutes
                current_time = (datetime.combine(selected_date, current_time) + timedelta(minutes=30)).time()
            
            # Get existing bookings for this worker on this date
            existing_bookings = Booking.objects.filter(worker=worker, date=selected_date)
            
            # Check availability for each time slot
            available_slots = []
            for slot_time in time_slots:
                is_available = True
                for booking in existing_bookings:
                    # Skip bookings without a service (legacy data)
                    if booking.service is None:
                        # For legacy bookings without service, assume 60 minutes duration
                        from datetime import datetime, timedelta
                        booking_start = datetime.combine(booking.date, booking.time)
                        booking_end = booking_start + timedelta(minutes=60)
                        slot_start = datetime.combine(selected_date, slot_time)
                        slot_end = slot_start + timedelta(minutes=60)  # Default 60 minutes for new booking
                        
                        if (slot_start < booking_end and slot_end > booking_start):
                            is_available = False
                            break
                    else:
                        if Booking.has_conflict(worker, selected_date, slot_time, booking.service):
                            is_available = False
                            break
                
                available_slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'available': is_available
                })
            
            return render(request, "bookings/calendar.html", {
                'worker': worker,
                'selected_date': selected_date,
                'time_slots': available_slots,
                'workers': Worker.objects.filter(is_active=True),
                'services': Service.objects.all(),
                'today': today,
            })
            
        except (ValueError, Worker.DoesNotExist):
            logger.warning(
                "Invalid calendar parameters",
                exc_info=True,
                extra={"date": request.GET.get("date"), "worker": request.GET.get("worker")},
            )
    
    # Default view - show worker and date selection
    workers = Worker.objects.filter(is_active=True)
    from django.utils import timezone as _tz
    return render(request, "bookings/calendar.html", {
        'workers': workers,
        'services': Service.objects.all(),
        'today': _tz.localdate(),
    })


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



