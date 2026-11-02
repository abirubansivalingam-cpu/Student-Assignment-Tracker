from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Assignment, StudentProfile

User = get_user_model()

class AssignmentTrackerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student1", password="StrongPass123!")
        self.other = User.objects.create_user(username="student2", password="StrongPass123!")
        self.client.login(username="student1", password="StrongPass123!")

    def make_assignment(self, **kwargs):
        values = {"student": self.user, "title": "Data Structures", "subject": "Computer Science",
                  "due_date": timezone.localdate() + timedelta(days=3), "priority": "Medium"}
        values.update(kwargs)
        return Assignment.objects.create(**values)

    def test_01_register_creates_account(self):
        self.client.logout()
        response = self.client.post(reverse("register"), {
            "username": "newstudent", "first_name": "New", "last_name": "Student",
            "email": "new@example.com", "password1": "AnotherStrong123!", "password2": "AnotherStrong123!"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newstudent").exists())

    def test_02_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_03_empty_dashboard_counts_are_zero(self):
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_assignments"], 0)
        self.assertEqual(response.context["completion_percentage"], 0)

    def test_04_create_assignment(self):
        response = self.client.post(reverse("assignments:assignment_create"), {
            "title": "Networks Lab", "subject": "Networking", "description": "Prepare lab record",
            "due_date": (timezone.localdate() + timedelta(days=2)).isoformat(), "priority": "High"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Assignment.objects.filter(student=self.user, title="Networks Lab").exists())

    def test_05_assignment_list_is_scoped_to_logged_in_user(self):
        mine = self.make_assignment(title="Mine")
        Assignment.objects.create(student=self.other, title="Other user's work", subject="Math",
                                  due_date=timezone.localdate() + timedelta(days=2))
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Other user's work")

    def test_06_update_assignment(self):
        item = self.make_assignment()
        response = self.client.post(reverse("assignments:assignment_update", args=[item.pk]), {
            "title": "Updated title", "subject": "Algorithms", "description": "Updated",
            "due_date": (timezone.localdate() + timedelta(days=5)).isoformat(), "priority": "Low"
        })
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.title, "Updated title")
        self.assertEqual(item.priority, "Low")

    def test_07_toggle_completion(self):
        item = self.make_assignment()
        response = self.client.post(reverse("assignments:assignment_toggle_complete", args=[item.pk]))
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertTrue(item.is_completed)

    def test_08_delete_assignment(self):
        item = self.make_assignment()
        response = self.client.post(reverse("assignments:assignment_delete", args=[item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Assignment.objects.filter(pk=item.pk).exists())

    def test_09_owner_cannot_edit_another_students_assignment(self):
        item = self.make_assignment(student=self.other)
        response = self.client.get(reverse("assignments:assignment_update", args=[item.pk]))
        self.assertEqual(response.status_code, 404)

    def test_10_owner_cannot_delete_another_students_assignment(self):
        item = self.make_assignment(student=self.other)
        response = self.client.post(reverse("assignments:assignment_delete", args=[item.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Assignment.objects.filter(pk=item.pk).exists())

    def test_11_dashboard_status_counts(self):
        self.make_assignment(title="Done", is_completed=True)
        self.make_assignment(title="Pending")
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.context["total_assignments"], 2)
        self.assertEqual(response.context["completed_assignments"], 1)
        self.assertEqual(response.context["pending_assignments"], 1)
        self.assertEqual(response.context["completion_percentage"], 50)

    def test_12_deadlines_this_week_count(self):
        self.make_assignment(title="Soon", due_date=timezone.localdate() + timedelta(days=7))
        self.make_assignment(title="Later", due_date=timezone.localdate() + timedelta(days=8))
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.context["deadlines_this_week"], 1)

    def test_13_overdue_count(self):
        self.make_assignment(title="Late", due_date=timezone.localdate() - timedelta(days=1))
        self.make_assignment(title="Done late", due_date=timezone.localdate() - timedelta(days=2), is_completed=True)
        response = self.client.get(reverse("assignments:assignment_list"))
        self.assertEqual(response.context["overdue_assignments"], 1)

    def test_14_profile_page_creates_profile(self):
        response = self.client.get(reverse("assignments:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(StudentProfile.objects.filter(user=self.user).exists())

    def test_15_profile_update(self):
        response = self.client.post(reverse("assignments:profile"), {
            "institution": "Example College", "course": "MCA", "bio": "Student profile"
        })
        self.assertEqual(response.status_code, 302)
        profile = StudentProfile.objects.get(user=self.user)
        self.assertEqual(profile.course, "MCA")

    def test_16_csv_export_contains_only_current_user_records(self):
        self.make_assignment(title="My CSV task")
        self.make_assignment(student=self.other, title="Private other task")
        response = self.client.get(reverse("assignments:export_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertContains(response, "My CSV task")
        self.assertNotContains(response, "Private other task")

    def test_17_pdf_export_returns_pdf(self):
        self.make_assignment(title="PDF task")
        response = self.client.get(reverse("assignments:export_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
