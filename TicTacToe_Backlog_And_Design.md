# Tic-Tac-Toe Game – Product Backlog, Data Models, and Wireframes (Django)

---

## Product Backlog Items (PBIs)

### PBI 1: Set Up Django Project and App
- **Description:** Initialize a new Django project and app for the Tic-Tac-Toe game.
- **Acceptance Criteria:**
  - Django project and app created in version control.
  - Project runs locally using `manage.py runserver`.

---

### PBI 2: Define Data Models
- **Description:** Create Django models to store games, moves, and player information.
- **Acceptance Criteria:**
  - Models for Game, Move, and Player (optional for named players) exist.
  - Database migrations are created and applied.
  - Admin interface displays models appropriately.

---

### PBI 3: Game Board UI – Start Page
- **Description:** Implement a page for starting a new Tic-Tac-Toe game.
- **Acceptance Criteria:**
  - "New Game" button is present.
  - On clicking, a new game is created and the player is redirected to the game board.

---

### PBI 4: Game Board UI – Play Game
- **Description:** Implement the game board interface allowing two players to play.
- **Acceptance Criteria:**
  - 3x3 grid is displayed.
  - Players can click cells to make moves alternately.
  - Board updates after each move.
  - Invalid moves (cell already occupied, playing out of turn) are prevented.

---

### PBI 5: Game Logic and Validation
- **Description:** Implement backend logic to enforce game rules and validate moves.
- **Acceptance Criteria:**
  - Only valid moves are accepted.
  - Game detects wins and draws.
  - Winning combination is highlighted in UI.

---

### PBI 6: Game State & Messaging
- **Description:** Display game state and notifications to players.
- **Acceptance Criteria:**
  - Current player/turn is shown.
  - Win/draw messages are displayed.
  - "Play Again" button shown after game ends.

---

### PBI 7: Responsive and Accessible UI
- **Description:** Ensure the web interface is responsive and accessible.
- **Acceptance Criteria:**
  - Works on mobile and desktop browsers.
  - Uses semantic HTML and ARIA where appropriate.

---

### PBI 8: Optional – Player Names and Score Tracking
- **Description:** Allow players to enter names and track scores across games.
- **Acceptance Criteria:**
  - Name entry form before game starts.
  - Scoreboard displayed and updated after each game.

---

### PBI 9: Optional – Single Player Against AI
- **Description:** Add an option to play against a simple AI.
- **Acceptance Criteria:**
  - "Play vs AI" button is available.
  - AI makes valid moves.
  - All game logic applies as in two-player mode.

---

## Data Models (Django Example)

```python name=game/models.py
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

class Move(models.Model):
    game = models.ForeignKey(Game, related_name='moves', on_delete=models.CASCADE)
    player = models.CharField(max_length=1, choices=Game.PLAYER_CHOICES)
    position = models.IntegerField()  # 0-8 for 3x3 grid
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Wireframes

### 1. Start Page

```
+---------------------------+
|      TIC-TAC-TOE          |
|                           |
|  [ Player X Name: ______ ]|
|  [ Player O Name: ______ ]|
|                           |
|  [ New Game ]   [ Play vs AI ]  |
+---------------------------+
```

---

### 2. Game Board Page

```
+---------------------------+
|   Player X (X) vs Player O (O)   |
|   Current Turn: X                |
|                                 |
|     |     |     |
|  X  |  O  |     |
|-----|-----|-----|
|     |  X  |     |
|-----|-----|-----|
|  O  |     |  X  |
|                                 |
|  [ Play Again ]                 |
|                                 |
|  [ Message: X wins! ]           |
+---------------------------+
```

---

### 3. Scoreboard (Optional)

```
+---------------------------+
|    Scoreboard             |
|   Player X: 2             |
|   Player O: 1             |
+---------------------------+
```

---

## Notes

- Board state can be stored as a 9-character string (e.g., "XOX O XO ") for simplicity.
- All validation and win/draw checking should be done server-side.
- Use AJAX or page reloads for move submissions (no real-time websockets required for MVP).
- Wireframes are text-based for clarity; UI can be styled as desired.

---

Let me know if you want this broken down into GitHub issues or need more technical detail on any section!