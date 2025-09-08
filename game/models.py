from django.db import models


class Score(models.Model):
    player_name = models.CharField(max_length=30, unique=True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player_name}: {self.wins}W-{self.losses}L-{self.draws}D"

    @property
    def total_games(self):
        return self.wins + self.losses + self.draws

    @property
    def win_percentage(self):
        if self.total_games == 0:
            return 0
        return round((self.wins / self.total_games) * 100, 1)

    class Meta:
        ordering = ['-wins', 'player_name']


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
        
        # Update scores if game finished
        if self.status != 'IN_PROGRESS':
            self.update_scores()
            
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

    def get_winning_pattern(self):
        """Get the winning pattern positions if there's a winner"""
        if self.status not in ['X_WON', 'O_WON']:
            return None

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
                return pattern
        return None

    def _check_draw(self):
        """Check if the game is a draw (board full with no winner)"""
        return ' ' not in self.board_state

    def update_scores(self):
        """Update player scores when game finishes"""
        if self.status == 'IN_PROGRESS':
            return  # Game not finished yet

        # Get or create score records for both players
        x_score, _ = Score.objects.get_or_create(
            player_name=self.player_x_name
        )
        o_score, _ = Score.objects.get_or_create(
            player_name=self.player_o_name
        )

        # Update scores based on game result
        if self.status == 'X_WON':
            x_score.wins += 1
            o_score.losses += 1
        elif self.status == 'O_WON':
            o_score.wins += 1
            x_score.losses += 1
        elif self.status == 'DRAW':
            x_score.draws += 1
            o_score.draws += 1

        # Save the updated scores
        x_score.save()
        o_score.save()


class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves',
                             on_delete=models.CASCADE)
    player = models.CharField(max_length=1, choices=Game.PLAYER_CHOICES)
    position = models.IntegerField()  # 0-8 for 3x3 grid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Move by {self.player} at position {self.position} "
                f"in Game {self.game.pk}")
