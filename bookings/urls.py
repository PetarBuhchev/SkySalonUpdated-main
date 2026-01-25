from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("book/", views.book, name="book"),
    path("booking-success/", views.booking_success, name="booking_success"),
    path("pricelist/", views.pricelist, name="pricelist"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("workers/<int:worker_id>/", views.worker_detail, name="worker_detail"),
    path("cancel/<str:token>/", views.cancel_booking, name="cancel_booking"),
]



