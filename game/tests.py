from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Game, Move


class GameModelTest(TestCase):
    def test_game_creation(self):
        """Test that a Game can be created with default values"""
        game = Game.objects.create()
        self.assertEqual(game.player_x_name, "Player X")
        self.assertEqual(game.player_o_name, "Player O")
        self.assertEqual(game.current_turn, "X")
        self.assertEqual(game.board_state, "         ")  # 9 spaces
        self.assertEqual(game.status, "IN_PROGRESS")
        self.assertIsNotNone(game.created_at)
        self.assertIsNotNone(game.updated_at)

    def test_game_creation_with_custom_names(self):
        """Test that a Game can be created with custom player names"""
        game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )
        self.assertEqual(game.player_x_name, "Alice")
        self.assertEqual(game.player_o_name, "Bob")

    def test_game_str_representation(self):
        """Test the string representation of a Game"""
        game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )
        expected_str = f"Game {game.pk}: Alice vs Bob - IN_PROGRESS"
        self.assertEqual(str(game), expected_str)


class MoveModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create()

    def test_move_creation(self):
        """Test that a Move can be created"""
        move = Move.objects.create(
            game=self.game,
            player="X",
            position=0
        )
        self.assertEqual(move.game, self.game)
        self.assertEqual(move.player, "X")
        self.assertEqual(move.position, 0)
        self.assertIsNotNone(move.created_at)

    def test_move_str_representation(self):
        """Test the string representation of a Move"""
        move = Move.objects.create(
            game=self.game,
            player="X",
            position=4
        )
        expected_str = f"Move by X at position 4 in Game {self.game.pk}"
        self.assertEqual(str(move), expected_str)

    def test_move_relationship_with_game(self):
        """Test that moves are properly related to their game"""
        move1 = Move.objects.create(game=self.game, player="X", position=0)
        move2 = Move.objects.create(game=self.game, player="O", position=1)

        # Test that the game has the moves
        game_moves = self.game.moves.all()
        self.assertEqual(game_moves.count(), 2)
        self.assertIn(move1, game_moves)
        self.assertIn(move2, game_moves)


class StartPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_start_page_loads(self):
        """Test that the start page loads correctly"""
        response = self.client.get(reverse('game:start_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TIC-TAC-TOE')
        self.assertContains(response, 'New Game')
        self.assertContains(response, 'Player X Name:')
        self.assertContains(response, 'Player O Name:')

    def test_new_game_creation_default_names(self):
        """Test creating a new game with default player names"""
        response = self.client.post(reverse('game:new_game'), {
            'player_x_name': 'Player X',
            'player_o_name': 'Player O'
        })

        # Should redirect to game board
        self.assertEqual(response.status_code, 302)

        # Check that a game was created
        game = Game.objects.first()
        self.assertIsNotNone(game)
        self.assertEqual(game.player_x_name, 'Player X')
        self.assertEqual(game.player_o_name, 'Player O')

        # Check redirect URL
        expected_url = reverse('game:game_board',
                               kwargs={'game_id': game.id})
        self.assertRedirects(response, expected_url)

    def test_new_game_creation_custom_names(self):
        """Test creating a new game with custom player names"""
        response = self.client.post(reverse('game:new_game'), {
            'player_x_name': 'Alice',
            'player_o_name': 'Bob'
        })

        # Should redirect to game board
        self.assertEqual(response.status_code, 302)

        # Check that a game was created with custom names
        game = Game.objects.first()
        self.assertIsNotNone(game)
        self.assertEqual(game.player_x_name, 'Alice')
        self.assertEqual(game.player_o_name, 'Bob')

    def test_new_game_creation_empty_names(self):
        """Test creating new game with empty names defaults to defaults"""
        response = self.client.post(reverse('game:new_game'), {
            'player_x_name': '',
            'player_o_name': ''
        })

        # Should redirect to game board
        self.assertEqual(response.status_code, 302)

        # Check that a game was created with default names
        game = Game.objects.first()
        self.assertIsNotNone(game)
        self.assertEqual(game.player_x_name, 'Player X')
        self.assertEqual(game.player_o_name, 'Player O')

    def test_new_game_get_redirects_to_start(self):
        """Test that GET request to new_game redirects to start page"""
        response = self.client.get(reverse('game:new_game'))
        self.assertRedirects(response, reverse('game:start_page'))


class GameBoardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )

    def test_game_board_loads(self):
        """Test that the game board loads correctly"""
        game_board_url = reverse('game:game_board',
                                 kwargs={'game_id': self.game.id})
        response = self.client.get(game_board_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice (X) vs Bob (O)')
        self.assertContains(response, 'Current Turn:')
        self.assertContains(response, '<strong>X</strong>')
        self.assertContains(response, 'Status:')
        self.assertContains(response, '<strong>In Progress</strong>')
        self.assertContains(response, 'Play Again')

    def test_game_board_nonexistent_game_404(self):
        """Test that accessing a nonexistent game returns 404"""
        game_board_url = reverse('game:game_board',
                                 kwargs={'game_id': 9999})
        response = self.client.get(game_board_url)
        self.assertEqual(response.status_code, 404)


class GameLogicTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )

    def test_valid_move(self):
        """Test that a valid move is accepted"""
        success, message = self.game.make_move(0, 'X')
        self.assertTrue(success)
        self.assertEqual(message, "Move successful")
        self.assertEqual(self.game.board_state[0], 'X')
        self.assertEqual(self.game.current_turn, 'O')

    def test_invalid_position(self):
        """Test that invalid positions are rejected"""
        success, message = self.game.make_move(-1, 'X')
        self.assertFalse(success)
        self.assertEqual(message, "Invalid position")

        success, message = self.game.make_move(9, 'X')
        self.assertFalse(success)
        self.assertEqual(message, "Invalid position")

    def test_wrong_turn(self):
        """Test that playing out of turn is rejected"""
        success, message = self.game.make_move(0, 'O')  # X should go first
        self.assertFalse(success)
        self.assertEqual(message, "It's X's turn")

    def test_occupied_position(self):
        """Test that occupied positions are rejected"""
        self.game.make_move(0, 'X')
        success, message = self.game.make_move(0, 'O')
        self.assertFalse(success)
        self.assertEqual(message, "Position already occupied")

    def test_win_detection_row(self):
        """Test win detection for rows"""
        # X wins first row
        self.game.make_move(0, 'X')  # X
        self.game.make_move(3, 'O')  # O
        self.game.make_move(1, 'X')  # X
        self.game.make_move(4, 'O')  # O
        self.game.make_move(2, 'X')  # X wins

        self.assertEqual(self.game.status, 'X_WON')

    def test_win_detection_column(self):
        """Test win detection for columns"""
        # X wins first column
        self.game.make_move(0, 'X')  # X
        self.game.make_move(1, 'O')  # O
        self.game.make_move(3, 'X')  # X
        self.game.make_move(2, 'O')  # O
        self.game.make_move(6, 'X')  # X wins

        self.assertEqual(self.game.status, 'X_WON')

    def test_win_detection_diagonal(self):
        """Test win detection for diagonals"""
        # X wins main diagonal
        self.game.make_move(0, 'X')  # X
        self.game.make_move(1, 'O')  # O
        self.game.make_move(4, 'X')  # X
        self.game.make_move(2, 'O')  # O
        self.game.make_move(8, 'X')  # X wins

        self.assertEqual(self.game.status, 'X_WON')

    def test_draw_detection(self):
        """Test draw detection when board is full"""
        # Skip this test for now - need to carefully construct a draw scenario
        # Will implement this after core functionality is working
        pass

    def test_move_after_game_finished(self):
        """Test that moves are rejected after game ends"""
        # Win the game first
        self.game.make_move(0, 'X')
        self.game.make_move(3, 'O')
        self.game.make_move(1, 'X')
        self.game.make_move(4, 'O')
        self.game.make_move(2, 'X')  # X wins

        # Try to make another move
        success, message = self.game.make_move(5, 'O')
        self.assertFalse(success)
        self.assertEqual(message, "Game is already finished")


class MakeMoveViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )
        self.url = reverse('game:make_move', kwargs={'game_id': self.game.id})

    def test_valid_move_ajax(self):
        """Test making a valid move via AJAX"""
        response = self.client.post(
            self.url,
            data=json.dumps({'position': 0, 'player': 'X'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Move successful')
        self.assertEqual(data['board_state'][0], 'X')
        self.assertEqual(data['current_turn'], 'O')

    def test_invalid_move_ajax(self):
        """Test making an invalid move via AJAX"""
        response = self.client.post(
            self.url,
            data=json.dumps({'position': 0, 'player': 'O'}),  # Wrong turn
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "It's X's turn")

    def test_invalid_request_data(self):
        """Test handling of invalid request data"""
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Invalid request data')
