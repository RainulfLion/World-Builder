import pygame
import os

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# UI Layout dimensions
TOP_BAR_HEIGHT = 40
RIGHT_PANEL_WIDTH = 250
BOTTOM_PANEL_HEIGHT = 150
LEFT_PANEL_WIDTH = 0  # Currently unused

# Map area dimensions (calculated)
MAP_AREA_LEFT = LEFT_PANEL_WIDTH
MAP_AREA_TOP = TOP_BAR_HEIGHT
MAP_AREA_WIDTH = SCREEN_WIDTH - LEFT_PANEL_WIDTH - RIGHT_PANEL_WIDTH
MAP_AREA_HEIGHT = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_PANEL_HEIGHT

# Colors
BG_COLOR = (30, 30, 30)
UI_PANEL_COLOR = (50, 50, 50)
UI_ALT_PANEL_COLOR = (40, 40, 40)
UI_BORDER_COLOR = (80, 80, 80)
UI_TEXT_COLOR = (255, 255, 255)
UI_BUTTON_COLOR = (100, 100, 100)
UI_BUTTON_HOVER_COLOR = (150, 150, 150)
UI_LIST_ITEM_COLOR = (70, 70, 70)
UI_LIST_HOVER_COLOR = (100, 100, 100)

# Grid settings
GRID_LINE_COLOR = (128, 128, 128)
GRID_OPACITY = 128
DEFAULT_GRID_SIZE = 50

# File paths
DATA_DIR = "data"
MAPS_DIR = os.path.join(DATA_DIR, "maps")
TOKENS_DIR = os.path.join(DATA_DIR, "tokens")
NOTES_DIR = os.path.join(DATA_DIR, "notes")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
DB_PATH = os.path.join(DATA_DIR, "game_data.db")

# Ensure directories exist
for directory in [DATA_DIR, MAPS_DIR, TOKENS_DIR, NOTES_DIR, AUDIO_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize pygame font system
pygame.font.init()

# Fonts
try:
    DEFAULT_FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 18)
    LARGE_FONT = pygame.font.Font(None, 32)
except:
    # Fallback if font loading fails
    DEFAULT_FONT = pygame.font.SysFont(None, 24)
    SMALL_FONT = pygame.font.SysFont(None, 18)
    LARGE_FONT = pygame.font.SysFont(None, 32)

# Token settings
DEFAULT_TOKEN_SIZE = 50
TOKEN_COLORS = {
    'player': (0, 255, 0),
    'enemy': (255, 0, 0),
    'npc': (255, 255, 0),
    'object': (128, 128, 128)
}

# Map settings
DEFAULT_MAP_SCALE = 1.0
MIN_MAP_SCALE = 0.25
MAX_MAP_SCALE = 4.0

# Animation settings
ANIMATION_SPEED = 2.0  # seconds for token movement
FADE_SPEED = 1.0  # seconds for UI fades

# Audio settings
ENABLE_AUDIO = True
DEFAULT_VOLUME = 0.7

# Debug settings
DEBUG_MODE = False
SHOW_FPS = False
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR