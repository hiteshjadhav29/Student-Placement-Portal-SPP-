from django.urls import path
from . import views

app_name = "recruiters"

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register, name='recruiter_register'),
    path('login/', views.recruiter_login, name='recruiter_login'),
    path('logout/', views.recruiter_logout, name='recruiter_logout'),

    # Dashboard
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    # Profile
    path('profile/', views.recruiter_profile, name='recruiter_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]