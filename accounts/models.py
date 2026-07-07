from django.contrib.auth.models import AbstractUser
from django.db import models

"""
This module defines the database models for the user accounts system.
It utilizes Django's built-in authentication system but extends it to support
custom fields, roles, team modules, and user properties for the Project Management system.
"""

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    By subclassing AbstractUser, we inherit standard fields like:
    - username, first_name, last_name, email, password
    - is_staff, is_active, is_superuser, last_login, date_joined
    
    We extend this model to add specific business logic properties, roles,
    teams, custom settings (like themes and email notifications), and granular 
    permissions for the IIA Observatory Management workspace (Project Management).
    """

    # Role choices defining the type of user in the Project Management space.
    # The first value in the tuple is what's saved in the DB, and the second is the human-readable label.
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("project_manager", "Project Manager"),
        ("member", "Member"),
        ("student", "Student"),
    ]

    # Module choices representing the scientific/engineering teams under IIA.
    MODULE_CHOICES = [
        ("electronics", "Electronics"),
        ("mechanical", "Mechanical"),
        ("optics", "Optics"),
        ("simulation", "Simulation"),
        ("software", "Software"),
        ("general", "General"),
    ]

    # User Profile Fields
    # role: Controls high-level capabilities in Project Management.
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default="member",
        help_text="Defines user level permissions within Project Management."
    )
    
    # team: Identifies the technical/scientific group the user belongs to.
    team = models.CharField(
        max_length=20, 
        choices=MODULE_CHOICES, 
        default="general",
        help_text="Specifies the functional module or department team."
    )
    
    # avatar_color: Hex color code used for generating a initials-based avatar when no profile picture is set.
    avatar_color = models.CharField(
        max_length=7, 
        default="#6366f1",
        help_text="Hex code of the color theme representing the user avatar."
    )
    
    # profile_picture: Image file upload field. Uses Django's ImageField and uploads images to 'media/avatars/'.
    profile_picture = models.ImageField(
        upload_to="avatars/", 
        null=True, 
        blank=True,
        help_text="Optional profile picture image file."
    )
    
    # nickname: An optional display name chosen by the user.
    nickname = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Optional nickname or display moniker."
    )
    
    # designation: Professional job title (e.g., 'Senior Scientist', 'Project Engineer').
    designation = models.CharField(
        max_length=100, 
        blank=True,
        help_text="User's professional title/designation."
    )
    
    # phone: Primary contact number.
    phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Contact telephone/mobile number."
    )
    
    # is_active: A flag to activate/deactivate accounts instead of deleting them (a Django best practice).
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user account is active. Deselect instead of deleting."
    )
    
    # theme_preference: Preference for dashboard colors, defaults to 'light'.
    theme_preference = models.CharField(
        max_length=20, 
        default="light",
        help_text="Dashboard UI theme preference (e.g., light, dark, night)."
    )
    
    # email_notifications: User preference to subscribe/unsubscribe to automated system email updates.
    email_notifications = models.BooleanField(
        default=True,
        help_text="Toggle to receive email updates and alerts from the system."
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Datetime when the user profile was originally created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Datetime when the user profile was last updated."
    )

    # App Access Flags
    can_access_pm = models.BooleanField(
        default=True,
        help_text="Allows access to the Project Management System."
    )

    class Meta:
        """
        Meta options for the User model.
        Defines human-readable names and default sorting behaviour.
        """
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]  # Newest users appear first by default

    def __str__(self):
        """
        String representation of a User instance.
        Used when rendering the user object in admin forms, dropdown lists, or templates.
        """
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # Helper properties for easy permission checks in views and template tags
    @property
    def is_admin(self):
        """Checks if the user has the 'admin' role or is a Django superuser."""
        return self.role == "admin" or self.is_superuser

    @property
    def is_project_manager(self):
        """Checks if the user role is 'project_manager'."""
        return self.role == "project_manager"

    @property
    def is_student(self):
        """Checks if the user role is 'student'."""
        return self.role == "student"

    @property
    def is_super_admin(self):
        """Checks if the user is a super administrator."""
        return self.role == "admin" or self.is_superuser


    @property
    def display_name(self):
        """
        Determines the best name to display.
        Uses nickname if present; otherwise full name; otherwise falls back to username.
        """
        if self.nickname:
            return self.nickname
        return self.get_full_name() or self.username

    @property
    def initials(self):
        """
        Generates 2-character uppercase initials from the user's name.
        Used for placeholder avatars. (e.g. 'John Doe' -> 'JD', 'operator' -> 'OP').
        """
        name = self.get_full_name()
        if name:
            parts = name.split()
            return "".join(p[0].upper() for p in parts[:2])
        return self.username[:2].upper()
