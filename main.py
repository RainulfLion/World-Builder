# main.py - Complete fix with world creation and map loading
import pygame
import pygame_gui
from pygame_gui import elements, windows
import sys
import os
import uuid
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Audio imports
try:
    import pygame.mixer
    AUDIO_AVAILABLE = True
    print("Audio support enabled")
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio support not available")

# Local imports
import config
import database
import map_creator
import map_view
import timeline
import ui_manager
import dice_roller

# pygame_gui Theme
THEME_PATH = 'theme.json'

class GameApp:
    def __init__(self):
        pygame.init()
        
        # Initialize audio mixer if available
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_enabled = True
                print("Audio mixer initialized successfully")
            except pygame.error as e:
                print(f"Could not initialize audio mixer: {e}")
                self.audio_enabled = False
        else:
            self.audio_enabled = False
            
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("TTS RPG App")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False

        # Initialize pygame_gui Manager
        try:
            script_dir = os.path.dirname(__file__)
            theme_path = os.path.join(script_dir, 'theme.json')
            print(f"DEBUG: Loading theme from: {theme_path}")
            self.gui_manager = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), theme_path)
        except FileNotFoundError:
            print(f"WARNING: Theme file not found at '{theme_path}'. Using default theme.")
            self.gui_manager = pygame_gui.UIManager((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Initialize Database
        self.db = database.Database()

        # Game State
        self.current_map_id = None
        self.current_world_id = None
        self.tokens = []
        self.waiting_for_map_creator = False
        self.initial_map_list = []
        self.frame_count = 0

        # Debug flags/state
        self.map_creator_open = False

        # Audio state
        self.current_audio = None
        self.audio_files = {}

        # Core Components
        self.timeline = timeline.Timeline(self.db)
        self.map_view = map_view.MapView(self)
        self.reset_map_creator_state()

        self.ui_manager = ui_manager.UIManager(self)
        self.dice_roller = dice_roller.DiceRoller()

        # UI State Management
        self.world_name_to_id_map = {}
        self.map_name_to_id_map = {}
        self.world_selection_list = None
        self.map_selection_list = None
        self.delete_world_selection_list = None
        self.pending_world_creation_data = None
        self.pending_world_deletion_id = None
        self.pending_ui_action = None

        # Application Mode State
        self.app_mode = "GAME"

        # Data for current view
        self.tokens_on_map = []
        self.notes_on_map = []
        self.locations_on_map = []
        self.selected_token_instance_id = None

        # Initialize map creator process
        self.map_creator_process = None

        # Load initial state
        self.load_initial_state()

    def get_creator_grid_color(self):
        """Get current grid color safely."""
        color_val = self.map_creator_state['grid_settings'].get('grid_color', config.GRID_LINE_COLOR)
        try:
            return pygame.Color(color_val)
        except (ValueError, TypeError):
            return pygame.Color(config.GRID_LINE_COLOR)

    def process_ui_action(self, action):
        """Process UI actions safely between frames."""
        action_type = action.get('type')
        
        if not action_type:
            print("WARNING: Received action with no type")
            return
            
        print(f"Processing UI action: {action_type}")
        
        if action_type == 'open_map_selection':
            self.create_map_selection_window()
        elif action_type == 'menu_create_world':
            print("Create World menu item clicked")
            self.start_world_creation()
        elif action_type == 'menu_load_world':
            print("Load World menu item clicked")
            self.show_world_selection()
        elif action_type == 'menu_delete_world':
            print("Delete World menu item clicked")
            self.show_world_selection_for_deletion()
        elif action_type == 'creator_load_image':
            self.handle_creator_load_image()
        elif action_type == 'creator_save_map':
            self.handle_creator_save_map()
        elif action_type == 'creator_back_to_game':
            print("Switching back to GAME mode")
            self.app_mode = "GAME"
            self.ui_manager.switch_to_game_mode()
        elif action_type == 'menu_create_map':
            print("Switching to MAP_CREATOR mode")
            self.app_mode = "MAP_CREATOR"
            self.reset_map_creator_state()
            self.ui_manager.switch_to_creator_mode()
        elif action_type == 'toggle_fullscreen':
            self.toggle_fullscreen()
        elif action_type == 'roll_dice':
            self.handle_dice_roll(action.get('data', {}))
        elif action_type == 'select_dice_type':
            self.handle_dice_type_selection(action.get('data', {}))
        elif action_type == 'select_num_dice':
            self.handle_num_dice_selection(action.get('data', {}))
        elif action_type == 'menu_create_token':
            print("Create Token menu item clicked")
            self.show_message_box("Info", "Token creation feature coming soon!", ['OK'])
        elif action_type == 'menu_create_note':
            print("Create Note menu item clicked")
            self.show_message_box("Info", "Note creation feature coming soon!", ['OK'])
        elif action_type == 'menu_create_location':
            print("Create Location menu item clicked")
            if self.current_map_id:
                center_x = config.MAP_AREA_WIDTH // 2 // 50
                center_y = config.MAP_AREA_HEIGHT // 2 // 50
                self.create_location_with_notes(center_x, center_y, self.current_map_id)
            else:
                self.show_message_box("No Map", "Please load a world with a map first.", ['OK'])
        elif action_type == 'show_settings':
            print("Settings menu item clicked")
            self.show_message_box("Info", "Settings panel coming soon!", ['OK'])
        elif action_type == 'show_about':
            print("About menu item clicked")
            self.show_message_box("About", "TTS RPG App v2.0\nEnhanced Tabletop RPG Simulator", ['OK'])
        elif action_type == 'show_help':
            print("Help menu item clicked")
            self.show_message_box("Help", "Use File > Create World to get started!\nThen Tools > Create Map to add maps.", ['OK'])
        else:
            print(f"WARNING: Unknown action type: {action_type}")

    def handle_creator_load_image(self):
        """Load an image for the map creator."""
        print("Map Creator: Load Image button clicked.")
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("All files", "*.*")
        ]
        
        image_path = filedialog.askopenfilename(
            title="Select map image",
            filetypes=filetypes
        )
        
        root.destroy()
        
        if not image_path:
            print("No image selected.")
            return
            
        try:
            image_id = str(uuid.uuid4())
            os.makedirs("data/images", exist_ok=True)
            
            _, ext = os.path.splitext(image_path)
            new_image_path = f"data/images/{image_id}{ext}"
            shutil.copy2(image_path, new_image_path)
            
            self.map_creator_state["image_surface"] = pygame.image.load(new_image_path)
            self.map_creator_state["image_path"] = new_image_path
            self.map_creator_state["image_id"] = image_id
            
            print(f"Image loaded for creator: {image_id}{ext}")
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.show_error_message(f"Failed to load image: {e}")

    def handle_creator_save_map(self):
        """Save the current map being created."""
        print("Map Creator: Save Map button clicked.")
        
        state = self.map_creator_state
        
        if not state["image_surface"]:
            self.show_error_message("No image loaded. Please load an image first.")
            return
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        map_name = simpledialog.askstring(
            "Map Name",
            "Enter map name:",
            initialvalue=state["map_name"]
        )
        root.destroy()
        
        if not map_name or not map_name.strip():
            print("Save cancelled.")
            return
        
        map_name = map_name.strip()
        state["map_name"] = map_name
        
        original_width = state["image_surface"].get_width()
        original_height = state["image_surface"].get_height()
        
        grid_color_str = "#%02x%02x%02x" % self.get_creator_grid_color()[:3]
        
        map_data_to_save = {
            'name': map_name,
            'image_path': state["image_path"],
            'grid_size': state['grid_settings']['grid_size'],
            'grid_enabled': state['grid_settings']['grid_visible'],
            'width': original_width,
            'height': original_height,
            'grid_color': grid_color_str,
            'map_scale': state["preview_scale"],
            'grid_style': state['grid_settings']['grid_style'],
            'grid_opacity': state['grid_settings']['grid_opacity'],
        }
        
        try:
            saved_id = self.db.save_or_update_map(map_data_to_save)
            if saved_id is not None:
                self.show_message_box("Success", f"Map '{map_name}' saved successfully.")
                self.app_mode = "GAME"
                self.ui_manager.switch_to_game_mode()
            else:
                self.show_error_message("Failed to save map to database.")
        
        except Exception as e:
            print(f"ERROR saving map: {e}")
            self.show_error_message(f"Failed to save map: {e}")

    def handle_dice_roll(self, data):
        """Handle dice rolling."""
        dice_type = data.get('dice_type', 'D20')
        num_dice = data.get('num_dice', 1)
        
        sides = dice_type[1:]
        dice_string = f"{num_dice}d{sides}"
        
        result = self.dice_roller.roll(dice_string)
        self.ui_manager.update_dice_results(result)

    def handle_dice_type_selection(self, data):
        """Handle dice type selection."""
        self.ui_manager.selected_dice_type = data.get('dice_type', 'D20')
        self.ui_manager._update_dice_buttons()
        self.ui_manager._update_roll_button()

    def handle_num_dice_selection(self, data):
        """Handle number of dice selection."""
        self.ui_manager.num_dice = data.get('num_dice', 1)
        self.ui_manager._update_dice_buttons()
        self.ui_manager._update_roll_button()

    def handle_map_click(self, grid_coords):
        """Handle left-clicks on the map grid."""
        print(f"GameApp: Map clicked at grid coordinates: {grid_coords}")

    def reset_map_creator_state(self):
        """Reset the map creator state to default values."""
        self.map_creator_state = {
            "map_name": "Untitled Map",
            "image_path": None,
            "image_surface": None,
            "image_id": None,
            "walls": set(),
            "preview_scale": 1.0,
            "preview_offset_x": 0,
            "preview_offset_y": 0,
            "grid_settings": {
                "grid_size": 50,
                "grid_visible": True,
                "grid_opacity": 0.7,
                "grid_color": config.GRID_LINE_COLOR,
                "grid_style": "dashed"
            }
        }
        print("Map creator state reset.")

    def map_to_grid_coords(self, pos):
        """Convert mouse position to grid coordinates."""
        map_x = pos[0] - config.MAP_AREA_LEFT
        map_y = pos[1] - config.MAP_AREA_TOP
        
        scale = self.map_creator_state.get("preview_scale", 1.0)
        if scale != 1.0:
            map_x = map_x / scale
            map_y = map_y / scale
        
        grid_size = self.map_creator_state["grid_settings"]["grid_size"]
        grid_x = int(map_x / grid_size)
        grid_y = int(map_y / grid_size)
        
        return grid_x, grid_y

    def toggle_wall_at_grid(self, grid_x, grid_y):
        """Toggle a wall at the specified grid coordinates."""
        wall_pos = (grid_x, grid_y)
        if wall_pos in self.map_creator_state["walls"]:
            self.map_creator_state["walls"].remove(wall_pos)
        else:
            self.map_creator_state["walls"].add(wall_pos)

    def draw_map_creator_preview(self):
        """Draw the map creator preview area."""
        preview_rect = pygame.Rect(
            config.MAP_AREA_LEFT, config.MAP_AREA_TOP,
            config.MAP_AREA_WIDTH, config.MAP_AREA_HEIGHT
        )

        pygame.draw.rect(self.screen, (30, 30, 30), preview_rect)
        pygame.draw.rect(self.screen, config.UI_BORDER_COLOR, preview_rect, 1)

        preview_surface = self.screen.subsurface(preview_rect)

        state = self.map_creator_state
        image_surface = state["image_surface"]

        if image_surface:
            try:
                original_w = image_surface.get_width()
                original_h = image_surface.get_height()
                scaled_w = max(1, int(original_w * state["preview_scale"]))
                scaled_h = max(1, int(original_h * state["preview_scale"]))

                display_surface = pygame.transform.smoothscale(image_surface, (scaled_w, scaled_h))

                blit_x = state["preview_offset_x"]
                blit_y = state["preview_offset_y"]

                preview_surface.blit(display_surface, (blit_x, blit_y))

                self.draw_creator_grid(preview_surface, display_surface.get_rect(topleft=(blit_x, blit_y)))

            except pygame.error as e:
                print(f"Error scaling/drawing preview image: {e}")
                font = config.DEFAULT_FONT
                err_surf = font.render("Error displaying image", True, (255,0,0))
                preview_surface.blit(err_surf, (10,10))

        else:
            font = config.DEFAULT_FONT
            text_surf = font.render("Click 'Load Image' to start", True, config.UI_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=preview_surface.get_rect().center)
            preview_surface.blit(text_surf, text_rect)

    def draw_creator_grid(self, target_surface, image_rect):
        """Draw the grid overlay on the preview surface."""
        state = self.map_creator_state
        settings = state["grid_settings"]

        if not settings['grid_visible']:
            return

        grid_size = settings['grid_size']
        scale = state["preview_scale"]
        grid_color = self.get_creator_grid_color()

        display_grid_size = grid_size * scale
        if display_grid_size < 2:
            return

        start_x = image_rect.left
        start_y = image_rect.top
        end_x = image_rect.right
        end_y = image_rect.bottom

        # Draw vertical grid lines
        current_x = start_x + (display_grid_size - (start_x % display_grid_size)) % display_grid_size
        while current_x < end_x:
            draw_y1 = max(start_y, 0)
            draw_y2 = min(end_y, target_surface.get_height())
            draw_x_clipped = int(current_x)

            if 0 <= draw_x_clipped <= target_surface.get_width():
                pygame.draw.line(target_surface, grid_color, (draw_x_clipped, draw_y1), (draw_x_clipped, draw_y2))
            current_x += display_grid_size

        # Draw horizontal grid lines
        current_y = start_y + (display_grid_size - (start_y % display_grid_size)) % display_grid_size
        while current_y < end_y:
            draw_x1 = max(start_x, 0)
            draw_x2 = min(end_x, target_surface.get_width())
            draw_y_clipped = int(current_y)

            if 0 <= draw_y_clipped <= target_surface.get_height():
                pygame.draw.line(target_surface, grid_color, (draw_x1, draw_y_clipped), (draw_x2, draw_y_clipped))
            current_y += display_grid_size

    def draw(self):
        """Draws everything based on the current app_mode."""
        self.screen.fill(config.BG_COLOR)

        if self.app_mode == "GAME":
            self.map_view.draw(self.screen, self.tokens_on_map, self.notes_on_map, self.locations_on_map, self.selected_token_instance_id)
            self.ui_manager.draw(self.screen)

        elif self.app_mode == "MAP_CREATOR":
            self.ui_manager.draw(self.screen)
            self.draw_map_creator_preview()

        # Draw pygame_gui elements
        self.gui_manager.draw_ui(self.screen)

        pygame.display.flip()

    def load_initial_state(self):
        print("App started. Select File > Create World or File > Load World.")

    def update(self, time_delta):
        """Update game state and UI."""
        if self.pending_ui_action:
            action = self.pending_ui_action
            self.pending_ui_action = None
            
            try:
                self.process_ui_action(action)
            except Exception as e:
                print(f"ERROR: Failed to execute UI action {action}: {e}")
                import traceback
                traceback.print_exc()
                self.show_error_message(f"Action failed: {str(e)}")

        self.gui_manager.update(time_delta)

        if self.app_mode == "GAME":
            self.map_view.update(time_delta)
            self.timeline.update(time_delta)

    def run(self):
        """Main game loop."""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            try:
                self.process_events()
                self.update(time_delta)
                self.draw()
            except Exception as e:
                print(f"Error in main game loop: {e}")
                import traceback
                traceback.print_exc()

        self.cleanup()

    def process_events(self):
        """Process all events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event detected.")
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.app_mode == "GAME":
                        print("ESC key pressed, showing menu.")
                        self.show_main_menu()
                    else:
                        print("ESC key pressed, returning to game.")
                        self.hide_main_menu()
            
            event_consumed = self.gui_manager.process_events(event)
            
            if not event_consumed:
                action = self.ui_manager.process_event(event)
                if action:
                    self.pending_ui_action = action
            
            # Handle pygame_gui UI events
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                obj_id = event.ui_object_id
                print(f"Button pressed: {obj_id}")
                
                # World creation buttons
                if obj_id == '#confirm_world_name_button':
                    print("DEBUG: Confirm world name button detected - calling handler")
                    self.handle_confirm_world_name()
                    
                elif obj_id == '#confirm_map_for_world_button':
                    print("DEBUG: Map selection confirm button pressed")
                    if hasattr(self, 'map_selection_list') and self.map_selection_list:
                        try:
                            selected_items = self.map_selection_list.get_single_selection()
                            print(f"DEBUG: Selected items: {selected_items}")
                            if selected_items:
                                map_name = selected_items
                                print(f"DEBUG: Selected map name: {map_name}")
                                self.handle_map_selection(map_name)
                            else:
                                print("DEBUG: No map selected, proceeding without map")
                                self.handle_map_selection(None)
                        except Exception as e:
                            print(f"ERROR: Exception in map selection: {e}")
                            import traceback
                            traceback.print_exc()
                            self.show_message_box("Error", f"Map selection error: {str(e)}", ['OK'])
                    else:
                        print("DEBUG: No map selection list found, proceeding without map")
                        self.handle_map_selection(None)
                
                elif obj_id == '#cancel_create_world_button':
                    print("DEBUG: Cancel world creation button pressed")
                    self.pending_world_creation_data = None
                    
                    # Close any related windows
                    for window_id in ['#create_world_name_window', '#create_world_map_window']:
                        try:
                            window = self.gui_manager.find_window_by_object_id(window_id)
                            if window:
                                window.kill()
                                print(f"DEBUG: Closed window {window_id}")
                        except:
                            pass
                
                # World selection buttons
                elif obj_id == '#confirm_world_selection_button':
                    print("DEBUG: Confirm world selection button pressed")
                    if hasattr(self, 'world_selection_list') and self.world_selection_list:
                        try:
                            selected_items = self.world_selection_list.get_single_selection()
                            if selected_items:
                                world_name = selected_items
                                world_id = self.world_name_to_id_map.get(world_name)
                                if world_id:
                                    print(f"DEBUG: Loading world {world_name} (ID: {world_id})...")
                                    # Close the selection window first
                                    world_select_window = self.gui_manager.find_window_by_object_id('#world_selection_window')
                                    if world_select_window:
                                        world_select_window.kill()
                                    self.load_world(world_id)
                                else:
                                    print(f"ERROR: Could not find ID for world: {world_name}")
                            else:
                                print("WARNING: No world selected")
                        except Exception as e:
                            print(f"ERROR: Exception in world selection: {e}")
                            self.show_message_box("Error", f"World selection error: {str(e)}", ['OK'])
                    else:
                        print("ERROR: No world selection list found")
                
                elif obj_id == '#cancel_world_selection_button':
                    print("DEBUG: Cancel world selection button pressed")
                    try:
                        window = self.gui_manager.find_window_by_object_id('#world_selection_window')
                        if window:
                            window.kill()
                    except:
                        pass
            
            if self.app_mode == "GAME" and not event_consumed:
                self.map_view.handle_event(event)

    def start_world_creation(self):
        """Starts the world creation process with a name entry dialog."""
        self.pending_world_creation_data = {
            'stage': 'enter_name',
            'world_name': '',
            'description': '',
            'selected_map_id': None
        }
        
        print(f"Starting world creation. Stage: {self.pending_world_creation_data['stage']}")
        self.create_world_name_entry_window()
    
    def create_world_name_entry_window(self):
        """Creates the name entry window for world creation."""
        window_width, window_height = 300, 180
        window_x = (config.SCREEN_WIDTH - window_width) // 2
        window_y = (config.SCREEN_HEIGHT - window_height) // 2
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        name_window = elements.UIWindow(
            rect=window_rect,
            manager=self.gui_manager,
            window_display_title="Create World - Step 1: Enter Name",
            object_id='#create_world_name_window'
        )
        
        elements.UILabel(
            relative_rect=pygame.Rect(10, 10, window_width - 20, 30),
            text="Enter a name for your new world:",
            manager=self.gui_manager,
            container=name_window
        )
        
        elements.UITextEntryLine(
            relative_rect=pygame.Rect(10, 50, window_width - 20, 40),
            manager=self.gui_manager,
            container=name_window,
            object_id='#world_name_input'
        )
        
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 210, window_height - 60, 100, 30),
            text='Confirm',
            manager=self.gui_manager,
            container=name_window,
            object_id='#confirm_world_name_button'
        )
        
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 100, window_height - 60, 90, 30),
            text='Cancel',
            manager=self.gui_manager,
            container=name_window,
            object_id='#cancel_create_world_button'
        )

def create_map_selection_window(self):
    """Creates the UI window for selecting an initial map for a new world."""
    print("DEBUG: Creating map selection window...")
    
    # Get UNASSIGNED maps only for world creation
    try:
        # First check total maps
        all_maps = self.db.get_all_maps()
        print(f"DEBUG: Found {len(all_maps)} total maps in database")
        
        # Then get unassigned maps
        unassigned_maps = self.db.get_unassigned_maps()
        print(f"DEBUG: Found {len(unassigned_maps)} unassigned maps")
        
        # If no unassigned maps, show all maps as options
        maps_to_show = unassigned_maps if unassigned_maps else all_maps
        
        self.map_name_to_id_map = {name: map_id for map_id, name in maps_to_show}
        map_list_items = [m[1] for m in maps_to_show]  # Just the names
        
        print(f"DEBUG: Showing {len(map_list_items)} maps: {map_list_items}")
        
    except Exception as e:
        print(f"ERROR: Could not load maps from database: {e}")
        import traceback
        traceback.print_exc()
        self.show_message_box("Error", f"Could not load maps: {str(e)}", ['OK'])
        return

    window_width = 350
    # Show message if no maps available
    if not map_list_items:
        window_height = 200
        message_text = "No maps available. You can:\n1. Skip this step and create maps later\n2. Use Tools > Create Map first"
    else:
        window_height = min(len(map_list_items) * 35 + 120, 400)
        message_text = "Select a map to be the starting map for this world:"
        
    window_x = (config.SCREEN_WIDTH - window_width) // 2
    window_y = (config.SCREEN_HEIGHT - window_height) // 2
    window_rect = pygame.Rect(window_x, window_y, window_width, window_height)

    try:
        map_selection_window = elements.UIWindow(
            rect=window_rect,
            manager=self.gui_manager,
            window_display_title="Create World - Step 2: Select Initial Map",
            object_id='#create_world_map_window'
        )
        print("DEBUG: Map selection window created successfully")

        # Instruction text
        elements.UILabel(
            relative_rect=pygame.Rect(10, 10, window_width - 20, 30),
            text=message_text,
            manager=self.gui_manager,
            container=map_selection_window
        )

        if map_list_items:
            # Selection List for Maps
            self.map_selection_list = elements.UISelectionList(
                relative_rect=pygame.Rect(10, 45, window_width - 20, window_height - 125),
                item_list=map_list_items,
                manager=self.gui_manager,
                container=map_selection_window,
                object_id='#map_selection_list_for_creation',
                allow_double_clicks=False
            )
            print("DEBUG: Map selection list created with items")
            button_text = 'Confirm Map'
        else:
            # No maps available - show instruction
            elements.UILabel(
                relative_rect=pygame.Rect(10, 45, window_width - 20, window_height - 125),
                text="Create maps using Tools > Create Map, then try creating a world again.",
                manager=self.gui_manager,
                container=map_selection_window
            )
            button_text = 'Skip (No Map)'

        # Confirm Map Button
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 220, window_height - 65, 100, 30),
            text=button_text,
            manager=self.gui_manager,
            container=map_selection_window,
            object_id='#confirm_map_for_world_button'
        )
        
        # Cancel Button
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 110, window_height - 65, 100, 30),
            text='Cancel',
            manager=self.gui_manager,
            container=map_selection_window,
            object_id='#cancel_create_world_button'
        )
        
        print("DEBUG: Map selection window setup complete")
        
    except Exception as e:
        print(f"ERROR: Could not create map selection window UI: {e}")
        import traceback
        traceback.print_exc()
        self.show_message_box("Error", f"UI Error: {str(e)}", ['OK'])

# Also add this debug function to check database state
def debug_database_contents(self):
    """Debug function to check what's in the database."""
    print("\n=== DATABASE DEBUG INFO ===")
    
    try:
        # Check worlds
        worlds = self.db.get_all_worlds()
        print(f"Worlds in database: {len(worlds)}")
        for world in worlds:
            print(f"  World: ID={world['id']}, Name='{world['name']}'")
        
        # Check all maps
        all_maps = self.db.get_all_maps()
        print(f"Total maps in database: {len(all_maps)}")
        for map_data in all_maps:
            print(f"  Map: ID={map_data[0]}, Name='{map_data[1]}', Path='{map_data[2]}'")
            
        # Check unassigned maps
        unassigned = self.db.get_unassigned_maps()
        print(f"Unassigned maps: {len(unassigned)}")
        for map_data in unassigned:
            print(f"  Unassigned: ID={map_data[0]}, Name='{map_data[1]}'")
            
    except Exception as e:
        print(f"ERROR checking database: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== END DATABASE DEBUG ===\n")
    def debug_ui_elements(self):
        """Debug method to list all current UI elements."""
        print("DEBUG: Current UI elements:")
        root_container = self.gui_manager.get_root_container()
        if hasattr(root_container, 'elements'):
            for i, element in enumerate(root_container.elements):
                element_type = type(element).__name__
                element_id = getattr(element, 'object_id', 'No ID')
                print(f"  {i}: {element_type} - {element_id}")
        else:
            print("  No elements found or no elements attribute")

    def handle_confirm_world_name(self):
        """Handle the confirmation of world name entry."""
        print("DEBUG: handle_confirm_world_name called")
        
        # Debug: List all current UI elements
        self.debug_ui_elements()
        
        # Find the text input element by searching through all UI elements
        name_input_element = None
        name_window = None
        
        # Search through UI manager's elements
        root_container = self.gui_manager.get_root_container()
        for element in root_container.elements:
            element_id = getattr(element, 'object_id', None)
            element_type = type(element).__name__
            print(f"DEBUG: Checking element: {element_type} with ID: {element_id}")
            
            if element_id == '#world_name_input':
                name_input_element = element
                print("DEBUG: Found name input element!")
            elif element_id == '#create_world_name_window':
                name_window = element
                print("DEBUG: Found name window!")
        
        # Alternative search - look for text entry elements
        if not name_input_element:
            print("DEBUG: Searching for UITextEntryLine elements...")
            for element in root_container.elements:
                if hasattr(element, 'get_text') and 'TextEntry' in type(element).__name__:
                    print(f"DEBUG: Found text entry element: {type(element).__name__}")
                    name_input_element = element
                    break
        
        if not name_input_element:
            print("ERROR: Could not find name input element")
            self.show_message_box("Debug Info", "Could not find text input field. Check console for debug info.", ['OK'])
            return False
        
        if not name_window:
            print("WARNING: Could not find name window, but continuing...")
        
        # Get and validate the entered name
        try:
            world_name = name_input_element.get_text().strip()
            print(f"DEBUG: Got world name: '{world_name}'")
        except Exception as e:
            print(f"ERROR: Could not get text from input: {e}")
            print(f"DEBUG: Input element type: {type(name_input_element).__name__}")
            print(f"DEBUG: Input element methods: {[method for method in dir(name_input_element) if not method.startswith('_')]}")
            self.show_message_box("Error", f"Could not read world name: {str(e)}", ['OK'])
            return False
        
        if not world_name:
            print("ERROR: World name is empty")
            self.show_message_box("Error", "World name cannot be empty", ['OK'])
            return False
        
        # Check if name already exists in database
        try:
            if self.db.world_name_exists(world_name):
                print(f"ERROR: World name '{world_name}' already exists")
                self.show_message_box("Error", f"A world named '{world_name}' already exists", ['OK'])
                return False
        except Exception as e:
            print(f"ERROR: Database error checking world name: {e}")
            self.show_message_box("Error", f"Database error: {str(e)}", ['OK'])
            return False
        
        # Update creation state
        if not self.pending_world_creation_data:
            print("ERROR: No pending world creation data")
            self.show_message_box("Error", "World creation data lost", ['OK'])
            return False
            
        self.pending_world_creation_data['world_name'] = world_name
        self.pending_world_creation_data['stage'] = 'select_map'
        
        print(f"SUCCESS: World name confirmed: {world_name}")
        
        # Close the name window
        if name_window:
            name_window.kill()
            print("DEBUG: Name window closed")
        else:
            # Try to find and close any window with the right ID
            for element in root_container.elements:
                if hasattr(element, 'object_id') and element.object_id == '#create_world_name_window':
                    element.kill()
                    print("DEBUG: Found and closed name window by alternative method")
                    break
        
        # Small delay to ensure window is closed before opening next one
        pygame.time.wait(100)
        
        # Open map selection window
        try:
            self.create_map_selection_window()
            print("DEBUG: Map selection window created")
        except Exception as e:
            print(f"ERROR: Could not create map selection window: {e}")
            import traceback
            traceback.print_exc()
            self.show_message_box("Error", f"Could not open map selection: {str(e)}", ['OK'])
            return False
            
        return True

    def handle_map_selection(self, selected_map_name=None):
        """Handle the map selection or skipping step."""
        # If a map was selected, get its ID
        if selected_map_name:
            map_id = self.map_name_to_id_map.get(selected_map_name)
            if not map_id:
                print(f"ERROR: Could not find map ID for '{selected_map_name}'")
                self.show_error_message(f"Could not find map: {selected_map_name}")
                return False
                
            self.pending_world_creation_data['selected_map_id'] = map_id
            print(f"Selected map: {selected_map_name} (ID: {map_id})")
        else:
            # User skipped map selection or no map was selected
            self.pending_world_creation_data['selected_map_id'] = None
            print("No map selected for world")
        
        # Final step: Create the world in the database
        try:
            world_id = self.db.create_world(
                name=self.pending_world_creation_data['world_name'],
                description=self.pending_world_creation_data.get('description', ''),
                active_map_id=self.pending_world_creation_data['selected_map_id']
            )
            
            if world_id:
                print(f"World created successfully with ID: {world_id}")
                
                # Load the newly created world
                world_data = self.db.load_world(world_id)
                if world_data:
                    self.current_world_id = world_id
                    print(f"Loading world: {world_data['name']}")
                    
                    # Set up timeline for this world
                    self.timeline.set_world(world_id)
                    
                    # If there's an active map, load it
                    if 'active_map' in world_data and world_data['active_map']:
                        print(f"Loading active map: {world_data['active_map']['name']}")
                        self.current_map_id = world_data['active_map']['id']
                        self.map_view.load_map_data(world_data['active_map'])
                        
                        # Set up timeline for this map too
                        self.timeline.set_map(self.current_map_id)
                        
                        # Load tokens and locations on this map
                        self.load_map_tokens()
                        self.load_map_locations()
                    else:
                        print("No active map found for this world")
                        self.current_map_id = None
                    
                    # Update UI to reflect loaded world
                    pygame.display.set_caption(f"TTS RPG App - {world_data['name']}")
                    self.show_message_box("Success", f"World '{self.pending_world_creation_data['world_name']}' created and loaded successfully!", ['OK'])
                    
                    # Hide main menu if it was open
                    if self.app_mode == "MENU":
                        self.hide_main_menu()
                        
                else:
                    self.show_message_box("Warning", f"World created but could not be loaded. Try loading it manually.", ['OK'])
            else:
                # Database error
                self.show_message_box("Error", "Failed to create world due to a database error.", ['OK'])
                
            # Reset creation state
            self.pending_world_creation_data = None
            
            # Close map selection window if it exists
            map_window = self.gui_manager.find_window_by_object_id('#create_world_map_window')
            if map_window:
                map_window.kill()
                
            return world_id is not None
                
        except Exception as e:
            print(f"ERROR in handle_map_selection: {e}")
            import traceback
            traceback.print_exc()
            self.show_message_box("Error", f"Failed to create world: {str(e)}", ['OK'])
            return False

    def load_map_tokens(self):
        """Load tokens for the current map."""
        if not self.current_map_id:
            self.tokens_on_map = []
            return
            
        try:
            # Get tokens from database
            token_data = self.db.get_map_tokens_with_history(self.current_map_id)
            
            # Convert database format to our internal format
            self.tokens_on_map = []
            for token in token_data:
                if len(token) >= 13:  # Ensure we have all the data we expect
                    token_dict = {
                        'map_token_id': token[0],
                        'token_id': token[1],
                        'name': token[2],
                        'image_path': token[3],
                        'size': token[4],
                        'color': token[5],
                        'type': token[6],
                        'x': token[7],
                        'y': token[8],
                        'rotation': token[9],
                        'active': token[10],
                        'initiative': token[11],
                        'has_moved': token[12],
                        'current_hp': token[13] if len(token) > 13 else 10,
                        'max_hp': token[14] if len(token) > 14 else 10
                    }
                    self.tokens_on_map.append(token_dict)
            
            print(f"Loaded {len(self.tokens_on_map)} tokens for map ID {self.current_map_id}")
            
            # Update UI token list
            self.ui_manager.update_token_list(self.tokens_on_map)
            
        except Exception as e:
            print(f"Error loading map tokens: {e}")
            self.tokens_on_map = []

    def load_map_locations(self):
        """Load location icons for the current map."""
        if not self.current_map_id:
            self.locations_on_map = []
            return
            
        try:
            locations = self.db.get_location_icons(self.current_map_id)
            self.locations_on_map = []
            
            for loc in locations:
                location_dict = {
                    'id': loc[0],
                    'x': loc[1],
                    'y': loc[2],
                    'name': loc[3],
                    'type': loc[4],
                    'sub_map_id': loc[5],
                    'notes': loc[6],
                    'audio_file': loc[7],
                    'icon_path': loc[8]
                }
                self.locations_on_map.append(location_dict)
            
            print(f"Loaded {len(self.locations_on_map)} locations for map")
            
        except Exception as e:
            print(f"Error loading map locations: {e}")
            self.locations_on_map = []

    def show_world_selection(self):
        """Shows a window for selecting a world to load."""
        worlds = self.db.get_worlds_simple()
        self.world_name_to_id_map = {name: world_id for world_id, name in worlds}
        world_names = [w[1] for w in worlds]
        
        if not world_names:
            self.show_message_box("No Worlds", "No worlds available to load. Create a world first.", ['OK'])
            return
        
        window_width = 350
        window_height = min(len(world_names) * 35 + 100, 400)
        window_x = (config.SCREEN_WIDTH - window_width) // 2
        window_y = (config.SCREEN_HEIGHT - window_height) // 2
        window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
        
        world_selection_window = elements.UIWindow(
            rect=window_rect,
            manager=self.gui_manager,
            window_display_title="Load World",
            object_id='#world_selection_window'
        )
        
        # Selection List for Worlds
        self.world_selection_list = elements.UISelectionList(
            relative_rect=pygame.Rect(10, 10, window_width - 40, window_height - 80),
            item_list=world_names,
            manager=self.gui_manager,
            container=world_selection_window,
            object_id='#world_selection_list',
            allow_double_clicks=False
        )
        
        # Confirm Button
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 220, window_height - 65, 100, 30),
            text='Load World',
            manager=self.gui_manager,
            container=world_selection_window,
            object_id='#confirm_world_selection_button'
        )
        
        # Cancel Button
        elements.UIButton(
            relative_rect=pygame.Rect(window_width - 110, window_height - 65, 100, 30),
            text='Cancel',
            manager=self.gui_manager,
            container=world_selection_window,
            object_id='#cancel_world_selection_button'
        )

    def load_world(self, world_id):
        """Load a world by ID and its associated maps."""
        try:
            print(f"Loading world ID: {world_id}")
            world_data = self.db.load_world(world_id)
            
            if not world_data:
                print(f"ERROR: Could not load world ID {world_id}")
                self.show_message_box("Error", f"Failed to load world (ID: {world_id})", ['OK'])
                return False
            
            self.current_world_id = world_id
            print(f"World loaded: {world_data['name']} (ID: {world_id})")
            
            # Set up timeline for this world
            self.timeline.set_world(world_id)
            
            if 'active_map' in world_data and world_data['active_map']:
                print(f"Loading active map: {world_data['active_map']['name']}")
                self.current_map_id = world_data['active_map']['id']
                self.map_view.load_map_data(world_data['active_map'])
                
                # Set up timeline for this map
                self.timeline.set_map(self.current_map_id)
                
                # Load tokens and locations on this map
                self.load_map_tokens()
                self.load_map_locations()
            else:
                print("No active map found for this world")
                self.current_map_id = None
                self.tokens_on_map = []
                self.locations_on_map = []
            
            pygame.display.set_caption(f"TTS RPG App - {world_data['name']}")
            
            if self.app_mode == "MENU":
                self.hide_main_menu()
            
            return True
            
        except Exception as e:
            print(f"ERROR loading world: {e}")
            import traceback
            traceback.print_exc()
            self.show_message_box("Error", f"Failed to load world: {str(e)}", ['OK'])
            return False

    # Audio Methods
    def play_audio_file(self, file_path, volume=0.7):
        """Play an audio file."""
        if not self.audio_enabled:
            print("Audio not available")
            return False
            
        try:
            self.stop_audio()
            
            if not os.path.exists(file_path):
                print(f"Audio file not found: {file_path}")
                return False
            
            if file_path not in self.audio_files:
                print(f"Loading audio file: {file_path}")
                self.audio_files[file_path] = pygame.mixer.Sound(file_path)
            
            self.current_audio = self.audio_files[file_path]
            self.current_audio.set_volume(volume)
            self.current_audio.play()
            print(f"Playing audio: {os.path.basename(file_path)}")
            return True
            
        except pygame.error as e:
            print(f"Error playing audio file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error playing audio: {e}")
            return False
    
    def stop_audio(self):
        """Stop currently playing audio."""
        if self.audio_enabled and self.current_audio:
            try:
                self.current_audio.stop()
                print("Audio stopped")
            except:
                pass
        self.current_audio = None

    def create_location_with_notes(self, x, y, map_id):
        """Create a location icon with notes and optional audio."""
        if not map_id:
            print("No map selected for location creation")
            return
            
        # Simple dialog for location creation
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # Get location name
        location_name = simpledialog.askstring(
            "Create Location",
            "Enter location name:",
            initialvalue="New Location"
        )
        
        if not location_name:
            root.destroy()
            return
            
        # Get location type
        location_types = ["generic", "city", "inn", "dungeon", "forest", "mountain", "castle", "village"]
        
        # Simple selection dialog
        type_dialog = tk.Toplevel()
        type_dialog.title("Location Type")
        type_dialog.geometry("200x300")
        type_dialog.transient(root)
        type_dialog.grab_set()
        
        selected_type = tk.StringVar(value="generic")
        
        tk.Label(type_dialog, text="Select location type:").pack(pady=10)
        
        for loc_type in location_types:
            tk.Radiobutton(
                type_dialog,
                text=loc_type.capitalize(),
                variable=selected_type,
                value=loc_type
            ).pack(anchor=tk.W, padx=20)
        
        result = {"type": "generic", "audio": None, "notes": ""}
        
        def on_ok():
            result["type"] = selected_type.get()
            type_dialog.destroy()
        
        def on_audio():
            audio_file = self.record_audio_note(location_name)
            if audio_file:
                result["audio"] = audio_file
                audio_btn.config(text="Audio: Selected")
        
        def on_notes():
            notes = simpledialog.askstring(
                "Location Notes",
                f"Enter notes for {location_name}:",
                initialvalue=""
            )
            if notes:
                result["notes"] = notes
                notes_btn.config(text="Notes: Added")
        
        # Buttons
        button_frame = tk.Frame(type_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        audio_btn = tk.Button(button_frame, text="Add Audio", command=on_audio)
        audio_btn.pack(side=tk.LEFT, padx=5)
        
        notes_btn = tk.Button(button_frame, text="Add Notes", command=on_notes)
        notes_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.RIGHT, padx=5)
        
        root.wait_window(type_dialog)
        root.destroy()
        
        # Create location in database
        try:
            location_id = self.db.add_location_icon(
                map_id, x, y, location_name, 
                result["type"], None, result["notes"], result["audio"]
            )
            
            if location_id:
                print(f"Location '{location_name}' created at ({x}, {y})")
                
                # Add timeline event
                if hasattr(self, 'timeline'):
                    self.timeline.log_location_discovered(location_name, result["type"])
                
                # Reload locations for display
                self.load_map_locations()
                
                return location_id
            else:
                self.show_error_message("Failed to create location")
                
        except Exception as e:
            print(f"Error creating location: {e}")
            self.show_error_message(f"Failed to create location: {e}")
        
        return None

    def record_audio_note(self, location_name=""):
        """Open a dialog to record an audio note."""
        if not self.audio_enabled:
            self.show_message_box("Audio Not Available", "Audio recording requires pygame mixer support.", ['OK'])
            return None
            
        # For now, show a file picker to select existing audio
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a"),
            ("All files", "*.*")
        ]
        
        audio_path = filedialog.askopenfilename(
            title=f"Select audio file for {location_name}" if location_name else "Select audio file",
            filetypes=filetypes
        )
        
        root.destroy()
        
        if audio_path and os.path.exists(audio_path):
            try:
                os.makedirs(config.AUDIO_DIR, exist_ok=True)
                audio_id = str(uuid.uuid4())
                _, ext = os.path.splitext(audio_path)
                new_audio_path = os.path.join(config.AUDIO_DIR, f"{audio_id}{ext}")
                shutil.copy2(audio_path, new_audio_path)
                print(f"Audio file copied to: {new_audio_path}")
                return new_audio_path
            except Exception as e:
                print(f"Error copying audio file: {e}")
                self.show_error_message(f"Failed to copy audio file: {e}")
                return None
        
        return None

    def show_main_menu(self):
        """Show the main menu with game options."""
        self.app_mode = "MENU"
        
        menu_width = 300
        menu_height = 350
        menu_x = (config.SCREEN_WIDTH - menu_width) // 2
        menu_y = (config.SCREEN_HEIGHT - menu_height) // 2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        self.menu_panel = elements.UIPanel(
            relative_rect=menu_rect,
            manager=self.gui_manager,
            object_id='#menu_panel'
        )
        
        print("Main menu shown.")

    def hide_main_menu(self):
        """Hide the main menu and return to game view."""
        if self.app_mode == "MENU":
            if hasattr(self, 'menu_panel') and self.menu_panel:
                self.menu_panel.kill()
                self.menu_panel = None
            
            self.app_mode = "GAME"
            print("Returned to game mode.")

    def show_message_box(self, title, message, buttons=None):
        """Show a message box to the user."""
        try:
            message_rect = pygame.Rect(0, 0, 350, 150)
            message_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            
            windows.UIMessageWindow(
                rect=message_rect,
                html_message=message,
                manager=self.gui_manager,
                window_title=title
            )
            return True
        except Exception as e:
            print(f"ERROR creating message box: {e}")
            return False

    def show_error_message(self, error_text):
        """Show an error message dialog to the user."""
        try:
            error_rect = pygame.Rect(0, 0, 350, 150)
            error_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            windows.UIMessageWindow(
                rect=error_rect,
                html_message=f"<font color='#FF0000'>{error_text}</font>",
                manager=self.gui_manager,
                window_title="Error"
            )
            return True
        except Exception as e:
            print(f"ERROR showing error message: {e}")
            print(f"Original error: {error_text}")
            return False

    def show_message_box(self, title, message, buttons=None):
        """Show a message box to the user."""
        try:
            message_rect = pygame.Rect(0, 0, 350, 150)
            message_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            windows.UIMessageWindow(
                rect=message_rect,
                html_message=message,
                manager=self.gui_manager,
                window_title=title
            )
            return True
        except Exception as e:
            print(f"ERROR creating message box: {e}")
            return False

    def stop_audio(self):
        """Stop currently playing audio."""
        if hasattr(self, 'audio_enabled') and self.audio_enabled and hasattr(self, 'current_audio') and self.current_audio:
            try:
                self.current_audio.stop()
                print("Audio stopped")
            except:
                pass
            self.current_audio = None

    def cleanup(self):
        """Clean up resources before exiting."""
        print("Cleaning up resources...")
        # Stop any playing audio
        if hasattr(self, 'audio_enabled') and self.audio_enabled:
            self.stop_audio()
            try:
                pygame.mixer.quit()
                print("Audio mixer closed")
            except:
                pass
        print("Closing database connection...")
        if hasattr(self, 'db') and self.db:
            self.db.close()
        # Terminate any subprocesses
        if hasattr(self, 'map_creator_process') and self.map_creator_process:
            if self.map_creator_process.poll() is None:
                print("Terminating map creator process...")
                self.map_creator_process.terminate()
                try:
                    self.map_creator_process.wait(timeout=2)
                    print("Map creator process terminated.")
                except subprocess.TimeoutExpired:
                    print("Map creator process did not terminate quickly, killing...")
                    self.map_creator_process.kill()
        print("Exiting Pygame.")
        pygame.quit()

    def debug_database_contents(self):
        """Debug function to check what's in the database."""
        print("\n=== DATABASE DEBUG INFO ===")
        try:
            import os
            db_path = "data/game_data.db"
            if os.path.exists(db_path):
                print(f"Database file exists: {db_path}")
                print(f"Database file size: {os.path.getsize(db_path)} bytes")
            else:
                print(f"Database file NOT found: {db_path}")
                return
            worlds = self.db.get_all_worlds()
            print(f"Worlds in database: {len(worlds)}")
            for world in worlds:
                print(f"  World: ID={world['id']}, Name='{world['name']}'")
            all_maps = self.db.get_all_maps()
            print(f"Total maps in database: {len(all_maps)}")
            for map_data in all_maps:
                print(f"  Map: ID={map_data[0]}, Name='{map_data[1]}', Path='{map_data[2]}'")
            unassigned = self.db.get_unassigned_maps()
            print(f"Unassigned maps: {len(unassigned)}")
            for map_data in unassigned:
                print(f"  Unassigned: ID={map_data[0]}, Name='{map_data[1]}'")
            images_path = "data/images"
            if os.path.exists(images_path):
                image_files = os.listdir(images_path)
                print(f"Images in data/images: {len(image_files)}")
                for img_file in image_files:
                    print(f"  Image: {img_file}")
            else:
                print("Images folder does not exist")
        except Exception as e:
            print(f"ERROR checking database: {e}")
            import traceback
            traceback.print_exc()
        print("=== END DATABASE DEBUG ===\n")

    def test_map_creation_flow(self):
        """Test the map creation and world creation flow."""
        print("\n=== TESTING MAP CREATION FLOW ===")
        self.debug_database_contents()
        try:
            test_map_data = {
                'name': 'Test Map',
                'image_path': 'data/images/test_map.png',
                'grid_size': 50,
                'grid_enabled': True,
                'width': 800,
                'height': 600,
                'grid_color': '#FFFFFF',
                'map_scale': 1.0,
                'grid_style': 'dashed',
                'grid_opacity': 0.7
            }
            map_id = self.db.save_or_update_map(test_map_data)
            if map_id:
                print(f"SUCCESS: Test map created with ID: {map_id}")
                unassigned = self.db.get_unassigned_maps()
                print(f"Unassigned maps after test creation: {len(unassigned)}")
            else:
                print("FAILED: Could not create test map")
        except Exception as e:
            print(f"ERROR in test map creation: {e}")
            import traceback
            traceback.print_exc()
        print("=== END TEST ===\n")

    def toggle_fullscreen(self):
        """Toggles the display between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        current_size = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        if self.fullscreen:
            self.screen = pygame.display.set_mode(current_size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(current_size, pygame.RESIZABLE)

        if hasattr(self, 'gui_manager') and self.gui_manager:
            self.gui_manager.set_window_resolution(current_size)

        print(f"Fullscreen: {self.fullscreen}")

    def cleanup(self):
        """Clean up resources before exiting."""
        print("Cleaning up resources...")
        
        # Stop any playing audio
        if self.audio_enabled:
            self.stop_audio()
            try:
                pygame.mixer.quit()
                print("Audio mixer closed")
            except:
                pass
        
        print("Closing database connection...")
        self.db.close()
        
        if hasattr(self, 'map_creator_process') and self.map_creator_process and self.map_creator_process.poll() is None:
            print("Terminating map creator process...")
            self.map_creator_process.terminate()
            try:
                self.map_creator_process.wait(timeout=2)
                print("Map creator process terminated.")
            except subprocess.TimeoutExpired:
                print("Map creator process did not terminate quickly, killing...")
                self.map_creator_process.kill()
        
        print("Exiting Pygame.")
        pygame.quit()


if __name__ == '__main__':
    app = GameApp()
    app.run()