from django.urls import path

from . import views

"""
This module defines URL routing configurations for the accounts application.
It uses standard Django path mapping to route incoming HTTP requests to their matching view logic.

The routes are organized into three logical segments:
1. Authentication (Login, Logout)
2. User Management actions (Creating, editing, deleting, role updating for PM users)
3. Self-service profile, settings, and password updates
"""

# Namespace name for routing reverse lookups (e.g. reverse("accounts:login"))
app_name = "accounts"

urlpatterns = [
    # ─── Authentication Routes ──────────────────────────────────────────────────
    # Default system login page
    path("login/", views.login_view, name="login"),
    
    # Global logout route
    path("logout/", views.logout_view, name="logout"),
    
    # ─── User Management (Admin only) ──────────────────────────────────────────
    # Lists Project Management users
    path("users/", views.user_list, name="user_list"),
    
    # Create a new PM user
    path("users/create/", views.user_create, name="user_create"),
    
    # View details of a specific user profile
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    
    # Edit details of a specific user
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    
    # Admin tool to override/reset a user's password
    path(
        "users/<int:pk>/reset-password/",
        views.user_reset_password,
        name="user_reset_password",
    ),
    
    # Delete a user account (destructive confirmation action)
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    
    # Toggle user active status (Active/Inactive toggle)
    path("users/<int:pk>/toggle/", views.user_toggle_active, name="user_toggle"),
    
    # API endpoint to change user's role via POST requests
    path(
        "users/<int:pk>/change-role/", views.change_user_role, name="user_change_role"
    ),
    
    # ─── Profile & Self-Service Settings ───────────────────────────────────────
    # Profile viewing dashboard (Self)
    path("profile/", views.profile_view, name="profile"),
    
    # Password changing form (Self)
    path("change-password/", views.change_password, name="change_password"),
    
    # General app theme preferences, notifications toggle, issue reporting configurations (Self)
    path("settings/", views.settings_view, name="settings"),
]
