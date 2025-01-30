import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

class WorldManager:
    def __init__(self):
        self.worlds_dir = os.path.join("D:", "WorldWiki", "Grid map", "worlds")
        if not os.path.exists(self.worlds_dir):
            os.makedirs(self.worlds_dir)

    def create_world(self):
        """Create a new world and return the world file path"""
        try:
            # Ask for world name
            dialog = tk.Toplevel()
            dialog.title("Create New World")
            dialog.geometry("300x100")
            dialog.transient()
            dialog.grab_set()

            tk.Label(dialog, text="World Name:").pack(pady=5)
            name_var = tk.StringVar()
            entry = tk.Entry(dialog, textvariable=name_var)
            entry.pack(pady=5)

            world_path = [None]  # Use list to store result

            def on_ok():
                name = name_var.get().strip()
                if name:
                    file_path = os.path.join(self.worlds_dir, f"{name}.world")
                    if os.path.exists(file_path):
                        messagebox.showerror("Error", "A world with this name already exists!")
                        return
                    
                    # Create initial world data
                    world_data = {
                        "name": name,
                        "current_map": None,
                        "maps": {},
                        "locations": {},
                        "tokens": {}
                    }
                    
                    # Save world file
                    with open(file_path, 'w') as f:
                        json.dump(world_data, f, indent=4)
                    
                    world_path[0] = file_path
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Please enter a world name!")

            tk.Button(dialog, text="Create", command=on_ok).pack(pady=5)
            
            dialog.wait_window()
            return world_path[0]
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create world: {str(e)}")
            return None

    def load_world(self):
        """Load an existing world and return the world file path"""
        try:
            file_path = filedialog.askopenfilename(
                title="Load World",
                initialdir=self.worlds_dir,
                filetypes=[("World files", "*.world")]
            )
            
            if file_path and os.path.exists(file_path):
                return file_path
            return None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load world: {str(e)}")
            return None

    def save_world_state(self, world_file, current_map, locations, tokens):
        """Save the current world state"""
        try:
            if not world_file:
                return False
                
            # Load existing world data
            with open(world_file, 'r') as f:
                world_data = json.load(f)
            
            # Get the map key (use relative path from world file)
            world_dir = os.path.dirname(world_file)
            if current_map:
                try:
                    map_key = os.path.relpath(current_map, world_dir)
                except ValueError:
                    map_key = current_map
            else:
                map_key = None
            
            # Update current map
            world_data["current_map"] = map_key
            
            # Initialize map data if it doesn't exist
            if map_key and map_key not in world_data["maps"]:
                world_data["maps"][map_key] = {
                    "locations": {},
                    "tokens": {}
                }
            
            if map_key:
                # Save locations for this map
                world_data["maps"][map_key]["locations"] = {}
                for name, info in locations.items():
                    world_data["maps"][map_key]["locations"][name] = {
                        "x": info["x"],
                        "y": info["y"],
                        "text": info["text_label"].cget("text"),
                        "linked_map": info["linked_map"]
                    }
                
                # Save tokens for this map
                world_data["maps"][map_key]["tokens"] = {}
                for name, token in tokens.items():
                    world_data["maps"][map_key]["tokens"][name] = {
                        "x": token.x,
                        "y": token.y,
                        "name": token.name,
                        "stats": token.token_stats.stats if hasattr(token, 'token_stats') else {}
                    }
            
            # Save to file
            with open(world_file, 'w') as f:
                json.dump(world_data, f, indent=4)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save world state: {str(e)}")
            return False

    def load_world_state(self, world_file):
        """Load a world state and return the data"""
        try:
            if not world_file or not os.path.exists(world_file):
                return None
            
            with open(world_file, 'r') as f:
                world_data = json.load(f)
            
            # Convert relative paths to absolute
            world_dir = os.path.dirname(world_file)
            if world_data["current_map"]:
                world_data["current_map"] = os.path.normpath(os.path.join(world_dir, world_data["current_map"]))
            
            # Convert all linked maps to absolute paths
            for map_key, map_data in world_data["maps"].items():
                for loc_name, loc_data in map_data["locations"].items():
                    if loc_data["linked_map"]:
                        loc_data["linked_map"] = os.path.normpath(os.path.join(world_dir, loc_data["linked_map"]))
            
            return world_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load world state: {str(e)}")
            return None

    def get_map_state(self, world_file, map_path):
        """Get the state for a specific map"""
        try:
            if not world_file or not os.path.exists(world_file):
                return None
            
            with open(world_file, 'r') as f:
                world_data = json.load(f)
            
            # Get relative path for map
            world_dir = os.path.dirname(world_file)
            try:
                map_key = os.path.relpath(map_path, world_dir)
            except ValueError:
                map_key = map_path
            
            if map_key in world_data["maps"]:
                map_data = world_data["maps"][map_key]
                
                # Convert linked maps to absolute paths
                for loc_data in map_data["locations"].values():
                    if loc_data["linked_map"]:
                        loc_data["linked_map"] = os.path.normpath(os.path.join(world_dir, loc_data["linked_map"]))
                
                return map_data
            return None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get map state: {str(e)}")
            return None
