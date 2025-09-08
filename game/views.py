from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Game, Score


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


def new_ai_game(request):
    """Create a new AI game and redirect to the game board"""
    if request.method == 'POST':
        player_x_name = request.POST.get('player_x_name', 'Player X').strip()
        
        # Ensure name is not empty
        if not player_x_name:
            player_x_name = 'Player X'

        # Create new AI game (player is X, AI is O)
        game = Game.objects.create(
            player_x_name=player_x_name,
            player_o_name="AI",
            is_ai_game=True
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


@csrf_exempt
@require_POST
def make_move(request, game_id):
    """Handle making a move in the game via AJAX"""
    try:
        game = get_object_or_404(Game, id=game_id)
        data = json.loads(request.body)
        position = int(data.get('position'))
        player = data.get('player')

        # Validate player matches current turn
        if player != game.current_turn:
            return JsonResponse({
                'success': False,
                'message': f"It's {game.current_turn}'s turn"
            })

        # Make the move
        success, message = game.make_move(position, player)

        if success:
            # Trigger AI move if it's an AI game and game is still in progress
            ai_move_success = False
            ai_message = ""
            if (game.is_ai_game and game.status == 'IN_PROGRESS' and 
                game.current_turn == 'O'):
                ai_move_success, ai_message = game.make_ai_move()
            
            # Return updated game state (after potential AI move)
            response_data = {
                'success': True,
                'message': message,
                'board_state': list(game.board_state),
                'current_turn': game.current_turn,
                'status': game.status,
                'status_display': game.get_status_display(),
                'game_finished': game.status != 'IN_PROGRESS',
                'winning_pattern': game.get_winning_pattern()
            }
            
            # Add AI move info if AI moved
            if game.is_ai_game and ai_move_success:
                response_data['ai_moved'] = True
                response_data['ai_message'] = ai_message
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'message': message
            })

    except (json.JSONDecodeError, ValueError, KeyError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data'
        })
    except Exception:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred'
        })


def scoreboard(request):
    """Display the scoreboard with player statistics"""
    scores = Score.objects.all()
    
    # Sort by wins descending, then by win percentage
    sorted_scores = sorted(scores, key=lambda x: (x.wins, x.win_percentage), reverse=True)
    
    context = {
        'scores': sorted_scores,
    }
    
    return render(request, 'game/scoreboard.html', context)
