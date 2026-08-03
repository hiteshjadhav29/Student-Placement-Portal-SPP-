from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path(
        "",
        views.my_applications,
        name="my_applications"
    ),
]