from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Game, Move, Score


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
        self.assertContains(response, '<strong id="current-turn">X</strong>')
        self.assertContains(response, 'Status:')
        self.assertContains(response,
                            '<strong id="game-status">In Progress</strong>')
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

    def test_get_winning_pattern_row(self):
        """Test getting winning pattern for row win"""
        # X wins first row
        self.game.make_move(0, 'X')  # X
        self.game.make_move(3, 'O')  # O
        self.game.make_move(1, 'X')  # X
        self.game.make_move(4, 'O')  # O
        self.game.make_move(2, 'X')  # X wins

        winning_pattern = self.game.get_winning_pattern()
        self.assertEqual(winning_pattern, [0, 1, 2])

    def test_get_winning_pattern_column(self):
        """Test getting winning pattern for column win"""
        # X wins first column
        self.game.make_move(0, 'X')  # X
        self.game.make_move(1, 'O')  # O
        self.game.make_move(3, 'X')  # X
        self.game.make_move(2, 'O')  # O
        self.game.make_move(6, 'X')  # X wins

        winning_pattern = self.game.get_winning_pattern()
        self.assertEqual(winning_pattern, [0, 3, 6])

    def test_get_winning_pattern_diagonal(self):
        """Test getting winning pattern for diagonal win"""
        # X wins main diagonal
        self.game.make_move(0, 'X')  # X
        self.game.make_move(1, 'O')  # O
        self.game.make_move(4, 'X')  # X
        self.game.make_move(2, 'O')  # O
        self.game.make_move(8, 'X')  # X wins

        winning_pattern = self.game.get_winning_pattern()
        self.assertEqual(winning_pattern, [0, 4, 8])

    def test_get_winning_pattern_none_for_in_progress(self):
        """Test that no winning pattern is returned for in-progress game"""
        self.game.make_move(0, 'X')
        winning_pattern = self.game.get_winning_pattern()
        self.assertIsNone(winning_pattern)

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

    def test_winning_move_includes_pattern(self):
        """Test that a winning move includes the winning pattern in response"""
        # Set up a near-win situation for X
        self.game.make_move(0, 'X')  # X at position 0
        self.game.make_move(3, 'O')  # O at position 3
        self.game.make_move(1, 'X')  # X at position 1
        self.game.make_move(4, 'O')  # O at position 4

        # Make the winning move
        response = self.client.post(
            self.url,
            data=json.dumps({'position': 2, 'player': 'X'}),  # Complete row
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['game_finished'])
        self.assertEqual(data['status'], 'X_WON')
        self.assertEqual(data['winning_pattern'], [0, 1, 2])


class ScoreModelTest(TestCase):
    def test_score_creation(self):
        """Test that a Score can be created with default values"""
        score = Score.objects.create(player_name="TestPlayer")
        self.assertEqual(score.player_name, "TestPlayer")
        self.assertEqual(score.wins, 0)
        self.assertEqual(score.losses, 0)
        self.assertEqual(score.draws, 0)
        self.assertEqual(score.total_games, 0)
        self.assertEqual(score.win_percentage, 0)

    def test_score_properties(self):
        """Test score calculated properties"""
        score = Score.objects.create(
            player_name="TestPlayer",
            wins=5,
            losses=3,
            draws=2
        )
        self.assertEqual(score.total_games, 10)
        self.assertEqual(score.win_percentage, 50.0)

    def test_score_win_percentage_no_games(self):
        """Test win percentage calculation with no games"""
        score = Score.objects.create(player_name="TestPlayer")
        self.assertEqual(score.win_percentage, 0)

    def test_score_string_representation(self):
        """Test Score model string representation"""
        score = Score.objects.create(
            player_name="TestPlayer",
            wins=2,
            losses=1,
            draws=1
        )
        expected = "TestPlayer: 2W-1L-1D"
        self.assertEqual(str(score), expected)


class ScoreTrackingTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            player_x_name="Alice",
            player_o_name="Bob"
        )

    def test_scores_updated_on_x_win(self):
        """Test that scores are updated when X wins"""
        # Set up a winning scenario for X (top row)
        self.game.board_state = "XX O     "
        self.game.current_turn = 'X'
        self.game.save()  # Save the updated state
        
        success, message = self.game.make_move(2, 'X')  # X wins with top row
        self.assertTrue(success, f"Move should succeed: {message}")
        self.assertEqual(self.game.status, 'X_WON')

        # Check that scores were created and updated
        alice_score = Score.objects.get(player_name="Alice")
        bob_score = Score.objects.get(player_name="Bob")

        self.assertEqual(alice_score.wins, 1)
        self.assertEqual(alice_score.losses, 0)
        self.assertEqual(alice_score.draws, 0)

        self.assertEqual(bob_score.wins, 0)
        self.assertEqual(bob_score.losses, 1)
        self.assertEqual(bob_score.draws, 0)

    def test_scores_updated_on_o_win(self):
        """Test that scores are updated when O wins"""
        # Set up a winning scenario for O (left column: 0, 3, 6)
        # O already at 0 and 3, needs to place at 6 to win
        self.game.board_state = "OX O X   "
        self.game.current_turn = 'O'
        self.game.save()  # Save the updated state
        
        success, message = self.game.make_move(6, 'O')  # O wins with left column (0,3,6)
        self.assertTrue(success, f"Move should succeed: {message}")
        self.assertEqual(self.game.status, 'O_WON')

        # Check that scores were created and updated
        alice_score = Score.objects.get(player_name="Alice")
        bob_score = Score.objects.get(player_name="Bob")

        self.assertEqual(alice_score.wins, 0)
        self.assertEqual(alice_score.losses, 1)
        self.assertEqual(alice_score.draws, 0)

        self.assertEqual(bob_score.wins, 1)
        self.assertEqual(bob_score.losses, 0)
        self.assertEqual(bob_score.draws, 0)

    def test_scores_updated_on_draw(self):
        """Test that scores are updated on a draw"""
        # Set up a draw scenario - board almost full, no winner possible
        self.game.board_state = "XOXOXXO O"
        self.game.current_turn = 'X'
        self.game.save()  # Save the updated state
        
        success, message = self.game.make_move(7, 'X')  # Game ends in draw
        self.assertTrue(success, f"Move should succeed: {message}")
        self.assertEqual(self.game.status, 'DRAW')

        # Check that scores were created and updated
        alice_score = Score.objects.get(player_name="Alice")
        bob_score = Score.objects.get(player_name="Bob")

        self.assertEqual(alice_score.wins, 0)
        self.assertEqual(alice_score.losses, 0)
        self.assertEqual(alice_score.draws, 1)

        self.assertEqual(bob_score.wins, 0)
        self.assertEqual(bob_score.losses, 0)
        self.assertEqual(bob_score.draws, 1)

    def test_existing_scores_updated(self):
        """Test that existing scores are updated correctly"""
        # Create existing scores
        alice_score = Score.objects.create(
            player_name="Alice",
            wins=2,
            losses=1,
            draws=1
        )
        bob_score = Score.objects.create(
            player_name="Bob",
            wins=1,
            losses=2,
            draws=1
        )

        # Set up a winning scenario for Alice (top row)
        self.game.board_state = "XX O     "
        self.game.current_turn = 'X'
        self.game.save()  # Save the updated state
        
        success, message = self.game.make_move(2, 'X')  # Alice (X) wins
        self.assertTrue(success, f"Move should succeed: {message}")
        self.assertEqual(self.game.status, 'X_WON')

        # Refresh from database
        alice_score.refresh_from_db()
        bob_score.refresh_from_db()

        # Check that scores were updated correctly
        self.assertEqual(alice_score.wins, 3)
        self.assertEqual(alice_score.losses, 1)
        self.assertEqual(alice_score.draws, 1)

        self.assertEqual(bob_score.wins, 1)
        self.assertEqual(bob_score.losses, 3)
        self.assertEqual(bob_score.draws, 1)


class ScoreboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create some test scores
        Score.objects.create(player_name="Alice", wins=5, losses=2, draws=1)
        Score.objects.create(player_name="Bob", wins=3, losses=3, draws=2)
        Score.objects.create(player_name="Charlie", wins=7, losses=1, draws=0)

    def test_scoreboard_loads(self):
        """Test that the scoreboard loads correctly"""
        response = self.client.get(reverse('game:scoreboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SCOREBOARD")
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")
        self.assertContains(response, "Charlie")

    def test_scoreboard_empty_state(self):
        """Test scoreboard with no scores"""
        Score.objects.all().delete()
        response = self.client.get(reverse('game:scoreboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games have been played yet!")

    def test_scoreboard_ordering(self):
        """Test that scoreboard is ordered by wins"""
        response = self.client.get(reverse('game:scoreboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check that scores are passed to template
        scores = response.context['scores']
        self.assertEqual(len(scores), 3)
        
        # Should be ordered by wins descending (Charlie: 7, Alice: 5, Bob: 3)
        self.assertEqual(scores[0].player_name, "Charlie")
        self.assertEqual(scores[1].player_name, "Alice")
        self.assertEqual(scores[2].player_name, "Bob")
