from django.contrib import admin
from .models import Game, Move


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player_x_name', 'player_o_name', 'current_turn',
                    'status', 'created_at', 'updated_at')
    list_filter = ('status', 'current_turn', 'created_at')
    search_fields = ('player_x_name', 'player_o_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'player', 'position', 'created_at')
    list_filter = ('player', 'created_at')
    search_fields = ('game__id', 'game__player_x_name',
                     'game__player_o_name')
