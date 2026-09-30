from django.urls import path
from . import views

urlpatterns = [
    # መነሻው ሊንክ ሲጠየቅ የትኛው ቪው (ለምሳሌ game_view) እንደሚከፈት
    path('', views.game_view, name='game_home'), 
]