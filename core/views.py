from django.shortcuts import render, redirect

"""
This module contains global core views (such as custom error pages handler).
"""

def home_redirect_view(request):
    """
    Redirects authenticated users to their corresponding default home portal.
    """
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    return redirect("tasks:dashboard")

def custom_page_not_found_view(request, exception=None):
    """
    Renders the custom 404 Error Page template.
    Returns status code 404 to the browser.
    """
    return render(request, "404.html", status=404)
