import os
import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from config import *

class MapCreator:
    """Standalone script or integrated UI for map creation."""
    
    def __init__(self, screen, database):
        """Initialize the map creator."""
        self.screen = screen
        self.db = database
        self.running = False
        self.map_image = None
        self.map_path = None
        self.map_name = ""
        self.map_width = 800
        self.map_height = 600
        self.grid_size = 50
        self.show_grid = True
        self.draw_mode = "none"  # none, wall, door, etc.
        self.wall_tiles = []
        self.door_tiles = []
        self.location_points = []  # [(x, y, name), ...]
        
        # Initialize UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.buttons = []
        self._setup_ui()

    def start(self):
        """Start the map creator."""
        pygame.init()  # Ensure pygame is initialized
        self.running = True
        self.run()

    def run(self):
        """Run the map creator loop."""
        while self.running:
            # Fill background
            self.screen.fill((40, 40, 40))
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if a button was clicked
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            btn["callback"]()
                            break
                    
                    # Handle drawing modes
                    if self.draw_mode == "wall" and self.map_image:
                        self._handle_wall_placement(mouse_pos)
                    elif self.draw_mode == "door" and self.map_image:
                        self._handle_door_placement(mouse_pos)
            
            # Draw everything
            self._draw()
            
            # Update display
            pygame.display.flip()
            pygame.time.Clock().tick(60)  # Limit to 60 FPS

def run_standalone():
    """Run the map creator as a standalone application."""
    import sqlite3
    from database import Database
    
    # Initialize pygame
    pygame.init()
    
    # Create screen with a reasonable default size
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Map Creator")
    
    # Create database connection
    db_path = os.path.join("data", "game_data.db")
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
        
    conn = sqlite3.connect(db_path)
    db = Database(conn)
    
    # Create and run map creator
    creator = MapCreator(screen, db)
    creator.start()
    
    # Clean up
    pygame.quit()

if __name__ == "__main__":
    run_standalone()
