from django.urls import path
from . import views

app_name = "assignments"
urlpatterns = [
    path("dashboard/", views.assignment_list, name="assignment_list"),
    path("assignments/add/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:pk>/edit/", views.assignment_update, name="assignment_update"),
    path("assignments/<int:pk>/toggle/", views.assignment_toggle_complete, name="assignment_toggle_complete"),
    path("assignments/<int:pk>/delete/", views.assignment_delete, name="assignment_delete"),
    path("exports/assignments.csv", views.export_assignments_csv, name="export_csv"),
    path("exports/assignments.pdf", views.export_assignments_pdf, name="export_pdf"),
    path("profile/", views.profile, name="profile"),
]
