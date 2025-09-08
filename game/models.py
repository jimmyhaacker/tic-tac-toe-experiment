from django.db import models


class Game(models.Model):
    PLAYER_CHOICES = (
        ('X', 'Player X'),
        ('O', 'Player O'),
    )
    STATUS_CHOICES = (
        ('IN_PROGRESS', 'In Progress'),
        ('X_WON', 'X Won'),
        ('O_WON', 'O Won'),
        ('DRAW', 'Draw'),
    )
    player_x_name = models.CharField(max_length=30, default="Player X")
    player_o_name = models.CharField(max_length=30, default="Player O")
    current_turn = models.CharField(max_length=1, choices=PLAYER_CHOICES,
                                    default='X')
    board_state = models.CharField(max_length=9, default=' ' * 9)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES,
                              default='IN_PROGRESS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (f"Game {self.pk}: {self.player_x_name} vs "
                f"{self.player_o_name} - {self.status}")

    def make_move(self, position, player):
        """
        Make a move at the specified position for the given player.
        Returns tuple (success: bool, message: str)
        """
        # Validate position
        if position < 0 or position > 8:
            return False, "Invalid position"

        # Check if game is finished
        if self.status != 'IN_PROGRESS':
            return False, "Game is already finished"

        # Check if it's the player's turn
        if self.current_turn != player:
            return False, f"It's {self.current_turn}'s turn"

        # Check if position is already occupied
        if self.board_state[position] != ' ':
            return False, "Position already occupied"

        # Make the move
        board_list = list(self.board_state)
        board_list[position] = player
        self.board_state = ''.join(board_list)

        # Create Move record
        Move.objects.create(game=self, player=player, position=position)

        # Check for win
        if self._check_winner():
            self.status = f"{player}_WON"
        # Check for draw
        elif self._check_draw():
            self.status = 'DRAW'
        else:
            # Switch turns
            self.current_turn = 'O' if player == 'X' else 'X'

        self.save()
        return True, "Move successful"

    def _check_winner(self):
        """Check if there's a winner on the board"""
        board = self.board_state

        # Winning combinations
        win_patterns = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for pattern in win_patterns:
            if (board[pattern[0]] == board[pattern[1]] == board[pattern[2]] and
                    board[pattern[0]] != ' '):
                return True
        return False

    def _check_draw(self):
        """Check if the game is a draw (board full with no winner)"""
        return ' ' not in self.board_state


class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves',
                             on_delete=models.CASCADE)
    player = models.CharField(max_length=1, choices=Game.PLAYER_CHOICES)
    position = models.IntegerField()  # 0-8 for 3x3 grid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Move by {self.player} at position {self.position} "
                f"in Game {self.game.pk}")
