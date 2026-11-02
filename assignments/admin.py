from django.contrib import admin
from .models import Assignment, StudentProfile

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "subject", "due_date", "priority", "is_completed")
    list_filter = ("priority", "is_completed", "due_date")
    search_fields = ("title", "subject", "student__username")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "course")
