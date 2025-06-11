from django.shortcuts import render

def index(request):
    """Vista principal del dashboard."""
    return render(request, "dashboard/index.html")
