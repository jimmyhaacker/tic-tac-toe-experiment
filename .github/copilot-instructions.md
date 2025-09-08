# Tic-Tac-Toe Django Project

**ALWAYS follow these instructions first** and only fallback to additional search and context gathering if the information here is incomplete or found to be in error.

This is a Django-based tic-tac-toe web application designed for two players. The repository currently contains specification documents but no implementation yet.

## Working Effectively

### Initial Environment Setup
- Python 3.12.3 and pip3 are pre-installed in the environment
- Install Django: `pip3 install Django` -- takes ~4 seconds
- Install linting tools: `pip3 install flake8` -- takes ~2 seconds

### Bootstrapping the Django Project (First Time Setup)
When no Django project exists yet, create it using these exact commands:

```bash
# Create project structure
django-admin startproject tictactoe_project .
python3 manage.py startapp game

# Add 'game' to INSTALLED_APPS in tictactoe_project/settings.py
```

### Building and Setup
- Run initial migrations: `python3 manage.py migrate` -- takes ~0.4 seconds
- Create models based on specifications in TicTacToe_Backlog_And_Design.md
- Add models to INSTALLED_APPS in settings.py
- Create migrations: `python3 manage.py makemigrations` -- takes ~0.3 seconds  
- Apply migrations: `python3 manage.py migrate` -- takes ~0.3 seconds

### Running the Application
- **Development server**: `python3 manage.py runserver 0.0.0.0:8000`
  - Server starts in ~0.3 seconds
  - Access at http://localhost:8000/
  - **NEVER CANCEL** - Server runs continuously until stopped with Ctrl+C
- **Background server**: Add `&` to run in background, use different ports (8001, 8002, etc.) to avoid conflicts

### Testing
- **Run tests**: `python3 manage.py test` -- takes ~0.4 seconds when no tests exist, ~0.4 seconds with basic model tests
- **NEVER CANCEL** - Wait for all tests to complete
- Tests create and destroy test database automatically

### Linting and Code Quality
- **Django system checks**: `python3 manage.py check` -- takes ~0.3 seconds
- **Python linting**: `flake8 . --exclude=migrations,venv,__pycache__` -- takes ~0.2 seconds
- **CRITICAL**: Always run both checks before committing changes

## Validation Scenarios

**ALWAYS manually validate changes** by running complete user scenarios:

### Basic Validation Workflow
1. Start the development server: `python3 manage.py runserver 0.0.0.0:8000`
2. Navigate to http://localhost:8000/ in browser
3. Verify the home page loads correctly
4. Test any API endpoints (e.g., /api/game/)
5. Ensure proper JSON responses and status codes

### Full End-to-End Testing
After making changes, always test:
- Create a new game through the web interface
- Make moves alternately (X and O)
- Verify move validation (no overwriting occupied cells)
- Test win detection and game end scenarios
- Verify "Play Again" functionality

## Project Structure and Key Files

### Repository Root
```
.
├── .github/                    # GitHub configuration
├── TicTacToe_Backlog_And_Design.md    # Product specifications and models
├── TicTacToe_Scrum_Specification.md   # User stories and requirements
├── chats/                      # Planning discussions
├── manage.py                   # Django management script (when created)
├── tictactoe_project/          # Django project settings (when created)
└── game/                       # Django app for game logic (when created)
```

### Django App Structure (After Creation)
```
game/
├── models.py          # Game and Move models (see specifications)
├── views.py           # Game views and API endpoints  
├── urls.py            # URL routing
├── tests.py           # Unit tests
├── admin.py           # Django admin configuration
├── templates/game/    # HTML templates
└── migrations/        # Database migrations
```

## Data Models

Implement these models exactly as specified in TicTacToe_Backlog_And_Design.md:

```python
class Game(models.Model):
    # Player choices, status choices, names, board state, etc.
    # See TicTacToe_Backlog_And_Design.md for complete model definition

class Move(models.Model):
    # Move tracking with game reference, player, position
```

## Critical Timing and Timeout Guidelines

- **Django installation**: 4 seconds (use 30 second timeout)
- **Project creation**: <1 second (use 30 second timeout)  
- **Migrations**: <1 second (use 30 second timeout)
- **Tests**: <1 second (use 30 second timeout)
- **Server startup**: <1 second (use 30 second timeout)
- **Linting**: <1 second (use 30 second timeout)

**NEVER CANCEL** any of these operations - they complete quickly but timeouts prevent hanging.

## Common Development Tasks

### Adding New Features
1. Update models.py if database changes needed
2. Run `python3 manage.py makemigrations`
3. Run `python3 manage.py migrate`
4. Update views.py for new endpoints
5. Update templates for UI changes
6. Add URL patterns in urls.py
7. Write tests in tests.py
8. Run full validation workflow

### Debugging Issues
- Check Django server logs (visible when running `python3 manage.py runserver`)
- Use `python3 manage.py check` for configuration issues
- Check database with `python3 manage.py dbshell` if needed
- Verify URL patterns match in urls.py

### Before Committing
**ALWAYS run these commands in order:**
1. `python3 manage.py check` -- must show "no issues"
2. `flake8 . --exclude=migrations,venv,__pycache__` -- address any style issues
3. `python3 manage.py test` -- all tests must pass
4. Start server and manually test core functionality

## Technical Specifications Reference

- **Tech Stack**: Python 3.12+, Django 5.2+, HTML, CSS, JavaScript
- **Database**: SQLite (default Django database)
- **Models**: Game model (board state, players, status), Move model (move history)
- **Frontend**: Django templates with basic JavaScript for interactivity
- **API**: JSON endpoints for game state and moves
- **Deployment**: Local development only using `manage.py runserver`

## Important Notes

- Board state stored as 9-character string (e.g., "XOX O XO ")
- All game logic validation must be server-side
- Use AJAX or page reloads for move submissions
- No real-time WebSockets required for MVP
- Responsive design for desktop and mobile browsers
- Prevent cheating through server-side validation

The specifications are thoroughly documented in the .md files - reference them for detailed requirements, user stories, and UI wireframes.