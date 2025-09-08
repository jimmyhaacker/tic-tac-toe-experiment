from django.test import TestCase
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
