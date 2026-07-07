from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import User

"""
This module defines Unit Tests for testing accounts application features.
Django's test framework uses Python's standard unittest module structure.
Running tests executes operations on a separate isolated temporary database,
guaranteeing that test actions don't affect live/production data.
"""


class UserFormFieldsTest(TestCase):
    """
    Test case to verify that System Access Permission fields
    are correctly excluded from standard User forms and default correctly.
    """

    def test_user_create_form_fields(self):
        from accounts.forms import UserCreateForm
        form = UserCreateForm()
        self.assertNotIn("can_access_pm", form.fields)

    def test_user_edit_form_fields(self):
        from accounts.forms import UserEditForm
        form = UserEditForm()
        self.assertNotIn("can_access_pm", form.fields)

    def test_user_creation_defaults(self):
        from accounts.forms import UserCreateForm
        data = {
            "username": "new_pm_user",
            "first_name": "PM",
            "last_name": "User",
            "email": "pm@example.com",
            "role": "member",
            "team": "software",
            "avatar_color": "#6366f1",
            "password1": "pass@1234",
            "password2": "pass@1234",
        }
        form = UserCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.can_access_pm)


class UserAdminTest(TestCase):
    """
    Test case to verify custom UserAdmin functionality (e.g. badges, querysets).
    """

    def test_badges(self):
        from django.contrib.admin.sites import AdminSite
        from accounts.admin import UserAdmin
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            role="admin",
            is_active=True,
            is_superuser=True
        )
        site = AdminSite()
        admin_instance = UserAdmin(User, site)
        
        # Test role_badge
        role_html = admin_instance.role_badge(user)
        self.assertIn("Admin", role_html)
        
        # Test status_badge
        status_html = admin_instance.status_badge(user)
        self.assertIn("Active", status_html)
        
        # Test is_superuser_badge
        superuser_html = admin_instance.is_superuser_badge(user)
        self.assertIn("Yes", superuser_html)
