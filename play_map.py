import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import json
from token_manager import TokenStats
from character_info_box import CharacterInfoBox
import time
import sys
from world_manager import WorldManager
from map_linker import MapLinker
import subprocess

class Token:
    def __init__(self, canvas, name, x, y, grid_size=None):
        """Initialize a token"""
        self.canvas = canvas
        self.name = name
        self.x = x
        self.y = y
        self.grid_size = grid_size
        print(f"[Token] Creating TokenStats for {name}")  # Debug print
        # Load token stats from JSON file
        json_path = os.path.join("D:/WorldWiki/Grid map/tokens", f"{name}.json")
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                print(f"[Token] Loaded data from JSON: {data}")  # Debug print
                self.token_stats = TokenStats(name=name, data=data)
        except Exception as e:
            print(f"[Token] Error loading JSON: {e}, creating default TokenStats")  # Debug print
            self.token_stats = TokenStats(name=name)
        
        print(f"[Token] Final token stats: {self.token_stats.stats}")  # Debug print
        self.token_image = None
        self.death_image = None
        self.is_dead = False
        self.snap_to_grid = True  # Default to grid snapping
        self.image_item = None
        self.highlight_item = None
        self.info_box = None
        self.selected = False
        
        print(f"[Token] Created new token: {name} at ({x}, {y}) with grid_size={grid_size}")  # Debug print
        
    def load_image(self):
        """Load the token's image if specified in stats"""
        try:
            # First try PNG file directly
            png_file = os.path.join("D:/WorldWiki/Grid map/tokens", f"{self.name}.png")
            print(f"[Token] Trying PNG file: {png_file}")  # Debug print
            
            if os.path.exists(png_file):
                print(f"[Token] Loading PNG file: {png_file}")  # Debug print
                image = Image.open(png_file)
                if self.grid_size:
                    # Convert grid_size to integer for resize
                    size = (int(self.grid_size), int(self.grid_size))
                    image = image.resize(size, Image.Resampling.LANCZOS)
                self.token_image = ImageTk.PhotoImage(image)
                print(f"[Token] Successfully loaded PNG image")  # Debug print
                
                # Load death image
                death_file = "D:/WorldWiki/dist/Death.png"
                if os.path.exists(death_file):
                    death_image = Image.open(death_file)
                    if self.grid_size:
                        death_image = death_image.resize(size, Image.Resampling.LANCZOS)
                    self.death_image = ImageTk.PhotoImage(death_image)
                return
                
            # If no PNG, try image path from stats
            if self.token_stats and self.token_stats.image_paths:
                image_path = self.token_stats.image_paths[0]
                print(f"[Token] Trying image from stats: {image_path}")  # Debug print
                
                if os.path.exists(image_path):
                    print(f"[Token] Loading image from stats: {image_path}")  # Debug print
                    image = Image.open(image_path)
                    if self.grid_size:
                        # Convert grid_size to integer for resize
                        size = (int(self.grid_size), int(self.grid_size))
                        image = image.resize(size, Image.Resampling.LANCZOS)
                    self.token_image = ImageTk.PhotoImage(image)
                    
                    # Load death image
                    death_file = "D:/WorldWiki/dist/Death.png"
                    if os.path.exists(death_file):
                        death_image = Image.open(death_file)
                        if self.grid_size:
                            death_image = death_image.resize(size, Image.Resampling.LANCZOS)
                        self.death_image = ImageTk.PhotoImage(death_image)
                    print(f"[Token] Successfully loaded image from stats")  # Debug print
                    return
                else:
                    print(f"[Token] Image file not found: {image_path}")  # Debug print
                    
            print(f"[Token] No valid image found for token: {self.name}")  # Debug print
                    
        except Exception as e:
            print(f"[Token] Error loading token image: {e}")  # Debug print
            
    def draw(self, image_pos=None):
        """Draw the token on the canvas"""
        try:
            # Load image if not already loaded
            if not self.token_image:
                self.load_image()
                
            if not self.token_image:
                # Create default rectangle if no image
                size = 20
                x = self.x - size/2
                y = self.y - size/2
                if self.image_item:
                    self.canvas.delete(self.image_item)
                self.image_item = self.canvas.create_rectangle(x, y, x+size, y+size, 
                                                             fill="red", tags=("token", self.name))
                return
                
            # Calculate position
            x = self.x
            y = self.y
            if image_pos:
                x += image_pos[0]
                y += image_pos[1]
            
            # Update existing image instead of deleting/recreating
            if self.image_item:
                # Update coordinates and image
                self.canvas.coords(self.image_item, x, y)
                if self.is_dead and self.death_image:
                    self.canvas.itemconfig(self.image_item, image=self.death_image)
                else:
                    self.canvas.itemconfig(self.image_item, image=self.token_image)
            else:
                # Create new image
                if self.is_dead and self.death_image:
                    self.image_item = self.canvas.create_image(x, y, image=self.death_image, tags=("token", self.name))
                else:
                    self.image_item = self.canvas.create_image(x, y, image=self.token_image, tags=("token", self.name))
            
            # Update selection highlight
            if self.selected:
                if not self.highlight_item:
                    # Create highlight circle using grid size
                    radius = self.grid_size / 2
                    self.highlight_item = self.canvas.create_oval(x-radius, y-radius, 
                                                                x+radius, y+radius,
                                                                outline="yellow",
                                                                width=2)
                else:
                    # Update highlight position
                    radius = self.grid_size / 2
                    self.canvas.coords(self.highlight_item, x-radius, y-radius, 
                                     x+radius, y+radius)
            else:
                # Remove highlight if not selected
                if self.highlight_item:
                    self.canvas.delete(self.highlight_item)
                    self.highlight_item = None
                    
        except Exception as e:
            print(f"[Token] Error drawing token: {e}")  # Debug print
            
    def show_info(self, event=None):
        """Show the character info box"""
        if self.info_box and not self.info_box.window.winfo_exists():
            self.info_box = None
            
        if not self.info_box:
            self.info_box = CharacterInfoBox(self.canvas, self)
        else:
            self.info_box.window.lift()
            # Update position to follow cursor
            x = self.canvas.winfo_rootx() + event.x
            y = self.canvas.winfo_rooty() + event.y
            self.info_box.window.geometry(f"+{x}+{y}")

    def contains_point(self, x, y):
        """Check if a point is within the token's bounds"""
        try:
            # Get token bounds
            if self.image_item:
                bbox = self.canvas.bbox(self.image_item)
            else:
                # Use default rectangle size if no image
                size = int(self.grid_size) if self.grid_size else 50
                x_pos = self.x * size if self.grid_size else self.x
                y_pos = self.y * size if self.grid_size else self.y
                bbox = (x_pos - size/2, y_pos - size/2, x_pos + size/2, y_pos + size/2)
            
            # Check if point is within bounds
            if bbox:
                return (bbox[0] <= x <= bbox[2]) and (bbox[1] <= y <= bbox[3])
            else:
                return False
            
        except Exception as e:
            print(f"[Token] Error checking point: {e}")  # Debug print
            return False

    def move_to(self, x, y):
        """Move token to specified position"""
        if self.grid_size and self.snap_to_grid:
            # Snap to center of grid squares
            grid_x = int(x / self.grid_size)
            grid_y = int(y / self.grid_size)
            self.x = (grid_x * self.grid_size) + (self.grid_size / 2)
            self.y = (grid_y * self.grid_size) + (self.grid_size / 2)
        else:
            # Free movement
            self.x = x
            self.y = y
        self.draw()

    def toggle_grid_snap(self):
        """Toggle grid snapping for this token"""
        self.snap_to_grid = not self.snap_to_grid
        print(f"[Token] Grid snap toggled to {self.snap_to_grid}")  # Debug print
        
    def toggle_death(self):
        """Toggle death state for this token"""
        self.is_dead = not self.is_dead
        print(f"[Token] Death state toggled to {self.is_dead}")  # Debug print
        self.draw()  # Redraw with new state

