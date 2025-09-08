from django.shortcuts import render, redirect, get_object_or_404
from .models import Game


def start_page(request):
    """Display the start page for creating a new game"""
    return render(request, 'game/start_page.html')


def new_game(request):
    """Create a new game and redirect to the game board"""
    if request.method == 'POST':
        player_x_name = request.POST.get('player_x_name', 'Player X').strip()
        player_o_name = request.POST.get('player_o_name', 'Player O').strip()

        # Ensure names are not empty
        if not player_x_name:
            player_x_name = 'Player X'
        if not player_o_name:
            player_o_name = 'Player O'

        # Create new game
        game = Game.objects.create(
            player_x_name=player_x_name,
            player_o_name=player_o_name
        )

        return redirect('game:game_board', game_id=game.id)

    # If not POST, redirect to start page
    return redirect('game:start_page')


def game_board(request, game_id):
    """Display the game board for a specific game"""
    game = get_object_or_404(Game, id=game_id)

    # Convert board_state string to list for template
    board_cells = list(game.board_state)

    context = {
        'game': game,
        'board_cells': board_cells,
    }

    return render(request, 'game/game_board.html', context)
