from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def my_applications(request):
    return render(
        request,
        "applications/my_applications.html"
    )