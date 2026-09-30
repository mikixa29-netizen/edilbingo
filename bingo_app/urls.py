from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/game-data/', views.get_game_data, name='get_game_data'),
    path('api/select-cartela/', views.select_cartela, name='select_cartela'),
]