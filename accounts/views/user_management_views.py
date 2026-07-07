from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from tasks.decorators import admin_required
from ..models import User
from ..forms import AdminPasswordResetForm, UserCreateForm, UserEditForm

"""
This module handles User Administration and Management Views.
It is secured by `@login_required` and `@admin_required` decorators, meaning
only authenticated administrators can perform operations within these endpoints.

Key capabilities:
1. Unified User List view for Project Management users.
2. Filter & Search capabilities on user lists using Q objects.
3. Pagination of users using Django's Paginator class.
4. CRUD operations for standard Project Management users.
5. Password resets and role changes.
"""

@login_required
@admin_required
def user_list(request):
    """
    Lists Project Management users.
    Supports searching by text and filtering by role, department/team, and account status.
    """
    # Retrieve query and filter options from the request's GET parameters
    search, role_filter, team_filter, status_filter = (
        request.GET.get("q", ""),
        request.GET.get("role", ""),
        request.GET.get("team", ""),
        request.GET.get("status", ""),
    )

    # PM users have the 'can_access_pm' flag enabled
    users = User.objects.filter(can_access_pm=True).order_by("-date_joined")

    # Apply filters
    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(designation__icontains=search)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    if team_filter:
        users = users.filter(team=team_filter)
    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    # Compute status statistics
    stats = {
        "total": User.objects.filter(can_access_pm=True).count(),
        "active": User.objects.filter(can_access_pm=True, is_active=True).count(),
        "inactive": User.objects.filter(can_access_pm=True, is_active=False).count(),
        "admins": User.objects.filter(can_access_pm=True, role="admin").count(),
        "managers": User.objects.filter(can_access_pm=True, role="project_manager").count(),
        "members": User.objects.filter(can_access_pm=True, role="member").count(),
    }

    # Paginate results (10 users per page)
    page_obj = Paginator(users, 10).get_page(request.GET.get("page"))
    
    return render(
        request,
        "accounts/user_list.html",
        {
            "users": page_obj,
            "page_obj": page_obj,
            "stats": stats,
            "search": search,
            "role_filter": role_filter,
            "team_filter": team_filter,
            "status_filter": status_filter,
            "role_choices": User.ROLE_CHOICES,
            "team_choices": User.MODULE_CHOICES,
            "active_tab": "pm",
        },
    )


@login_required
@admin_required
def user_create(request):
    """
    Renders and processes user registration form to create a new Project Management User.
    """
    form = UserCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            # Save the new user instance
            user = form.save()
            messages.success(request, f'✅ User "{user.username}" created.')
            # Redirect to the detail page of the newly created user profile
            return redirect("accounts:user_detail", pk=user.pk)
            
        messages.error(request, "Please fix the errors below.")
        
    return render(
        request,
        "accounts/user_form.html",
        {"form": form, "title": "Create New User", "action": "Create User"},
    )


@login_required
@admin_required
def user_detail(request, pk):
    """
    Renders the profile dashboard of a specific user.
    Shows assigned tasks and metrics for that specific user.
    """
    from tasks.models import Project, Task

    # Fetch the user using primary key (pk) or raise 404 error if not found
    profile_user = get_object_or_404(User, pk=pk)
    
    # Query tasks assigned to this user.
    # select_related performs a SQL join to fetch related project data in a single query (performance optimization).
    assigned_tasks = Task.objects.filter(assignees=profile_user).select_related(
        "project"
    )
    
    # Calculate task metrics for this specific user
    task_stats = {
        "total": assigned_tasks.count(),
        "todo": assigned_tasks.filter(status="todo").count(),
        "in_progress": assigned_tasks.filter(status="in_progress").count(),
        "done": assigned_tasks.filter(status="done").count(),
        "overdue": sum(1 for t in assigned_tasks if t.is_overdue),
    }
    
    return render(
        request,
        "accounts/user_detail.html",
        {
            "profile_user": profile_user,
            "assigned_tasks": assigned_tasks[:10], # Limit list to top 10 tasks
            "managed_projects": Project.objects.filter(managers=profile_user),
            "member_projects": Project.objects.filter(members=profile_user),
            "task_stats": task_stats,
        },
    )


