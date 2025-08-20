"""
Debug view to test payment flow
"""
from django.http import JsonResponse
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class PaymentDebugView(View):
    """
    Simple debug view to test payment redirection
    """
    
    def get(self, request):
        """
        Test GET request handling
        """
        logger.info("PaymentDebugView GET called")
        return JsonResponse({
            'status': 'success',
            'message': 'Payment debug view working',
            'session': dict(request.session.items())
        })
    
    def post(self, request):
        """
        Test POST request handling
        """
        logger.info("PaymentDebugView POST called")
        logger.info(f"POST data: {request.POST}")
        
        # Add a test message and redirect
        messages.success(request, "Payment form submitted successfully!")
        return redirect('checkout:payment-details')