class TokenInfoPopup:
    def __init__(self, parent, token, position):
        """Initialize the token info popup"""
        self.token = token  # Store reference to token
        self.top = tk.Toplevel(parent)
        self.top.title(f"{token.name} Info")
        
        # Position window near token
        if position:
            self.top.geometry(f"+{position[0]}+{position[1]}")
        
        # Create main frame
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add grid coordinates
        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(fill=tk.X, pady=2)
        ttk.Label(grid_frame, text="Position:").pack(side=tk.LEFT)
        ttk.Label(grid_frame, text=f"X: {int(token.x)}, Y: {int(token.y)}").pack(side=tk.LEFT, padx=(5, 0))
        
        # Token name
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(name_frame, text=token.name, 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # HP adjustment
        hp_frame = ttk.Frame(main_frame)
        hp_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(hp_frame, text="HP:").pack(side=tk.LEFT)
        self.hp_var = tk.StringVar(value=str(token.token_stats.stats.get('HP', 10)))
        hp_entry = ttk.Entry(hp_frame, textvariable=self.hp_var, width=5)
        hp_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(hp_frame, text="-", width=2,
                  command=lambda: self.adjust_hp(-1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(hp_frame, text="+", width=2,
                  command=lambda: self.adjust_hp(1)).pack(side=tk.LEFT, padx=1)
        
        # Other stats display
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(stats_frame, text=f"AC: {token.token_stats.stats.get('AC', 10)}").pack(side=tk.LEFT, padx=2)
        ttk.Label(stats_frame, text=f"Init: {token.token_stats.stats.get('Initiative', 0)}").pack(side=tk.LEFT, padx=2)
        ttk.Label(stats_frame, text=f"Speed: {token.token_stats.stats.get('Speed', 30)}").pack(side=tk.LEFT, padx=2)
        
        # Status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        status_text = "Dead" if token.is_dead else "Alive"
        ttk.Label(status_frame, text=status_text).pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind events
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)
        self.top.bind("<Button-1>", self.start_move)
        self.top.bind("<B1-Motion>", self.on_move)
        
        # Movement variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Set focus
        self.top.focus_force()
        
    def adjust_hp(self, amount):
        """Adjust HP by the specified amount"""
        try:
            current_hp = int(self.hp_var.get())
            new_hp = current_hp + amount
            self.hp_var.set(str(new_hp))
            self.token.token_stats.stats['HP'] = new_hp
        except ValueError as e:
            print(f"[TokenInfoPopup] Error adjusting HP: {e}")
            
    def on_close(self):
        """Handle window close"""
        try:
            # Update HP before closing
            new_hp = int(self.hp_var.get())
            self.token.token_stats.stats['HP'] = new_hp
            self.token.info_box = None
            self.top.destroy()
        except ValueError as e:
            print(f"[TokenInfoPopup] Error saving HP: {e}")
            self.top.destroy()
            
    def start_move(self, event):
        """Start moving the popup"""
        self.drag_start_x = event.x_root - self.top.winfo_x()
        self.drag_start_y = event.y_root - self.top.winfo_y()
        
    def on_move(self, event):
        """Handle moving the popup"""
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.top.geometry(f"+{x}+{y}")

class TokenSelectDialog:
    def __init__(self, parent):
        """Initialize the token select dialog"""
        self.top = tk.Toplevel(parent)
        self.top.title("Select Token")
        self.result = None
        
        # Create listbox with scrollbar
        list_frame = ttk.Frame(self.top)
        list_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(list_frame, width=40, height=15)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load token list
        self.token_files = {}
        token_dir = "D:/WorldWiki/Grid map/tokens"
        if os.path.exists(token_dir):
            # Get all JSON files
            json_files = [f for f in os.listdir(token_dir) if f.lower().endswith('.json')]
            
            # Get all PNG files
            png_files = [f for f in os.listdir(token_dir) if f.lower().endswith('.png')]
            png_names = {os.path.splitext(f)[0].lower(): f for f in png_files}
            
            for json_file in json_files:
                token_name = os.path.splitext(json_file)[0]
                json_path = os.path.join(token_dir, json_file)
                
                # Find matching PNG file
                png_name = png_names.get(token_name.lower())
                if png_name:
                    # Add token to list
                    self.token_files[token_name] = {
                        'json': json_path,
                        'png': os.path.join(token_dir, png_name)
                    }
                    self.listbox.insert(tk.END, token_name)
                    print(f"[TokenSelectDialog] Added token: {token_name} with files: {self.token_files[token_name]}")  # Debug print
        
        if not self.token_files:
            self.listbox.insert(tk.END, "No tokens found - Create some in Token Manager")
            self.listbox.configure(state='disabled')
        
        # Add buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Select", command=self.on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT)
        
        # Center dialog
        self.top.transient(parent)
        self.top.grab_set()
        
        # Position dialog
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.top.geometry(f"+{x}+{y}")
        
        # Wait for user input
        parent.wait_window(self.top)
    
    def on_select(self):
        """Handle select button click"""
        selection = self.listbox.curselection()
        if selection:
            token_name = self.listbox.get(selection[0])
            self.result = token_name
            self.top.destroy()
    
    def on_cancel(self):
        """Handle cancel button click"""
        self.result = None
        self.top.destroy()

class MapPlayer:
    def __init__(self, root):
        """Initialize the map player"""
        self.root = root
        self.root.title("Map Player")
        
        # Initialize variables
        self.current_world = None
        self.current_map = None
        self.tokens = {}
        self.selected_token = None
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.grid_size = 20
        self.show_grid = True  # Add show_grid variable
        self.placing_location = False
        self.location_buttons = {}
        
        # Create UI elements
        self.setup_ui()
        
    def create_token(self, token_name, x, y):
        """Create a new token at the specified position"""
        try:
            # Find the correct case for the token name
            token_dir = "D:/WorldWiki/Grid map/tokens"
            actual_name = token_name
            if os.path.exists(token_dir):
                for file in os.listdir(token_dir):
                    if file.lower() == f"{token_name.lower()}.json":
                        actual_name = os.path.splitext(file)[0]
                        break
        
            print(f"[MapPlayer] Creating token with name: {actual_name}")  # Debug print
            token = Token(self.canvas, actual_name, x, y, self.grid_size)
            token.load_image()
            token.draw()
            self.tokens[token_name] = token
            return token
            
        except Exception as e:
            print(f"[MapPlayer] Error creating token: {e}")
            messagebox.showerror("Error", f"Failed to create token: {str(e)}")
            return None

    def add_token(self):
        """DO NOT CHANGE THIS METHOD - Working correctly for adding tokens from JSON files"""
        try:
            # Open token selection dialog
            dialog = TokenSelectDialog(self.root)
            
            if dialog.result:
                # Get token info
                token_name = dialog.result
                print(f"[MapPlayer] Selected token: {token_name}")  # Debug print
                
                # Create token at center of visible area
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                x = self.canvas.canvasx(canvas_width/2)
                y = self.canvas.canvasy(canvas_height/2)
                
                # Create and add token
                self.create_token(token_name, x, y)
                
        except Exception as e:
            print(f"[MapPlayer] Error adding token: {e}")
            messagebox.showerror("Error", f"Failed to add token: {str(e)}")

    def load_token_info(self, token_name):
        """Load token information from token directory"""
        try:
            json_path = os.path.join("D:/WorldWiki/Grid map/tokens", f"{token_name}.json")
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"[MapPlayer] Error loading token info: {e}")
            return None
    
    def load_map(self, file_path=None):
        """Load and display a map file"""
        try:
            if not file_path:
                file_path = filedialog.askopenfilename(
                    title="Select Map File",
                    initialdir=os.path.join("D:", "WorldWiki", "dist", "Places"),
                    filetypes=[
                        ("Map files", "*.map;*.MAP"),
                        ("Game Map files", "*.gmap;*.gamemap"),
                        ("All files", "*.*")
                    ]
                )
            
            if not file_path:
                return
                
            try:
                # Try to read the map file as JSON
                with open(file_path, 'r') as f:
                    map_data = json.load(f)
                    
                # Get image path from map data
                image_path = map_data.get('image_path')
                if not image_path:
                    raise ValueError("No image path found in map file")
                    
                # Convert relative path to absolute if needed
                if not os.path.isabs(image_path):
                    map_dir = os.path.dirname(file_path)
                    image_path = os.path.join(map_dir, image_path)
                    
                print(f"[MapPlayer] Loading image from: {image_path}")  # Debug print
                
                # Check if image exists
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Image file not found: {image_path}")
                    
                # Load other map properties if available
                self.grid_size = map_data.get('grid_size', self.grid_size)
                self.show_grid = map_data.get('show_grid', True)  # Default to True
                saved_image_position = map_data.get('image_position')
                if saved_image_position:
                    self.image_position = saved_image_position
                    
            except json.JSONDecodeError:
                # If not JSON, try to load the file directly as an image
                image_path = file_path
                
            # Load map image
            self.image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(self.image)
            
            # Set current map
            self.current_map = file_path
            
            # Clear existing items
            self.canvas.delete("all")
            self.tokens.clear()
            for info in self.location_buttons.values():
                self.canvas.delete(info["window"])
            self.location_buttons.clear()
            
            # Update canvas
            self.update_canvas()
            
            # Load saved state for this map if it exists
            if self.current_world:
                map_data = self.world_manager.get_map_state(self.current_world, file_path)
                if map_data:
                    self.restore_map_state(map_data)
            
            print("[MapPlayer] Map loaded successfully")  # Debug print
            
        except Exception as e:
            print(f"[MapPlayer] Error loading map: {e}")  # Debug print
            messagebox.showerror("Error", f"Failed to load map: {str(e)}")

    def restore_map_state(self, map_data):
        """Restore a map's saved state"""
        try:
            # Restore locations
            for name, loc_data in map_data["locations"].items():
                # Create frame for the button
                frame = tk.Frame(self.canvas, bd=1, relief="raised")
                
                # Create image label
                image_label = tk.Label(frame, image=self.location_photo)
                image_label.pack(side=tk.LEFT, padx=2)
                
                # Create text label
                text_label = tk.Label(frame, text=loc_data["text"])
                text_label.pack(side=tk.LEFT, padx=2)
                
                # Add to canvas
                window = self.canvas.create_window(loc_data["x"], loc_data["y"], 
                                                 window=frame, anchor="nw")
                
                # Store button info
                self.location_buttons[name] = {
                    "frame": frame,
                    "image_label": image_label,
                    "text_label": text_label,
                    "x": loc_data["x"],
                    "y": loc_data["y"],
                    "linked_map": loc_data["linked_map"],
                    "window": window,
                    "dragging": False,
                    "clicked": False
                }
                
                # Bind events
                frame.bind("<Button-1>", lambda e, n=name: self.start_location_click(e, n))
                frame.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
                frame.bind("<ButtonRelease-1>", lambda e, n=name: self.handle_location_release(e, n))
                frame.bind("<Button-3>", lambda e, n=name: self.show_location_menu(e, n))
                
                image_label.bind("<Button-1>", lambda e, n=name: self.start_location_click(e, n))
                image_label.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
                image_label.bind("<ButtonRelease-1>", lambda e, n=name: self.handle_location_release(e, n))
                image_label.bind("<Button-3>", lambda e, n=name: self.show_location_menu(e, n))
                
                text_label.bind("<Button-1>", lambda e, n=name: self.start_location_click(e, n))
                text_label.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
                text_label.bind("<ButtonRelease-1>", lambda e, n=name: self.handle_location_release(e, n))
                text_label.bind("<Button-3>", lambda e, n=name: self.show_location_menu(e, n))
            
            # Restore tokens
            for name, token_data in map_data["tokens"].items():
                token = self.create_token(token_data["name"], token_data["x"], token_data["y"])
                if token and "stats" in token_data:
                    token.token_stats.stats.update(token_data["stats"])
                    
        except Exception as e:
            print(f"[MapPlayer] Error restoring map state: {e}")
            messagebox.showerror("Error", f"Failed to restore map state: {str(e)}")

    def load_world(self):
        """Load an existing world"""
        world_file = self.world_manager.load_world()
        if world_file:
            self.current_world = world_file
            world_data = self.world_manager.load_world_state(world_file)
            if world_data:
                # Clear current state
                self.canvas.delete("all")
                self.tokens.clear()
                for info in self.location_buttons.values():
                    self.canvas.delete(info["window"])
                self.location_buttons.clear()
                
                # Load the last map if there was one
                if world_data["current_map"]:
                    self.load_map(world_data["current_map"])

    def handle_location_release(self, event, button_name):
        """Handle mouse release on a location button"""
        try:
            button_info = self.location_buttons[button_name]
            
            if button_info["clicked"]:
                if not button_info["dragging"]:
                    if abs(event.x - button_info["click_x"]) > 5 or abs(event.y - button_info["click_y"]) > 5:
                        button_info["dragging"] = True
                
                if button_info["dragging"]:
                    # Get current position
                    x = self.canvas.canvasx(event.x)
                    y = self.canvas.canvasy(event.y)
                    
                    # Update button position
                    info = self.location_buttons[button_name]
                    info["x"] = x
                    info["y"] = y
                    
                    # Move the window
                    self.canvas.coords(info["window"], x, y)
                    
            button_info["clicked"] = False
            button_info["dragging"] = False
            
        except Exception as e:
            print(f"[MapPlayer] Error handling location release: {e}")
            
    def start_location_click(self, event, button_name):
        """Start location button click"""
        try:
            button_info = self.location_buttons[button_name]
            button_info["clicked"] = True
            button_info["dragging"] = False
            button_info["click_x"] = event.x
            button_info["click_y"] = event.y
        except Exception as e:
            print(f"[MapPlayer] Error in start_location_click: {e}")

    def location_clicked(self, button_name):
        """Handle location button click"""
        try:
            print(f"[MapPlayer] Location clicked: {button_name}")  # Debug print
            print(f"[MapPlayer] Current location_buttons: {list(self.location_buttons.keys())}")  # Debug print
            
            # If button not found, try to find it by text label
            if button_name not in self.location_buttons:
                print(f"[MapPlayer] Button {button_name} not found, searching by text label...")  # Debug print
                # Search through all buttons to find matching text
                for name, info in self.location_buttons.items():
                    text = info["text_label"].cget("text")  # Get actual text
                    print(f"[MapPlayer] Checking button {name} with text {text}")  # Debug print
                    if text == button_name:
                        button_name = name
                        print(f"[MapPlayer] Found matching button: {name}")  # Debug print
                        break
            
            if button_name not in self.location_buttons:
                raise ValueError(f"Button {button_name} not found in location_buttons")
                
            info = self.location_buttons[button_name]
            print(f"[MapPlayer] Button info: {info}")  # Debug print
            
            if info["linked_map"]:
                print(f"[MapPlayer] Loading linked map: {info['linked_map']}")  # Debug print
                # Save current map state
                if self.current_world:
                    self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                      self.location_buttons, self.tokens)
                
                # Load linked map
                self.load_map(info["linked_map"])
                
                # Update window title
                if self.current_world:
                    self.root.title(f"Map Player - {os.path.basename(self.current_world)} - {os.path.basename(self.current_map)}")
            else:
                print("[MapPlayer] No linked map, showing link menu")  # Debug print
                self.link_map_to_location(button_name)
                
        except Exception as e:
            print(f"[MapPlayer] Error in location_clicked: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"Failed to handle click: {str(e)}")
            
    def link_map_to_location(self, button_name):
        """Link a map to an existing location token"""
        try:
            if button_name not in self.location_buttons:
                raise ValueError(f"Button {button_name} not found")
                
            # Select map to link
            file_path = filedialog.askopenfilename(
                title="Select Map File",
                initialdir=os.path.join("D:", "WorldWiki", "dist", "Places"),
                filetypes=[
                    ("Map files", "*.map;*.MAP"),
                    ("PNG files", "*.png")
                ]
            )
            
            if not file_path:
                return
                
            try:
                # Update button info
                button_info = self.location_buttons[button_name]
                button_info["linked_map"] = file_path
                
                # Save world state after linking map
                if self.current_world:
                    self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                      self.location_buttons, self.tokens)
                                                      
            except Exception as e:
                print(f"[MapPlayer] Error linking map to location: {e}")
                messagebox.showerror("Error", f"Failed to link map: {str(e)}")
            
        except Exception as e:
            print(f"[MapPlayer] Error linking map: {e}")
            messagebox.showerror("Error", f"Failed to link map: {str(e)}")
            
    def load_linked_map(self, button_name):
        """Load the linked map"""
        try:
            linked_map = self.location_buttons[button_name]["linked_map"]
            if linked_map:
                self.load_map(linked_map)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load linked map: {str(e)}")

    def remove_location(self, button_name):
        """Remove a location link"""
        try:
            if button_name in self.location_buttons:
                # Remove button from canvas
                self.canvas.delete(self.location_buttons[button_name]["window"])
                
                # Remove from dictionary
                del self.location_buttons[button_name]
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove location: {str(e)}")

    def add_notes(self):
        """Add notes"""
        messagebox.showinfo("Coming Soon", "Notes Manager will be added in a future update!")

    def on_canvas_click(self, event):
        """Handle canvas click"""
        if self.placing_token:
            # Get canvas coordinates
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Create token at click position
            token = self.create_token(self.placing_token_name, x, y)
            
            # Reset placement mode
            self.placing_token = False
            self.placing_token_name = None
            self.canvas.config(cursor="")
        else:
            # Try to select a token
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Find overlapping items
            items = self.canvas.find_overlapping(x-10, y-10, x+10, y+10)
            
            # Check each item
            for item in items:
                tags = self.canvas.gettags(item)
                if "token" in tags:
                    for tag in tags:
                        if tag != "token" and tag in self.tokens:
                            self.selected_token = tag
                            self.dragging = True
                            return
            
            # If we get here, no token was found
            self.selected_token = None
            self.dragging = False

    def link_map(self):
        """Link a new map"""
        if not hasattr(self, 'image') or not self.image:
            messagebox.showwarning("Warning", "Load a map first!")
            return
            
        # Create MapLinker dialog
        linker = MapLinker(self.root, self.current_map)
        
        if linker.result:
            # Save world state after linking map
            if self.current_world:
                self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                  self.location_buttons, self.tokens)
            
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # World submenu
        world_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="World", menu=world_menu)
        world_menu.add_command(label="Create New World", command=self.create_world)
        world_menu.add_command(label="Load World", command=self.load_world)
        world_menu.add_command(label="Save World", command=self.save_world)
        
        file_menu.add_command(label="Load Map", command=self.load_map)
        file_menu.add_command(label="Add Token", command=self.add_token)
        file_menu.add_command(label="Add Location", command=self.start_add_location)
        file_menu.add_command(label="Add Notes", command=self.add_notes)
        file_menu.add_command(label="Character Data", command=self.show_character_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Grid", variable=self.show_grid, command=self.update_canvas)
        
        # Map menu
        map_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Map", menu=map_menu)
        map_menu.add_command(label="Link Map", command=self.link_map)
        
        # Token menu
        token_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Token", menu=token_menu)
        token_menu.add_command(label="Add Token", command=self.add_token)
        token_menu.add_command(label="Token Creator", command=self.open_token_creator)
        
        # Map menu
        map_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Map", menu=map_menu)
        map_menu.add_command(label="Map Creator", command=self.open_map_creator)

    def move_selected_token(self, direction):
        """Move the selected token in the specified direction"""
        if not self.selected_token:
            return
            
        # Get current position
        x = self.tokens[self.selected_token].x
        y = self.tokens[self.selected_token].y
        
        # Calculate new position
        if direction == "left":
            x -= self.grid_size
        elif direction == "right":
            x += self.grid_size
        elif direction == "up":
            y -= self.grid_size
        elif direction == "down":
            y += self.grid_size
            
        # Update token position
        self.tokens[self.selected_token].x = x
        self.tokens[self.selected_token].y = y
        self.canvas.coords(self.tokens[self.selected_token].image_item, x, y)
        
        # Update highlight rectangle if present
        if self.tokens[self.selected_token].highlight_item:
            self.canvas.coords(self.tokens[self.selected_token].highlight_item,
                             x - self.grid_size/2, y - self.grid_size/2,
                             x + self.grid_size/2, y + self.grid_size/2)
            
        # Update info box if present
        if self.tokens[self.selected_token].info_box:
            self.tokens[self.selected_token].info_box.update_position((x, y))
            
        # Save world state after moving token
        if self.current_world:
            self.world_manager.save_world_state(self.current_world, self.current_map, 
                                              self.location_buttons, self.tokens)

    def handle_drag(self, event):
        """Handle dragging on the canvas"""
        if not hasattr(self, 'image') or not self.image:
            return
            
        if self.placing_location or self.placing_token:
            return
            
    def handle_release(self, event):
        """Handle mouse release on canvas"""
        if not hasattr(self, 'image') or not self.image:
            return
            
        if self.placing_location:
            # Place a location at the release point
            self.place_location(event)
            return
            
        if self.placing_token and self.current_token:
            # Get final position
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Update token position
            self.canvas.coords(self.current_token, x, y)
            print(f"[MapPlayer] Token placed at: ({int(x/20)}, {int(y/20)})")
            
            # Add to tokens list
            self.tokens.append({
                'image': self.current_token_image,
                'x': x,
                'y': y,
                'token_id': self.current_token
            })
            
            # Reset placing flag
            self.placing_token = False
            self.current_token = None
            self.current_token_image = None
            
            # Save world state after placing token
            if self.current_world:
                self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                  self.location_buttons, self.tokens)
            return
            
        # Stop panning
        self.stop_pan(event)
        
    def start_pan(self, event):
        """Start panning the canvas"""
        if not hasattr(self, 'image') or not self.image:
            return
            
        if self.placing_location or self.placing_token:
            return
            
        self.canvas.scan_mark(event.x, event.y)
        self.pan_start = (event.x, event.y)

    def stop_pan(self, event):
        """Stop panning the canvas"""
        if hasattr(self, 'pan_start'):
            del self.pan_start
        
    def update_canvas(self):
        """Update the canvas display"""
        if not hasattr(self, 'image') or not self.image:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw image
        self.image_item = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        
        # Draw grid if enabled
        if self.show_grid:
            # Get canvas size
            width = self.image.width
            height = self.image.height
            
            # Draw vertical lines
            for x in range(0, width, self.grid_size):
                self.canvas.create_line(x, 0, x, height, fill="gray50", dash=(2, 2))
                
            # Draw horizontal lines
            for y in range(0, height, self.grid_size):
                self.canvas.create_line(0, y, width, y, fill="gray50", dash=(2, 2))
                
        # Configure scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Redraw tokens
        for token in self.tokens.values():
            token_id = self.canvas.create_image(token['x'], token['y'], image=token['image'])
            token['token_id'] = token_id
            
        # Redraw locations
        for button_name, button_info in self.location_buttons.items():
            window = self.canvas.create_window(button_info['x'], button_info['y'], 
                                            window=button_info['frame'], anchor="nw")
            button_info['window'] = window

    def place_location(self, event):
        """Place a location link token"""
        try:
            print("[MapPlayer] Starting place_location...")  # Debug print
            
            # Get click position
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            print(f"[MapPlayer] Canvas coordinates: x={x}, y={y}")  # Debug print
            
            # Create unique name
            count = len(self.location_buttons) + 1
            button_name = f"Location {count}"
            print(f"[MapPlayer] Creating button with name: {button_name}")  # Debug print
            
            # Create frame for the button
            frame = tk.Frame(self.canvas, bd=1, relief="raised")
            
            # Create image label
            image_label = tk.Label(frame, image=self.location_photo)
            image_label.pack(side=tk.LEFT, padx=2)
            
            # Create text label
            text_label = tk.Label(frame, text=button_name)
            text_label.pack(side=tk.LEFT, padx=2)
            
            # Add to canvas
            window = self.canvas.create_window(x, y, window=frame, anchor="nw")
            print(f"[MapPlayer] Created window with id: {window}")  # Debug print
            
            # Store button info with all necessary fields
            self.location_buttons[button_name] = {
                "frame": frame,
                "image_label": image_label,
                "text_label": text_label,
                "x": x,
                "y": y,
                "linked_map": None,
                "window": window,
                "dragging": False,
                "clicked": False
            }
            print(f"[MapPlayer] Stored button info. Current buttons: {list(self.location_buttons.keys())}")  # Debug print
            
            # Bind events to frame and its children
            frame.bind("<Button-1>", lambda e, n=button_name: self.start_location_click(e, n))
            frame.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
            frame.bind("<ButtonRelease-1>", lambda e, n=button_name: self.handle_location_release(e, n))
            frame.bind("<Button-3>", lambda e, n=button_name: self.show_location_menu(e, n))
            
            image_label.bind("<Button-1>", lambda e, n=button_name: self.start_location_click(e, n))
            image_label.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
            image_label.bind("<ButtonRelease-1>", lambda e, n=button_name: self.handle_location_release(e, n))
            image_label.bind("<Button-3>", lambda e, n=button_name: self.show_location_menu(e, n))
            
            text_label.bind("<Button-1>", lambda e, n=button_name: self.start_location_click(e, n))
            text_label.bind("<B1-Motion>", lambda e, f=frame: self.drag_location(e, f))
            text_label.bind("<ButtonRelease-1>", lambda e, n=button_name: self.handle_location_release(e, n))
            text_label.bind("<Button-3>", lambda e, n=button_name: self.show_location_menu(e, n))
            print("[MapPlayer] Finished binding events")  # Debug print
            
            # Save world state after adding location
            if self.current_world:
                self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                  self.location_buttons, self.tokens)
            
            # Reset placing flag
            self.placing_location = False
            self.canvas.config(cursor="")
            print("[MapPlayer] place_location completed successfully")  # Debug print
            
        except Exception as e:
            print(f"[MapPlayer] Error placing location: {e}")
            messagebox.showerror("Error", f"Failed to place location: {str(e)}")

    def drag_location(self, event, frame):
        """Handle dragging of a location button"""
        try:
            # Find which button this frame belongs to
            button_name = None
            for name, info in self.location_buttons.items():
                if info["frame"] == frame:
                    button_name = name
                    info["dragging"] = True  # Set dragging flag
                    break
                    
            if not button_name:
                return
                
            # Get new position
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Update button position
            info = self.location_buttons[button_name]
            info["x"] = x
            info["y"] = y
            
            # Move the window
            self.canvas.coords(info["window"], x, y)
            
        except Exception as e:
            print(f"[MapPlayer] Error dragging location: {e}")
            
    def start_location_click(self, event, button_name):
        """Handle initial click on a location button"""
        try:
            if button_name in self.location_buttons:
                info = self.location_buttons[button_name]
                info["clicked"] = True
                info["dragging"] = False
                info["click_x"] = event.x
                info["click_y"] = event.y
        except Exception as e:
            print(f"[MapPlayer] Error starting location click: {e}")
            
    def handle_location_release(self, event, button_name):
        """Handle mouse release on a location button"""
        try:
            button_info = self.location_buttons[button_name]
            
            if button_info["clicked"]:
                if not button_info["dragging"]:
                    if abs(event.x - button_info["click_x"]) > 5 or abs(event.y - button_info["click_y"]) > 5:
                        button_info["dragging"] = True
                
                if button_info["dragging"]:
                    # Get current position
                    x = self.canvas.canvasx(event.x)
                    y = self.canvas.canvasy(event.y)
                    
                    # Update button position
                    info = self.location_buttons[button_name]
                    info["x"] = x
                    info["y"] = y
                    
                    # Move the window
                    self.canvas.coords(info["window"], x, y)
                    
                    # Save world state after moving
                    if self.current_world:
                        self.world_manager.save_world_state(self.current_world, self.current_map,
                                                          self.location_buttons, self.tokens)
                else:
                    # Handle click
                    self.handle_location_click(button_name)
                    
            button_info["clicked"] = False
            button_info["dragging"] = False
            
        except Exception as e:
            print(f"[MapPlayer] Error in handle_location_release: {e}")
            
    def handle_location_click(self, button_name):
        """Handle clicking on a location button"""
        try:
            print(f"[MapPlayer] Location clicked: {button_name}")
            print(f"[MapPlayer] Current location_buttons: {list(self.location_buttons.keys())}")
            button_info = self.location_buttons[button_name]
            print(f"[MapPlayer] Button info: {button_info}")
            
            if button_info["linked_map"]:
                print(f"[MapPlayer] Loading linked map: {button_info['linked_map']}")
                # Save current map state
                if self.current_world:
                    self.world_manager.save_world_state(self.current_world, self.current_map,
                                                      self.location_buttons, self.tokens)
                
                # Load linked map
                self.load_map(button_info["linked_map"])
                
                # Update window title
                if self.current_world:
                    self.root.title(f"Map Player - {os.path.basename(self.current_world)} - {os.path.basename(self.current_map)}")
            else:
                print("[MapPlayer] No linked map, showing link menu")
                self.link_map_to_location(button_name)
                
        except Exception as e:
            print(f"[MapPlayer] Error handling location click: {e}")
            
    def show_location_menu(self, event, button_name):
        """Show right-click menu for a location button"""
        try:
            menu = tk.Menu(self.root, tearoff=0)
            
            # Add menu items
            menu.add_command(label="Link Map...", command=lambda: self.link_map_to_location(button_name))
            menu.add_command(label="Rename...", command=lambda: self.rename_location(button_name))
            menu.add_separator()
            menu.add_command(label="Delete", command=lambda: self.delete_location(button_name))
            
            # Show menu at mouse position
            menu.post(event.x_root, event.y_root)
            
        except Exception as e:
            print(f"[MapPlayer] Error showing location menu: {e}")
            
    def link_map_to_location(self, button_name):
        """Link a map file to a location button"""
        try:
            if button_name not in self.location_buttons:
                raise ValueError(f"Button {button_name} not found")
                
            # Select map to link
            file_path = filedialog.askopenfilename(
                title="Select Map File",
                initialdir=os.path.join("D:", "WorldWiki", "dist", "Places"),
                filetypes=[
                    ("Map files", "*.map;*.MAP"),
                    ("PNG files", "*.png")
                ]
            )
            
            if not file_path:
                return
                
            # Get new name from map file
            new_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Update button info
            info = self.location_buttons[button_name]
            
            # Update text label
            info["text_label"].configure(text=new_name)
            
            # Store under new name if different
            if button_name != new_name:
                # First remove old entry
                del self.location_buttons[button_name]
                # Then add new entry
                self.location_buttons[new_name] = info
                
                # Update event bindings with new name
                frame = info["frame"]
                image_label = info["image_label"]
                text_label = info["text_label"]
                
                # Rebind events to frame and its children with new name
                frame.bind("<Button-1>", lambda e: self.start_location_click(e, new_name))
                frame.bind("<B1-Motion>", lambda e: self.drag_location(e, frame))
                frame.bind("<ButtonRelease-1>", lambda e: self.handle_location_release(e, new_name))
                frame.bind("<Button-3>", lambda e: self.show_location_menu(e, new_name))
                
                # Rebind events to the labels with new name
                image_label.bind("<Button-1>", lambda e: self.start_location_click(e, new_name))
                image_label.bind("<B1-Motion>", lambda e: self.drag_location(e, frame))
                image_label.bind("<ButtonRelease-1>", lambda e: self.handle_location_release(e, new_name))
                image_label.bind("<Button-3>", lambda e: self.show_location_menu(e, new_name))
                
                text_label.bind("<Button-1>", lambda e: self.start_location_click(e, new_name))
                text_label.bind("<B1-Motion>", lambda e: self.drag_location(e, frame))
                text_label.bind("<ButtonRelease-1>", lambda e: self.handle_location_release(e, new_name))
                text_label.bind("<Button-3>", lambda e: self.show_location_menu(e, new_name))
                
                print(f"[MapPlayer] Updated event bindings for button {new_name}")
            
            # Update linked map
            info["linked_map"] = file_path
            print(f"[MapPlayer] Successfully linked map {file_path} to button {new_name}")
            
            # Save world state after linking
            if self.current_world:
                self.world_manager.save_world_state(self.current_world, self.current_map,
                                                  self.location_buttons, self.tokens)
                
        except Exception as e:
            print(f"[MapPlayer] Error linking map: {e}")
            messagebox.showerror("Error", f"Failed to link map: {str(e)}")
            
    def rename_location(self, old_name):
        """Rename a location button"""
        try:
            new_name = simpledialog.askstring("Rename Location", "Enter new name:", initialvalue=old_name)
            
            if new_name and new_name != old_name:
                # Update button text
                self.location_buttons[old_name]["text_label"].config(text=new_name)
                
                # Update dictionary
                self.location_buttons[new_name] = self.location_buttons.pop(old_name)
                
                # Save world state after renaming
                if self.current_world:
                    self.world_manager.save_world_state(self.current_world, self.current_map,
                                                      self.location_buttons, self.tokens)
                                                      
        except Exception as e:
            print(f"[MapPlayer] Error renaming location: {e}")
            messagebox.showerror("Error", f"Failed to rename location: {str(e)}")
            
    def delete_location(self, button_name):
        """Delete a location button"""
        try:
            if messagebox.askyesno("Confirm Delete", f"Delete location '{button_name}'?"):
                # Remove window from canvas
                self.canvas.delete(self.location_buttons[button_name]["window"])
                
                # Remove from dictionary
                del self.location_buttons[button_name]
                
                # Save world state after deleting
                if self.current_world:
                    self.world_manager.save_world_state(self.current_world, self.current_map,
                                                      self.location_buttons, self.tokens)
                                                      
        except Exception as e:
            print(f"[MapPlayer] Error deleting location: {e}")
            messagebox.showerror("Error", f"Failed to delete location: {str(e)}")
            
    def start_add_location(self):
        """Start the process of adding a location"""
        try:
            if not hasattr(self, 'image') or not self.image:
                messagebox.showerror("Error", "Please load a map first")
                return
                
            self.placing_location = True
            self.canvas.config(cursor="crosshair")
            
        except Exception as e:
            print(f"[MapPlayer] Error starting location add: {e}")
            messagebox.showerror("Error", f"Failed to start adding location: {str(e)}")
            
    def create_world(self):
        """Create a new world"""
        try:
            # Ask for world file location
            world_file = filedialog.asksaveasfilename(
                title="Create New World",
                initialdir=os.path.join("D:", "WorldWiki", "dist", "Places"),
                defaultextension=".world",
                filetypes=[("World files", "*.world")]
            )
            
            if world_file:
                # Create empty world data
                world_data = {
                    "maps": {},
                    "current_map": None
                }
                
                # Save world file
                with open(world_file, 'w') as f:
                    json.dump(world_data, f, indent=4)
                    
                # Set as current world
                self.current_world = world_file
                
                # Update window title
                self.root.title(f"Map Player - {os.path.basename(world_file)}")
                
        except Exception as e:
            print(f"[MapPlayer] Error creating world: {e}")
            messagebox.showerror("Error", f"Failed to create world: {str(e)}")
            
    def save_world(self):
        """Save the current world state"""
        try:
            if not self.current_world:
                messagebox.showerror("Error", "No world is currently loaded")
                return
                
            # Save world state
            self.world_manager.save_world_state(self.current_world, self.current_map, 
                                              self.location_buttons, self.tokens)
            
            messagebox.showinfo("Success", "World saved successfully")
            
        except Exception as e:
            print(f"[MapPlayer] Error saving world: {e}")
            messagebox.showerror("Error", f"Failed to save world: {str(e)}")
            
    def select_token_at(self, x, y):
        """Select a token at the given coordinates"""
        # Convert screen coordinates to canvas coordinates
        x = self.canvas.canvasx(x)
        y = self.canvas.canvasy(y)
        
        # Find overlapping items
        items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        # Check each item
        for item in items:
            # Check if this item belongs to a token
            tags = self.canvas.gettags(item)
            if "token" in tags:
                for tag in tags:
                    if tag != "token" and tag in self.tokens:
                        # Deselect previous token
                        if self.selected_token and self.selected_token in self.tokens:
                            self.tokens[self.selected_token].selected = False
                        
                        # Select new token
                        self.selected_token = tag
                        self.tokens[tag].selected = True
                        return
        
        # If we get here, no token was found
        if self.selected_token and self.selected_token in self.tokens:
            self.tokens[self.selected_token].selected = False
        self.selected_token = None
        return False
        
    def show_character_data(self):
        """Show character data for selected token"""
        try:
            print(f"[MapPlayer] Showing character data for {self.selected_token}")  # Debug print
            if not self.selected_token or self.selected_token not in self.tokens:
                print("[MapPlayer] No token selected")  # Debug print
                return
                
            token = self.tokens[self.selected_token]
            print(f"[MapPlayer] Token stats: {token.token_stats.stats}")  # Debug print
            
            # If info box exists but window is destroyed, remove reference
            if hasattr(token, 'info_box') and token.info_box and not token.info_box.window.winfo_exists():
                print("[MapPlayer] Removing old info box reference")  # Debug print
                token.info_box = None
            
            # If info box already exists, just focus it
            if hasattr(token, 'info_box') and token.info_box:
                print("[MapPlayer] Info box exists, focusing window")  # Debug print
                token.info_box.window.focus_force()
                return
                
            # Create new info box
            print("[MapPlayer] Creating new info box")  # Debug print
            token.info_box = CharacterInfoBox(self.root, token)
            
            # Position info box near token
            if token.info_box and token.info_box.window.winfo_exists():
                print("[MapPlayer] Positioning info box")  # Debug print
                canvas_x = self.canvas.winfo_rootx()
                canvas_y = self.canvas.winfo_rooty()
                token_bbox = self.canvas.bbox(token.image_item)
                if token_bbox:
                    x = canvas_x + token_bbox[2] + 10  # Place to right of token
                    y = canvas_y + token_bbox[1]  # Align with top of token
                    token.info_box.window.geometry(f"+{x}+{y}")
                    
        except Exception as e:
            print(f"[MapPlayer] Error showing character data: {e}")  # Debug print
            if 'token' in locals() and hasattr(token, 'info_box'):
                token.info_box = None

    def handle_token_click(self, event):
        """Handle clicking on a token"""
        try:
            print("[MapPlayer] Token clicked")  # Debug print
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Find items at click position - increase overlap area for better detection
            items = self.canvas.find_overlapping(x-10, y-10, x+10, y+10)
            print(f"[MapPlayer] Found items at click: {items}")  # Debug print
            
            # Get all token items at click position
            token_items = []
            for item in items:
                tags = self.canvas.gettags(item)
                print(f"[MapPlayer] Item {item} tags: {tags}")  # Debug print
                if "token" in tags:
                    for tag in tags:
                        if tag != "token" and tag in self.tokens:
                            token_items.append((item, tag))
            
            # If we found any tokens, select the top one
            if token_items:
                # Get the last (top) token
                item, tag = token_items[-1]
                
                # Deselect previous token
                if self.selected_token:
                    self.tokens[self.selected_token].selected = False
                
                # Select new token
                self.selected_token = tag
                token = self.tokens[tag]
                token.selected = True
                print(f"[MapPlayer] Selected token: {tag}")  # Debug print
                
                # Store offset for dragging
                self.drag_offset_x = token.x - x
                self.drag_offset_y = token.y - y
                self.dragging = True
                
                return
                            
        except Exception as e:
            print(f"[MapPlayer] Error handling token click: {e}")  # Debug print
            
    def handle_token_right_click(self, event):
        """Handle right-clicking on a token"""
        try:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Find items at click position
            items = self.canvas.find_overlapping(x-10, y-10, x+10, y+10)
            
            for item in items:
                tags = self.canvas.gettags(item)
                if "token" in tags:
                    for tag in tags:
                        if tag != "token" and tag in self.tokens:
                            # Select the token
                            if self.selected_token:
                                self.tokens[self.selected_token].selected = False
                            self.selected_token = tag
                            self.tokens[tag].selected = True
                            
                            # Show character data
                            self.show_character_data()
                            return
                            
        except Exception as e:
            print(f"[MapPlayer] Error handling token right click: {e}")  # Debug print
            
    def handle_token_motion(self, event):
        """Handle dragging a token"""
        try:
            if not self.dragging or not self.selected_token:
                return
                
            token = self.tokens[self.selected_token]
            
            # Get canvas coordinates
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Calculate target position with offset
            target_x = x + self.drag_offset_x
            target_y = y + self.drag_offset_y
            
            # Move token
            token.move_to(target_x, target_y)
            
        except Exception as e:
            print(f"[MapPlayer] Error moving token: {e}")  # Debug print
            
    def handle_token_release(self, event):
        """Handle releasing a token"""
        try:
            if self.dragging and self.selected_token:
                self.dragging = False
                print(f"[MapPlayer] Token {self.selected_token} released")  # Debug print
                
        except Exception as e:
            print(f"[MapPlayer] Error releasing token: {e}")  # Debug print
            
    def toggle_token_grid_snap(self):
        """Toggle grid snapping for the selected token"""
        if self.selected_token:
            self.tokens[self.selected_token].snap_to_grid = not self.tokens[self.selected_token].snap_to_grid
            # Update info box if open
            if self.tokens[self.selected_token].info_box:
                self.tokens[self.selected_token].info_box.update_grid_snap()
                
    def toggle_token_death(self):
        """Toggle the death state of the selected token"""
        if self.selected_token:
            token = self.tokens[self.selected_token]
            token.is_dead = not token.is_dead
            token.draw()  # Redraw the token with updated death state
            
            # Update any open info box
            if token.info_box:
                token.info_box.update_death_state(token.is_dead)
                
    def delete_selected_token(self):
        """Delete the selected token"""
        if self.selected_token:
            # Remove from canvas
            self.canvas.delete(self.tokens[self.selected_token].image_item)
            
            # Remove from list
            del self.tokens[self.selected_token]
            
            # Clear selection
            self.selected_token = None
            
            # Save world state after deleting token
            if self.current_world:
                self.world_manager.save_world_state(self.current_world, self.current_map, 
                                                  self.location_buttons, self.tokens)

    def open_token_creator(self):
        """Open the token creator dialog"""
        try:
            # Run token_manager.py in a new process
            subprocess.Popen([sys.executable, "token_manager.py"], 
                           cwd="D:/WorldWiki/Grid map")
        except Exception as e:
            print(f"[MapPlayer] Error opening token creator: {e}")
            messagebox.showerror("Error", f"Failed to open token creator: {e}")
            
    def open_map_creator(self):
        """Open the map creator dialog"""
        try:
            # Run grid_map.py in a new process
            subprocess.Popen([sys.executable, "grid_map.py"], 
                           cwd="D:/WorldWiki/Grid map")
        except Exception as e:
            print(f"[MapPlayer] Error opening map creator: {e}")
            messagebox.showerror("Error", f"Failed to open map creator: {e}")
            
    def setup_ui(self):
        """Setup the UI elements"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu panel frame
        self.menu_panel = ttk.Frame(self.main_frame, width=150)
        self.menu_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_panel.pack_propagate(False)  # Prevent frame from shrinking
        
        # Add tool buttons to panel
        ttk.Button(self.menu_panel, text="Token Creator", command=self.open_token_creator).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(self.menu_panel, text="Map Creator", command=self.open_map_creator).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(self.menu_panel, text="Add Location", command=self.start_add_location).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(self.menu_panel, text="Add Notes", command=self.add_notes).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(self.menu_panel, text="Link Map", command=self.link_map).pack(fill=tk.X, padx=5, pady=2)
        
        # Add load map button
        ttk.Button(self.menu_panel, text="Load Map", command=self.load_map).pack(fill=tk.X, padx=5, pady=2)
        
        # Add token button
        ttk.Button(self.menu_panel, text="Add Token", command=self.add_token).pack(fill=tk.X, padx=5, pady=2)
        
        # Create canvas frame
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(canvas_frame, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for tokens
        self.canvas.tag_bind("token", "<Button-1>", self.handle_token_click)
        self.canvas.tag_bind("token", "<B1-Motion>", self.handle_token_motion)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.handle_token_release)
        self.canvas.tag_bind("token", "<Button-3>", self.handle_token_right_click)
        
        # Bind canvas click for token placement
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Right button for map scrolling
        self.canvas.bind("<Button-3>", self.start_right_scroll)
        self.canvas.bind("<B3-Motion>", self.handle_right_scroll)
        self.canvas.bind("<ButtonRelease-3>", self.stop_right_scroll)
        
        # Bind keyboard events
        self.root.bind("<Left>", lambda e: self.move_selected_token("left"))
        self.root.bind("<Right>", lambda e: self.move_selected_token("right"))
        self.root.bind("<Up>", lambda e: self.move_selected_token("up"))
        self.root.bind("<Down>", lambda e: self.move_selected_token("down"))

    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # World submenu
        world_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="World", menu=world_menu)
        world_menu.add_command(label="Create New World", command=self.create_world)
        world_menu.add_command(label="Load World", command=self.load_world)
        world_menu.add_command(label="Save World", command=self.save_world)
        
        file_menu.add_command(label="Load Map", command=self.load_map)
        file_menu.add_command(label="Add Token", command=self.add_token)
        file_menu.add_command(label="Add Location", command=self.start_add_location)
        file_menu.add_command(label="Add Notes", command=self.add_notes)
        file_menu.add_command(label="Character Data", command=self.show_character_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Grid", variable=self.show_grid, command=self.update_canvas)
        
        # Map menu
        map_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Map", menu=map_menu)
        map_menu.add_command(label="Link Map", command=self.link_map)

    def start_right_scroll(self, event):
        """Start right-click scrolling"""
        self.right_click_scroll = True
        self.last_x = event.x
        self.last_y = event.y
        
    def handle_right_scroll(self, event):
        """Handle right-click scrolling with dead zone"""
        if not hasattr(self, 'image') or not self.image or not hasattr(self, 'right_click_scroll') or not self.right_click_scroll:
            return
            
        # Edge scrolling
        margin = 100  # pixels from edge to start scrolling
        dead_zone = 0.4  # percentage of screen for dead zone (40%)
        speed = 0.0004  # fraction of view to scroll per update
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calculate dead zone boundaries
        dead_zone_left = width * dead_zone
        dead_zone_right = width * (1 - dead_zone)
        dead_zone_top = height * dead_zone
        dead_zone_bottom = height * (1 - dead_zone)
        
        # Get current scroll position
        x_view = self.canvas.xview()
        y_view = self.canvas.yview()
        x_pos = x_view[0]  # Position of left edge of view (0.0 to 1.0)
        y_pos = y_view[0]  # Position of top edge of view (0.0 to 1.0)
        
        # Calculate new scroll positions
        new_x = x_pos
        new_y = y_pos
        
        # Check horizontal scrolling (outside dead zone)
        if event.x < dead_zone_left:
            # Left edge scrolling
            if event.x < margin:
                new_x = max(0.0, x_pos - speed)
        elif event.x > dead_zone_right:
            # Right edge scrolling
            if event.x > width - margin:
                new_x = min(1.0, x_pos + speed)
            
        # Check vertical scrolling (outside dead zone)
        if event.y < dead_zone_top:
            # Top edge scrolling
            if event.y < margin:
                new_y = max(0.0, y_pos - speed)
        elif event.y > dead_zone_bottom:
            # Bottom edge scrolling
            if event.y > height - margin:
                new_y = min(1.0, y_pos + speed)
            
        # Apply scrolling if position changed
        if new_x != x_pos or new_y != y_pos:
            self.canvas.xview_moveto(new_x)
            self.canvas.yview_moveto(new_y)
            # Schedule next update
            self.root.after(16, lambda e=event: self.handle_right_scroll(e))
            
    def stop_right_scroll(self, event):
        """Stop right-click scrolling"""
        self.right_click_scroll = False

if __name__ == "__main__":
    root = tk.Tk()
    app = MapPlayer(root)
    app.create_menu()
    root.mainloop()
