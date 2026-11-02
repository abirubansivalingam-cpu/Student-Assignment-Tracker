import csv
from datetime import timedelta
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .forms import AssignmentForm, StudentProfileForm, StudentRegistrationForm
from .models import Assignment, StudentProfile


def home(request):
    return redirect("assignments:assignment_list") if request.user.is_authenticated else redirect("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("assignments:assignment_list")
    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        StudentProfile.objects.create(user=user)
        messages.success(request, "Your account was created. Welcome!")
        login(request, user)
        return redirect("assignments:assignment_list")
    return render(request, "registration/register.html", {"form": form})


@login_required
def assignment_list(request):
    today = timezone.localdate()
    all_assignments = Assignment.objects.filter(student=request.user).order_by("due_date")
    total_assignments = all_assignments.count()
    completed_assignments = all_assignments.filter(is_completed=True).count()
    pending_assignments = all_assignments.filter(is_completed=False).count()
    overdue_assignments = all_assignments.filter(is_completed=False, due_date__lt=today).count()
    deadlines_this_week = all_assignments.filter(
        is_completed=False, due_date__gte=today, due_date__lte=today + timedelta(days=7)
    ).count()
    completion_percentage = round(completed_assignments / total_assignments * 100) if total_assignments else 0
    return render(request, "assignments/assignment_list.html", {
        "assignments": all_assignments,
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "pending_assignments": pending_assignments,
        "overdue_assignments": overdue_assignments,
        "deadlines_this_week": deadlines_this_week,
        "completion_percentage": completion_percentage,
        "today": today,
    })


@login_required
def assignment_create(request):
    form = AssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.student = request.user
        assignment.save()
        messages.success(request, "Assignment added successfully.")
        return redirect("assignments:assignment_list")
    return render(request, "assignments/assignment_form.html", {"form": form, "page_title": "Add assignment"})


@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, student=request.user)
    form = AssignmentForm(request.POST or None, instance=assignment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Assignment updated successfully.")
        return redirect("assignments:assignment_list")
    return render(request, "assignments/assignment_form.html", {"form": form, "page_title": "Edit assignment"})


@login_required
@require_POST
def assignment_toggle_complete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, student=request.user)
    assignment.is_completed = not assignment.is_completed
    assignment.save(update_fields=["is_completed"])
    messages.success(request, "Assignment status updated.")
    return redirect("assignments:assignment_list")


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, student=request.user)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("assignments:assignment_list")
    return render(request, "assignments/assignment_delete.html", {"assignment": assignment})


@login_required
def profile(request):
    profile_obj, _ = StudentProfile.objects.get_or_create(user=request.user)
    form = StudentProfileForm(request.POST or None, instance=profile_obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("assignments:profile")
    return render(request, "assignments/profile.html", {"form": form})


@login_required
def export_assignments_csv(request):
    rows = Assignment.objects.filter(student=request.user).order_by("due_date")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="my_assignments.csv"'
    writer = csv.writer(response)
    writer.writerow(["Title", "Subject", "Due date", "Priority", "Status", "Description"])
    for item in rows:
        writer.writerow([item.title, item.subject, item.due_date, item.priority,
                         "Completed" if item.is_completed else "Pending", item.description])
    return response


@login_required
def export_assignments_pdf(request):
    rows = Assignment.objects.filter(student=request.user).order_by("due_date")
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=28, leftMargin=28, topMargin=28, bottomMargin=28)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Student Assignment Tracker", styles["Title"]),
                Paragraph(f"Assignment summary for {request.user.username}", styles["Normal"]), Spacer(1, 14)]
    data = [["Assignment", "Subject", "Due date", "Priority", "Status"]]
    for item in rows:
        data.append([item.title, item.subject, item.due_date.strftime("%d %b %Y"), item.priority,
                     "Completed" if item.is_completed else "Pending"])
    table = Table(data, repeatRows=1, colWidths=[220, 150, 100, 85, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#19324D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D8E0E8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="my_assignments.pdf"'
    return response
