from django.urls import path

from triage import views

urlpatterns = [
    path("triage/routes/", views.routes, name="triage-routes"),
    path("triage/", views.triage, name="triage"),
]
