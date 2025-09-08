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
    current_turn = models.CharField(max_length=1, choices=PLAYER_CHOICES, default='X')
    board_state = models.CharField(max_length=9, default=' ' * 9)  # e.g., "XOX O XO "
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.pk}: {self.player_x_name} vs {self.player_o_name} - {self.status}"


class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves', on_delete=models.CASCADE)
    player = models.CharField(max_length=1, choices=Game.PLAYER_CHOICES)
    position = models.IntegerField()  # 0-8 for 3x3 grid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move by {self.player} at position {self.position} in Game {self.game.pk}"
