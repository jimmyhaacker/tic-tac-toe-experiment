from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('new-game/', views.new_game, name='new_game'),
    path('game/<int:game_id>/', views.game_board, name='game_board'),
    path('game/<int:game_id>/move/', views.make_move, name='make_move'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
]
