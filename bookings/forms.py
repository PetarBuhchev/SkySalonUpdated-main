from __future__ import annotations

from datetime import date, time
from django import forms
from django.utils import timezone
from .models import Booking, Worker, Service


class BookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time", "step": 900}))
    worker = forms.ModelChoiceField(queryset=Worker.objects.filter(is_active=True), empty_label="Select a worker")
    service = forms.ModelChoiceField(queryset=Service.objects.all(), required=True, help_text="", empty_label="Select a service")

    class Meta:
        model = Booking
        fields = ["worker", "service", "date", "time", "phone", "email"]

    def clean(self):
        cleaned = super().clean()
        selected_date: date | None = cleaned.get("date")
        selected_time: time | None = cleaned.get("time")
        selected_worker: Worker | None = cleaned.get("worker")
        selected_service: Service | None = cleaned.get("service")

        if selected_date and selected_time:
            dt = timezone.make_aware(timezone.datetime.combine(selected_date, selected_time))
            if dt < timezone.now():
                raise forms.ValidationError("Please choose a future date and time.")

        if selected_worker and selected_service and selected_date and selected_time:
            if Booking.has_conflict(selected_worker, selected_date, selected_time, selected_service):
                raise forms.ValidationError("This time slot conflicts with an existing appointment.")

        return cleaned