@login_required
@admin_required
def user_edit(request, pk):
    """
    Edits a PM user's account details.
    """
    edit_user = get_object_or_404(User, pk=pk)
    # Bind form to the edit_user instance for pre-populating inputs
    form = UserEditForm(request.POST or None, instance=edit_user)
    
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request, f'User "{edit_user.username}" updated successfully.'
            )
            return redirect("accounts:user_detail", pk=edit_user.pk)
            
        messages.error(request, "Please fix the errors below.")
        
    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": f"Edit User — {edit_user.username}",
            "action": "Save Changes",
            "edit_user": edit_user,
        },
    )


@login_required
@admin_required
def user_reset_password(request, pk):
    """
    Allows admins to perform manual password overrides for a user account.
    """
    reset_user = get_object_or_404(User, pk=pk)
    form = AdminPasswordResetForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            # Update password and save changes
            reset_user.set_password(form.cleaned_data["new_password1"])
            reset_user.save()
            messages.success(
                request, f'✅ Password for "{reset_user.username}" has been reset.'
            )
            return redirect("accounts:user_detail", pk=reset_user.pk)
            
        messages.error(request, "Please fix the errors below.")
        
    return render(
        request,
        "accounts/user_reset_password.html",
        {"form": form, "reset_user": reset_user},
    )


@login_required
@admin_required
def user_delete(request, pk):
    """
    Permanently deletes a user account. Includes safety guard against self-deletion.
    """
    del_user = get_object_or_404(User, pk=pk)
    
    # Safety guard: prevent self-deletion
    if del_user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("accounts:user_list")
        
    if request.method == "POST":
        username = del_user.username
        # Deactivate user instead of delete
        del_user.is_active = False
        del_user.save(update_fields=["is_active"])
        messages.success(request, f'User "{username}" deactivated instead of deleted.')
        return redirect("accounts:user_list")
        
    return render(request, "accounts/user_confirm_delete.html", {"user_obj": del_user})


@login_required
@admin_required
def user_toggle_active(request, pk):
    """
    Deactivates or activates a user.
    Deactivating blocks authentication while preserving historical task/project links.
    """
    toggle_user = get_object_or_404(User, pk=pk)
    
    # Safety guard: prevent self-deactivation
    if toggle_user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("accounts:user_list")
        
    # Toggle boolean state
    toggle_user.is_active = not toggle_user.is_active
    toggle_user.save()
    
    messages.success(
        request,
        f'User "{toggle_user.username}" {"activated" if toggle_user.is_active else "deactivated"}.',
    )
    return redirect(request.META.get("HTTP_REFERER", "accounts:user_list"))


@login_required
@require_POST
def change_user_role(request, pk):
    """
    AJAX endpoint to quickly update a user's role on the list view.
    Only allows requests originating from POST protocol. Returns JsonResponse.
    """
    # Authorization checks
    if not (request.user.is_superuser or request.user.is_admin):
        return JsonResponse({"ok": False, "error": "Permission denied."}, status=403)
        
    target_user = get_object_or_404(User, pk=pk)
    
    if target_user.is_superuser and not request.user.is_superuser:
        return JsonResponse(
            {"ok": False, "error": "Cannot change a superuser account."}, status=403
        )
        
    if target_user == request.user:
        return JsonResponse(
            {"ok": False, "error": "You cannot change your own role here."}, status=400
        )
        
    new_role = request.POST.get("role", "")
    
    # Check if role value is defined in ROLE_CHOICES
    if new_role not in [r[0] for r in User.ROLE_CHOICES]:
        return JsonResponse(
            {"ok": False, "error": f"Invalid role: {new_role}"}, status=400
        )
        
    old_role = target_user.get_role_display()
    target_user.role = new_role
    
    # Optimizes DB save by updating only the 'role' field column
    target_user.save(update_fields=["role"])
    
    return JsonResponse(
        {
            "ok": True,
            "message": f"✅ {target_user.display_name} role changed from {old_role} to {target_user.get_role_display()}.",
            "new_role": new_role,
            "new_role_display": target_user.get_role_display(),
        }
    )
