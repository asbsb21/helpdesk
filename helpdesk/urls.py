from django.urls import path

from . import views

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("tickets/new/", views.ticket_create, name="ticket_create"),
    path("tickets/<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("tickets/<int:pk>/manage/", views.ticket_manage, name="ticket_manage"),
    path("register/", views.register, name="register"),
]
