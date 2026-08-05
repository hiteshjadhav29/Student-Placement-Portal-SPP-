from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/start-session/', views.start_session, name='start_session'),
    path('api/next-question/', views.next_question, name='next_question'),
    path('api/evaluate-session/', views.evaluate_session, name='evaluate_session'),
    path('api/session-history/', views.session_history, name='session_history'),
]
