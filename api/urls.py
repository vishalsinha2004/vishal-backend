# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('system-apps/', views.get_system_apps, name='get_system_apps'),
    path('system-os/', views.get_system_os, name='get_system_os'),
    
    # --- NEW: About Us Endpoint ---
    path('about-us/', views.get_about_me, name='get_about_me'),
    path('ai-search/', views.GroqAISearchView.as_view(), name='ai-search'),
    path('voice-assistant/', views.GroqVoiceAssistantView.as_view(), name='voice-assistant'),
]