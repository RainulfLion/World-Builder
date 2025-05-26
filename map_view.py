# map_view.py
import pygame
import os
import config # For colors, potentially grid size default

class MapView:
    def __init__(self, app_ref):
        self.app = app_ref
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 300 # Pixels per second
        self.scroll_speed = 50 # Pixels per scroll wheel tick
        self.grid_size = 50
        self.grid_color = (128, 128, 128)
        self.grid_opacity = 128
        self.map_surface = None # Holds the original loaded map image
        self.map_pixel_width = 0 # Actual pixel dimensions of the map image
        self.map_pixel_height = 0

        # Define the area on the screen where the map is drawn
        # Example: dynamically calculate based on UI layout
        self.map_area_rect = pygame.Rect(
            config.MAP_AREA_LEFT,
            config.MAP_AREA_TOP,
            config.MAP_AREA_WIDTH,
            config.MAP_AREA_HEIGHT
        )
        # Surface for drawing the visible portion of the map
        self.view_surface = pygame.Surface(self.map_area_rect.size)

        # Cache loaded token images {image_path: surface}
        self.token_image_cache = {}
        # Cache loaded death images
        self.death_image_cache = {}

        # Panning state
        self.is_panning_mouse = False # For middle mouse button panning
        self.last_mouse_pos = None
        self.is_panning_up = False
        self.is_panning_down = False
        self.is_panning_left = False
        self.is_panning_right = False

        # Zoom is now fixed at 1.0
        self.zoom_level = 1.0


    def handle_event(self, event):
        """Handle events related to map interaction (panning, zooming, clicks)."""
        # --- Keyboard Panning ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.is_panning_up = True
            elif event.key == pygame.K_DOWN:
                self.is_panning_down = True
            elif event.key == pygame.K_LEFT:
                self.is_panning_left = True
            elif event.key == pygame.K_RIGHT:
                self.is_panning_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.is_panning_up = False
            elif event.key == pygame.K_DOWN:
                self.is_panning_down = False
            elif event.key == pygame.K_LEFT:
                self.is_panning_left = False
            elif event.key == pygame.K_RIGHT:
                self.is_panning_right = False

        # --- Mouse Interaction ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is within the map drawing area
            if self.map_area_rect.collidepoint(event.pos):
                if event.button == 2: # Middle mouse button
                    self.is_panning_mouse = True
                    self.last_mouse_pos = event.pos
                elif event.button == 1: # Left click (example: select token)
                    map_coords = self.screen_to_map_coords(event.pos)
                    grid_coords = self.map_to_grid_coords(map_coords)
                    # Pass click to app to handle selection/movement logic
                    self.app.handle_map_click(grid_coords) # Assuming GameApp has this method
                    print(f"Map left-click at screen {event.pos} -> map {map_coords} -> grid {grid_coords}")
                elif event.button == 3: # Right click (example: context menu)
                    map_coords = self.screen_to_map_coords(event.pos)
                    grid_coords = self.map_to_grid_coords(map_coords)
                    # Pass click to app to handle context menu
                    # self.app.handle_map_right_click(grid_coords, event.pos)
                    print(f"Map right-click at screen {event.pos} -> map {map_coords} -> grid {grid_coords}")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2: # Middle mouse button release
                self.is_panning_mouse = False
                self.last_mouse_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if self.is_panning_mouse and self.last_mouse_pos:
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                # Adjust camera based on mouse movement (inverse)
                self.camera_x -= dx # / self.zoom_level (Zoom is 1.0)
                self.camera_y -= dy # / self.zoom_level (Zoom is 1.0)
                self.last_mouse_pos = event.pos
                # Clamp camera after mouse panning
                self.clamp_camera()

        elif event.type == pygame.MOUSEWHEEL:
             if self.map_area_rect.collidepoint(pygame.mouse.get_pos()): # Only scroll if mouse is over map
                # Scroll vertically with mouse wheel
                scroll_amount = event.y * self.scroll_speed
                self.camera_y -= scroll_amount # Adjust camera_y (inverse direction typical for scrolling)
                print(f"Scroll event: y={event.y}, new camera_y={self.camera_y}")
                self.clamp_camera() # Re-clamp after scroll adjustment

    def clamp_camera(self):
        """Prevent the camera from panning beyond the map boundaries."""
        if not self.map_surface: return # No map loaded

        # Calculate the dimensions of the view in map pixels
        # Zoom is fixed at 1.0
        view_width_map = self.map_area_rect.width
        view_height_map = self.map_area_rect.height

        # Calculate max camera coordinates
        max_camera_x = max(0, self.map_pixel_width - view_width_map)
        max_camera_y = max(0, self.map_pixel_height - view_height_map)

        # Clamp camera coordinates
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def update(self, time_delta):
        """Update camera position based on panning flags."""
        if not self.map_surface:
            return # Don't pan if no map

        delta_x = 0
        delta_y = 0
        speed = self.camera_speed # Panning speed no longer adjusts with zoom

        if self.is_panning_up:
            delta_y -= speed * time_delta
        if self.is_panning_down:
            delta_y += speed * time_delta
        if self.is_panning_left:
            delta_x -= speed * time_delta
        if self.is_panning_right:
            delta_x += speed * time_delta

        if delta_x != 0 or delta_y != 0:
            self.camera_x += delta_x
            self.camera_y += delta_y
            self.clamp_camera()

    def get_map_rect(self):
        """Returns the screen rectangle where the map is drawn."""
        return self.map_area_rect

    def load_map_data(self, map_data):
        """Update view settings and load the map image when a map is loaded."""
        self.grid_size = map_data.get('grid_size', 50)
        self.map_pixel_width = map_data.get('map_width_pixels', self.map_area_rect.width) # Default to view size if not set
        self.map_pixel_height = map_data.get('map_height_pixels', self.map_area_rect.height)

        # --- Load the map image ---
        image_path = map_data.get('image_path')
        loaded = False
        if image_path:
            print(f"MapView: Attempting to load image from path: {image_path}")
            # Check common image path scenarios (copied from main.py's original logic)
            potential_paths = [
                image_path,  # Absolute path?
                os.path.join(config.MAPS_DIR, image_path),  # Relative to configured maps dir
                # Add other potential relative paths if necessary
            ]
            for path in potential_paths:
                abs_path = os.path.abspath(path) # Ensure path is absolute for checking
                print(f"MapView: Trying absolute path: {abs_path}")
                if os.path.exists(abs_path):
                    try:
                        print(f"MapView: Found existing file at: {abs_path}")
                        self.map_surface = pygame.image.load(abs_path).convert_alpha()
                        print(f"MapView: Map image loaded successfully. Size: {self.map_surface.get_size()}")
                        # Update map dimensions based on loaded image
                        self.map_pixel_width = self.map_surface.get_width()
                        self.map_pixel_height = self.map_surface.get_height()
                        loaded = True
                        break
                    except pygame.error as e:
                        print(f"MapView: Failed to load image at {abs_path}: {e}")

        if not loaded:
            print("MapView ERROR: Could not load map image.")
            self.map_surface = None # Ensure it's None if loading failed
            self.map_pixel_width = 0
            self.map_pixel_height = 0
        # --- END: Load the map image ---

        # Reset camera and clamp on map load
        self.camera_x = 0
        self.camera_y = 0
        # self.zoom_level = 1.0 # Zoom is always 1.0 now
        self.clamp_camera() # Clamp initially

    def screen_to_map_coords(self, screen_pos):
        """Convert screen coordinates (within map_area_rect) to map pixel coordinates."""
        # Account for camera pan and zoom, and the map area's offset on screen
        # Zoom is fixed at 1.0
        map_x = (screen_pos[0] - self.map_area_rect.left) + self.camera_x
        map_y = (screen_pos[1] - self.map_area_rect.top) + self.camera_y
        return int(map_x), int(map_y)

    def map_to_grid_coords(self, map_x, map_y=None):
        """Convert map pixel coordinates to grid coordinates.
        Accepts either separate x,y coordinates or a single (x,y) tuple."""
        # Handle case where first argument is a tuple
        if map_y is None:
            map_x, map_y = map_x
            
        # Account for grid offset
        grid_x = map_x // self.grid_size
        grid_y = map_y // self.grid_size
        return grid_x, grid_y

    def grid_to_map_coords(self, grid_pos):
        """Convert grid coordinates to map pixel coordinates (top-left of grid cell)."""
        map_x = grid_pos[0] * self.grid_size
        map_y = grid_pos[1] * self.grid_size
        return map_x, map_y

    def map_to_screen_coords(self, map_pos):
         """Convert map pixel coordinates to screen coordinates."""
         # Account for camera pan and zoom, and map area offset
         # Zoom is fixed at 1.0
         screen_x = (map_pos[0] - self.camera_x) + self.map_area_rect.left
         screen_y = (map_pos[1] - self.camera_y) + self.map_area_rect.top
         return int(screen_x), int(screen_y)

    def _load_image(self, image_path, cache):
        """Loads an image, caches it, handles errors."""
        if not image_path or not isinstance(image_path, str):
             return None
        if image_path in cache:
            return cache[image_path]
        try:
            # Assume paths are relative to an assets directory
            full_path = os.path.join("assets", image_path) # Adjust structure if needed
            if os.path.exists(full_path):
                image = pygame.image.load(full_path).convert_alpha()
                cache[image_path] = image
                return image
            else:
                print(f"Warning: Image file not found: {full_path}")
                cache[image_path] = None # Cache the miss
                return None
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            cache[image_path] = None # Cache the error
            return None


    def draw(self, screen, tokens, notes, locations, selected_token_instance_id):
        """Draw the map view with all elements, handling pan and zoom."""
        # Fill the view surface with a background color (e.g., black)
        self.view_surface.fill((0, 0, 0))

        # Draw map image if loaded
        if self.map_surface:
            # 1. Calculate the source rectangle (portion of the map image to draw)
            # Zoom is fixed at 1.0
            source_rect = pygame.Rect(self.camera_x, self.camera_y,
                                      self.map_area_rect.width, self.map_area_rect.height)

            # Ensure source rect doesn't exceed map image bounds
            source_rect = source_rect.clip(self.map_surface.get_rect())

            if source_rect.width > 0 and source_rect.height > 0:
                 # 2. Blit the correct portion of the map image directly (no scaling needed as zoom=1)
                 self.view_surface.blit(self.map_surface.subsurface(source_rect), (0, 0))


        # Draw grid onto the view_surface
        self.draw_grid(self.view_surface)

        # Draw tokens onto the view_surface
        self.draw_tokens(self.view_surface, tokens, selected_token_instance_id)

        # Draw notes onto the view_surface (similar to tokens)
        self.draw_notes(self.view_surface, notes)

        # Draw locations onto the view_surface (similar to tokens)
        self.draw_locations(self.view_surface, locations)

        # Finally, blit the completed view_surface onto the main screen
        screen.blit(self.view_surface, self.map_area_rect.topleft)


    def draw_grid(self, surface):
        """Draws the grid lines on the target surface, considering camera and zoom."""
        if not self.map_surface or self.grid_size <= 0:
            return

        view_width, view_height = surface.get_size()
        # grid_size_zoomed = self.grid_size # Zoom is 1.0

        # Calculate the map coordinates of the top-left corner of the view
        map_start_x = self.camera_x
        map_start_y = self.camera_y

        # Calculate the map coordinates of the bottom-right corner of the view
        map_end_x = map_start_x + view_width # Zoom is 1.0
        map_end_y = map_start_y + view_height # Zoom is 1.0

        # Determine the first grid lines within the view
        start_grid_x = int(map_start_x // self.grid_size)
        start_grid_y = int(map_start_y // self.grid_size)

        # Determine the last grid lines to draw
        end_grid_x = int(map_end_x // self.grid_size) + 1
        end_grid_y = int(map_end_y // self.grid_size) + 1

        grid_color_with_alpha = (*self.grid_color, self.grid_opacity)

        # Draw vertical lines
        for grid_x in range(start_grid_x, end_grid_x + 1):
            map_x = grid_x * self.grid_size
            # Convert map x-coordinate to view x-coordinate
            view_x = map_x - self.camera_x # Zoom is 1.0

            if 0 <= view_x <= view_width: # Only draw if potentially visible
                 # Draw line directly on the surface (view_surface)
                 start_pos = (int(view_x), 0)
                 end_pos = (int(view_x), view_height)
                 pygame.draw.line(surface, grid_color_with_alpha, start_pos, end_pos, 1)


        # Draw horizontal lines
        for grid_y in range(start_grid_y, end_grid_y + 1):
            map_y = grid_y * self.grid_size
            # Convert map y-coordinate to view y-coordinate
            view_y = map_y - self.camera_y # Zoom is 1.0

            if 0 <= view_y <= view_height: # Only draw if potentially visible
                 # Draw line directly on the surface (view_surface)
                 start_pos = (0, int(view_y))
                 end_pos = (view_width, int(view_y))
                 pygame.draw.line(surface, grid_color_with_alpha, start_pos, end_pos, 1)


    def draw_tokens(self, surface, tokens, selected_token_instance_id):
        """Draw tokens onto the target surface, adjusting for camera and zoom."""
        if self.grid_size <= 0: return # Avoid division by zero

        token_size_pixels = self.grid_size # Scale token size with zoom is removed
        # if token_size_pixels <= 0: return # Grid size check above covers this

        for token_data in tokens:
            # Example token data structure (adapt as needed):
            # {'instance_id': '...', 'token_id': '...', 'map_id': '...',
            #  'x': grid_x, 'y': grid_y, 'image_path': '...', 'death_image_path': '...'}

            grid_x = token_data.get('x')
            grid_y = token_data.get('y')
            image_path = token_data.get('image_path')
            death_image_path = token_data.get('death_image_path') # Optional
            instance_id = token_data.get('instance_id')
            is_dead = token_data.get('is_dead', False) # Assuming you track this

            if grid_x is None or grid_y is None: continue # Skip if position is invalid

            # Determine which image to use
            current_image_path = death_image_path if is_dead else image_path
            if not current_image_path: continue # Skip if no image path

            # Load image (use appropriate cache)
            cache = self.death_image_cache if is_dead else self.token_image_cache
            token_image = self._load_image(current_image_path, cache)
            if not token_image: continue # Skip if image loading failed

            # Scale the token image
            try:
                scaled_token_image = pygame.transform.smoothscale(token_image, (token_size_pixels, token_size_pixels))
            except ValueError: # May happen if token_size_pixels is zero or negative
                continue

            # Calculate map pixel coordinates (top-left corner of the grid cell)
            map_x = grid_x * self.grid_size
            map_y = grid_y * self.grid_size

            # Convert map coordinates to view coordinates (relative to the view_surface)
            view_x = map_x - self.camera_x # Zoom is 1.0
            view_y = map_y - self.camera_y # Zoom is 1.0

            # --- Draw Token ---
            # Check if the token is at least partially visible within the view surface
            token_rect_view = pygame.Rect(view_x, view_y, token_size_pixels, token_size_pixels)
            view_rect = surface.get_rect()

            if view_rect.colliderect(token_rect_view):
                 surface.blit(scaled_token_image, (view_x, view_y))

                 # --- Highlight Selected Token ---
                 if instance_id == selected_token_instance_id:
                     highlight_color = (255, 255, 0, 150) # Yellow semi-transparent
                     # Draw border slightly inside the token bounds
                     border_rect = pygame.Rect(view_x + 1, view_y + 1, token_size_pixels - 2, token_size_pixels - 2)
                     pygame.draw.rect(surface, highlight_color, border_rect, 3) # 3px thick border


    def draw_notes(self, surface, notes):
        """Placeholder for drawing notes."""
        # TODO: Implement drawing notes similar to tokens, possibly using icons or text
        pass

    def draw_locations(self, surface, locations):
        """Placeholder for drawing locations."""
        # TODO: Implement drawing locations, maybe as markers or area highlights
        pass