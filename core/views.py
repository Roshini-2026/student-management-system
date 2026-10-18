from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseNotFound


def home(request):
    return HttpResponse("<h1>Home</h1>")


def about(request):
    return HttpResponse("<h1>About Us</h1>")


def services(request):
    return HttpResponse("<h1>Services</h1>")


def contact(request):
    return HttpResponse("<h1>Contact Us</h1>")


def privacy_policy(request):
    return HttpResponse("<h1>Privacy Policy</h1>")


def custom_404(request, exception):
    return HttpResponseNotFound("<h1>404 - Page not found</h1>")