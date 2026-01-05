from django.contrib import admin
from .models import Worker, Booking, Service, WorkerServicePrice


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "is_active")
    list_filter = ("is_active",)
    search_fields = ("full_name", "role")
    fieldsets = (
        (None, {"fields": ("full_name", "role", "is_active")}),
        ("Profile", {"fields": ("photo", "bio")}),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("worker", "service", "date", "time", "phone", "email", "created_at")
    list_filter = ("worker", "service", "date")
    search_fields = ("phone", "worker__full_name", "service__name")
    autocomplete_fields = ("worker", "service")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes")
    search_fields = ("name",)


@admin.register(WorkerServicePrice)
class WorkerServicePriceAdmin(admin.ModelAdmin):
    list_display = ("worker", "service", "price", "duration_minutes")
    list_filter = ("worker", "service")
    search_fields = ("worker__full_name", "service__name")
    autocomplete_fields = ("worker", "service")



