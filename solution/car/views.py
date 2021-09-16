from django.shortcuts import render
from django.http import JsonResponse
from car.models import Car
import json

# Create your views here.
def create_car(request):
    """Create a car and return its full status"""
    car = Car()
    car.save()
    return JsonResponse(
        car.resume
    )
