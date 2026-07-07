import logging

from django.shortcuts import redirect

logger = logging.getLogger(__name__)

"""
This module defines Django Custom Middleware classes.
Middleware is a framework of hooks into Django's request/response processing.
It's a light, low-level 'plugin' system for globally altering Django's input or output.
"""

class InventoryAccessMiddleware:
    """
    Middleware placeholder retained for compatibility.
    Inventory and Telescope management have been removed from this project.
    This middleware now simply passes requests through without modification.
    """

    def __init__(self, get_response):
        """
        One-time configuration and initialization.
        get_response is the next middleware or view callable in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later middleware) are called.
        """
        # Process the request normally and return the generated response
        response = self.get_response(request)
        return response
