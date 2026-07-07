from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

"""
This module handles user profile and settings views.
It includes:
1. Main Project Management Profile View with user task/project summaries.
2. Settings interface for updating self profile metadata, reporting system issues, 
   changing email preferences, and saving system configurations (admin only).
"""

@login_required
def profile_view(request):
    """
    Renders the logged-in user's Project Management profile page.
    Retrieves assigned tasks and related projects to show a quick dashboard summary.
    """
    from tasks.models import Project, Task

    u = request.user
    
    # Query tasks where the user is an assignee
    my_tasks = Task.objects.filter(assignees=u)
    
    # Query projects where the user is listed as either a manager or a member.
    # We use Q objects for complex OR queries, and .distinct() to avoid duplicate results.
    my_projects = Project.objects.filter(Q(managers=u) | Q(members=u)).distinct()
    
    # Calculate task status metrics
    task_stats = {
        "total": my_tasks.count(),
        "todo": my_tasks.filter(status="todo").count(),
        "in_progress": my_tasks.filter(status="in_progress").count(),
        "done": my_tasks.filter(status="done").count(),
        # Iterate over tasks and check the 'is_overdue' model property
        "overdue": sum(1 for t in my_tasks if t.is_overdue),
    }
    
    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": u,
            "my_tasks": my_tasks[:8],      # Slice to display only the top 8 tasks
            "my_projects": my_projects[:6],  # Slice to display only the top 6 projects
            "task_stats": task_stats,
        },
    )


@login_required
def settings_view(request):
    """
    Renders and handles the user settings panel.
    Supports multiple post action targets identified by the 'action' parameter.
    Actions:
    - update_profile: Edit basic fields (first_name, nickname, upload avatar, password update)
    - update_preferences: Change theme preferences and email notifications settings
    - report_issue: Save a new system bug/feedback ticket
    - update_system_settings: Modify global application parameters (Admin only)
    """
    from tasks.models import SystemIssue, SystemSettings
    from events.models import UserCalendarSettings

    # Ensure calendar settings model instance exists for the user
    UserCalendarSettings.objects.get_or_create(user=request.user)
    
    # Retrieve system settings singleton instance
    sys_settings = SystemSettings.get_settings()

    if request.method == "POST":
        action = request.POST.get("action")

        # ─── ACTION: Update Personal Profile ───
        if action == "update_profile":
            from accounts.models import User as UserModel
            user = request.user
            # Update user model fields from POST payload, fallback to current values if omitted
            (
                user.first_name,
                user.last_name,
                user.nickname,
                user.designation,
                user.phone,
            ) = (
                request.POST.get("first_name", user.first_name),
                request.POST.get("last_name", user.last_name),
                request.POST.get("nickname", user.nickname),
                request.POST.get("designation", user.designation),
                request.POST.get("phone", user.phone),
            )
            
            # Update email with uniqueness check — ensure no other user has this email
            new_email = request.POST.get("email", "").strip()
            if new_email and new_email != user.email:
                if UserModel.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                    messages.error(request, "That email address is already in use by another account.")
                    return redirect("/accounts/settings/#account")
                user.email = new_email
            elif not new_email:
                user.email = ""  # Allow clearing the email field
            
            # Save uploaded profile picture if supplied in request.FILES
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]
                
            if "avatar_color" in request.POST:
                user.avatar_color = request.POST.get("avatar_color")
                
            # If changing password, hash it and update session token to avoid automatic logout
            if request.POST.get("new_password"):
                user.set_password(request.POST.get("new_password"))
                update_session_auth_hash(request, user)
                
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("/accounts/settings/#account") # Redirect using anchor link to focus tab

        # ─── ACTION: Update User Preferences ───
        elif action == "update_preferences":
            user = request.user
            user.theme_preference = request.POST.get(
                "theme_preference", user.theme_preference
            )
            user.email_notifications = request.POST.get("email_notifications") == "on"
            user.save()
            messages.success(request, "Preferences updated successfully.")
            return redirect("/accounts/settings/#preferences")

        # ─── ACTION: Report System Issue ───
        elif action == "report_issue":
            SystemIssue.objects.create(
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                issue_type=request.POST.get("issue_type", "bug"),
                reported_by=request.user,
            )
            messages.success(request, "Thank you! Your issue has been reported.")
            return redirect("/accounts/settings/#issues")

        # ─── ACTION: Update System Settings (Admin Only) ───
        elif action == "update_system_settings" and request.user.is_admin:
            (
                sys_settings.primary_color,
                sys_settings.font_size,
                sys_settings.default_pm_password,
            ) = (
                request.POST.get("primary_color", sys_settings.primary_color),
                request.POST.get("font_size", sys_settings.font_size),
                request.POST.get(
                    "default_pm_password", sys_settings.default_pm_password
                ),
            )
            sys_settings.save()

            # Update file manager configurations
            from files.models import SystemSettings as FileSystemSettings
            files_settings = FileSystemSettings.objects.first()
            if not files_settings:
                files_settings = FileSystemSettings.objects.create()
                
            if "max_file_size_gb" in request.POST:
                try:
                    files_settings.max_file_size_gb = int(
                        request.POST.get("max_file_size_gb")
                    )
                    files_settings.save()
                except ValueError:
                    pass

            messages.success(request, "System settings updated successfully.")
            return redirect("/accounts/settings/#system")

    # Fetch configuration for file uploading
    from files.models import SystemSettings as FileSystemSettings
    files_settings = FileSystemSettings.objects.first()
    if not files_settings:
        files_settings = FileSystemSettings.objects.create()

    # Renders the settings view context
    return render(
        request,
        "accounts/settings.html",
        {
            "base_template": "base.html",
            "sys_settings": sys_settings,
            "files_settings": files_settings,
            "reported_issues": (
                SystemIssue.objects.all().order_by("-created_at")
                if request.user.is_admin
                else SystemIssue.objects.none()
            ),
            "my_issues": SystemIssue.objects.filter(
                reported_by=request.user
            ).order_by("-created_at"),
            "calendar_settings": UserCalendarSettings.objects.get_or_create(
                user=request.user
            )[0],
        },
    )
