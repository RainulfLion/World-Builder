import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import shutil
from datetime import datetime

class TokenStats:
    def __init__(self, name=None, data=None):
        """Initialize token stats with defaults or from data"""
        self.name = name
        self.stats = {}
        self.notes = ''
        self.image_path = None
        self.json_path = None  # Store the JSON path for verification
        
        print(f"[TokenStats] Initializing for {name}")  # Debug print
        
        # If data is provided directly, use it
        if data:
            print(f"[TokenStats] Using provided data: {data}")  # Debug print
            self.stats = data.get('stats', {})
            self.notes = data.get('notes', '')
            self.image_path = data.get('image_path', None)
            
        # If only name is provided, try to load from JSON file
        elif name:
            # Try exact name first
            json_path = os.path.join("D:/WorldWiki/Grid map/tokens", f"{name}.json")
            # If not found, try case-insensitive search
            if not os.path.exists(json_path):
                token_dir = "D:/WorldWiki/Grid map/tokens"
                if os.path.exists(token_dir):
                    for file in os.listdir(token_dir):
                        if file.lower() == f"{name.lower()}.json":
                            json_path = os.path.join(token_dir, file)
                            break
            
            self.json_path = json_path  # Store the JSON path
            print(f"[TokenStats] Looking for JSON file: {json_path}")  # Debug print
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        print(f"[TokenStats] Loaded data from JSON: {data}")  # Debug print
                        if 'stats' in data:
                            self.stats = data['stats']
                            print(f"[TokenStats] Loaded stats from JSON: {self.stats}")  # Debug print
                        else:
                            print(f"[TokenStats] No 'stats' key found in JSON data")  # Debug print
                            self._set_defaults()
                        self.notes = data.get('notes', '')
                        self.image_path = data.get('image_path', None)
                except Exception as e:
                    error_msg = f"Error loading token stats from {json_path}: {e}"
                    print(f"[TokenStats] {error_msg}")  # Debug print
                    messagebox.showerror("Error Loading Token", error_msg)
                    self._set_defaults()
            else:
                error_msg = f"JSON file not found: {json_path}\nUsing default stats."
                print(f"[TokenStats] {error_msg}")  # Debug print
                messagebox.showwarning("Token Data Not Found", error_msg)
                self._set_defaults()
        else:
            print("[TokenStats] No name or data provided, using defaults")  # Debug print
            self._set_defaults()
            
    def _set_defaults(self):
        """Set default stats"""
        print("[TokenStats] Setting default stats")  # Debug print
        self.stats = {
            'Name': self.name if self.name else '',
            'HP': '10',
            'Max HP': '10',
            'AC': '10',
            'Initiative': '+0',
            'Speed': '30',
            'Strength': '10',
            'Dexterity': '10',
            'Constitution': '10',
            'Intelligence': '10',
            'Wisdom': '10',
            'Charisma': '10',
            'Proficiency': '+2',
            'Level': '1'
        }
        self.notes = 'Equipment:\n'

    def to_dict(self):
        """Convert token stats to dictionary"""
        return {
            'name': self.name,
            'stats': self.stats,
            'notes': self.notes,
            'image_path': self.image_path
        }

    def from_dict(self, data):
        """Load token stats from dictionary"""
        self.name = data['name']
        self.stats = data['stats']
        self.notes = data.get('notes', '')
        self.image_path = data.get('image_path')

    def verify_stats(self):
        """Verify that current stats match the JSON file"""
        if not self.json_path or not os.path.exists(self.json_path):
            return False
            
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                json_stats = data.get('stats', {})
                
                # Compare each stat
                for key, value in json_stats.items():
                    if str(self.stats.get(key)) != str(value):
                        error_msg = f"Stat mismatch for {key}: Expected {value}, got {self.stats.get(key)}"
                        print(f"[TokenStats] {error_msg}")
                        messagebox.showerror("Stats Mismatch", error_msg)
                        return False
                        
                return True
        except Exception as e:
            error_msg = f"Error verifying stats: {e}"
            print(f"[TokenStats] {error_msg}")
            messagebox.showerror("Error", error_msg)
            return False

    def save_to_json(self):
        """Save stats to JSON file"""
        if not self.name:
            return False
            
        json_path = os.path.join("D:/WorldWiki/Grid map/tokens", f"{self.name}.json")
        try:
            data = {
                'stats': self.stats,
                'notes': self.notes,
                'image_path': self.image_path
            }
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[TokenStats] Saved stats to {json_path}")  # Debug print
            return True
        except Exception as e:
            print(f"[TokenStats] Error saving stats: {e}")  # Debug print
            return False

class TokenEditor:
    def __init__(self, root):
        """Initialize the token editor"""
        self.root = root
        self.root.title("Token Editor")
        self.token_dir = "D:/WorldWiki/Grid map/tokens"
        self.token_types_dir = "D:/WorldWiki/Grid map/token_types"
        self.current_token = None
        self.token_image = None
        self.basic_entries = {}
        self.stat_entries = {}
        
        # Create frames
        self.create_frames()
        
        # Load existing tokens
        self.load_token_list()

    def create_frames(self):
        """Create the main frames for the token editor"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left frame for token list
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Token list
        ttk.Label(left_frame, text="Tokens:").pack(fill=tk.X)
        self.token_list = ttk.Treeview(left_frame, selectmode='browse', height=20)
        self.token_list.pack(fill=tk.BOTH, expand=True)
        
        # Buttons under token list
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="New", command=self.show_new_token_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Load", command=self.load_token).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_token).pack(side=tk.LEFT, padx=2)
        
        # Right frame for token details
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Image section
        image_frame = ttk.LabelFrame(right_frame, text="Token Image", padding="5")
        image_frame.pack(fill=tk.X, pady=5)
        
        self.image_label = ttk.Label(image_frame, text="No Image")
        self.image_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(image_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        
        # Stats section
        stats_frame = ttk.LabelFrame(right_frame, text="Stats", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Add new stat button
        add_stat_frame = ttk.Frame(stats_frame)
        add_stat_frame.pack(fill=tk.X, pady=5)
        self.new_stat_name = ttk.Entry(add_stat_frame)
        self.new_stat_name.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(add_stat_frame, text="Add Stat", command=self.add_stat).pack(side=tk.RIGHT, padx=5)
        
        # Scrollable frame for stats
        stats_canvas = tk.Canvas(stats_frame)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=stats_canvas.yview)
        self.scrollable_stats_frame = ttk.Frame(stats_canvas)
        
        self.scrollable_stats_frame.bind(
            "<Configure>",
            lambda e: stats_canvas.configure(scrollregion=stats_canvas.bbox("all"))
        )
        
        stats_canvas.create_window((0, 0), window=self.scrollable_stats_frame, anchor="nw")
        stats_canvas.configure(yscrollcommand=stats_scrollbar.set)
        
        stats_canvas.pack(side="left", fill="both", expand=True)
        stats_scrollbar.pack(side="right", fill="y")
        
        # Notes section
        notes_frame = ttk.LabelFrame(right_frame, text="Notes", padding="5")
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.notes_text = tk.Text(notes_frame, height=10)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Save button
        ttk.Button(right_frame, text="Save Token", command=self.save_token).pack(fill=tk.X, pady=5)

    def show_new_token_dialog(self):
        """Show dialog for creating a new token with type selection"""
        dialog = NewTokenDialog(self.root, self.token_types_dir)
        if dialog.result:
            self.create_new_token(dialog.result['name'], dialog.result['type'])

    def create_new_token(self, name, token_type=None):
        """Create a new token with optional type template"""
        self.current_token = TokenStats(name)
        
        if token_type:
            # Load token type template
            type_file = os.path.join(self.token_types_dir, f"{token_type}.json")
            try:
                with open(type_file, 'r') as f:
                    template = json.load(f)
                    self.current_token.stats = template['stats'].copy()
                    self.current_token.stats['Name'] = name
            except Exception as e:
                print(f"Error loading token type: {e}")
                
        self.token_image = None
        self.image_label.configure(image='', text="No Image")
        self.update_ui_from_token()

    def add_stat(self):
        """Add a new stat to the token"""
        stat_name = self.new_stat_name.get().strip()
        if not stat_name:
            messagebox.showwarning("Warning", "Please enter a stat name")
            return
            
        if stat_name in self.stat_entries:
            messagebox.showwarning("Warning", f"Stat '{stat_name}' already exists")
            return
            
        self.create_stat_row(stat_name, "0")
        self.new_stat_name.delete(0, tk.END)

    def create_stat_row(self, stat_name, stat_value):
        """Create a row for a stat with name and value"""
        row_frame = ttk.Frame(self.scrollable_stats_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        # Stat name (now as a label)
        name_label = ttk.Label(row_frame, text=stat_name)
        name_label.pack(side=tk.LEFT, padx=5)
        
        # Stat value
        value_var = tk.StringVar(value=stat_value)
        value_entry = ttk.Entry(row_frame, textvariable=value_var)
        value_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Delete button
        delete_btn = ttk.Button(row_frame, text="X", width=3,
                              command=lambda: self.delete_stat(stat_name, row_frame))
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Store references
        self.stat_entries[stat_name] = {
            'frame': row_frame,
            'value': value_var
        }

    def delete_stat(self, stat_name, row_frame):
        """Delete a stat from the token"""
        if messagebox.askyesno("Confirm Delete", f"Delete stat '{stat_name}'?"):
            row_frame.destroy()
            del self.stat_entries[stat_name]

    def update_ui_from_token(self):
        """Update the UI from the current token"""
        if not self.current_token:
            return
            
        # Clear existing stats
        for stat_info in self.stat_entries.values():
            stat_info['frame'].destroy()
        self.stat_entries.clear()
        
        # Add all stats from token
        for stat_name, stat_value in self.current_token.stats.items():
            self.create_stat_row(stat_name, stat_value)
            
        # Update notes
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', self.current_token.notes)
        
        # Update image if exists
        if hasattr(self.current_token, 'image_path') and self.current_token.image_path:
            self.display_image(self.current_token.image_path)

    def save_token(self):
        """Save the current token"""
        try:
            if not self.current_token:
                messagebox.showwarning("Warning", "No token selected")
                return
                
            # Get token name
            token_name = None
            for stat_name, stat_info in self.stat_entries.items():
                if stat_name == "Name":
                    token_name = stat_info['value'].get()
                    break
                    
            if not token_name:
                messagebox.showwarning("Warning", "Token must have a Name stat")
                return
                
            # Update token stats
            self.current_token.stats = {}
            for stat_name, stat_info in self.stat_entries.items():
                self.current_token.stats[stat_name] = stat_info['value'].get()
                
            # Update notes
            self.current_token.notes = self.notes_text.get('1.0', tk.END).strip()
            
            # Verify stats against JSON file
            if not self.current_token.verify_stats():
                return
                
            # Save token data
            token_data = {
                'stats': self.current_token.stats,
                'notes': self.current_token.notes
            }
            
            if hasattr(self.current_token, 'image_path'):
                token_data['image_path'] = self.current_token.image_path
                
            # Save to file
            json_path = os.path.join(self.token_dir, f"{token_name}.json")
            with open(json_path, 'w') as f:
                json.dump(token_data, f, indent=4)
                
            messagebox.showinfo("Success", "Token saved successfully")
            self.load_token_list()
            
        except Exception as e:
            print(f"Error saving token: {e}")
            messagebox.showerror("Error", f"Failed to save token: {str(e)}")

    def load_image(self):
        """Load an image file for the token"""
        file_path = filedialog.askopenfilename(
            title="Select Token Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")],
            initialdir=self.token_dir
        )
        
        if file_path:
            try:
                # Convert to relative path if in tokens directory
                rel_path = os.path.relpath(file_path, self.token_dir)
                if not rel_path.startswith('..'):
                    file_path = rel_path
                
                # Save image path
                if not hasattr(self.current_token, 'image_path'):
                    self.current_token.image_path = ''
                self.current_token.image_path = file_path
                
                # Display image
                self.display_image(file_path)
                print(f"Loaded image: {file_path}")  # Debug print
                
            except Exception as e:
                print(f"Error loading image: {e}")  # Debug print
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_image(self, image_path):
        """Display the token image"""
        try:
            # Get full path if relative
            if not os.path.isabs(image_path):
                image_path = os.path.join(self.token_dir, image_path)
            
            if os.path.exists(image_path):
                print(f"Loading image from: {image_path}")  # Debug print
                image = Image.open(image_path)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                self.token_image = ImageTk.PhotoImage(image)
                if self.image_label:
                    self.image_label.configure(image=self.token_image)
                    print("Image displayed successfully")  # Debug print
            else:
                print(f"Image file not found: {image_path}")  # Debug print
                
        except Exception as e:
            print(f"Error displaying image: {e}")  # Debug print
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
            
    def load_token(self):
        """Load a selected token"""
        try:
            selection = self.token_list.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a token to load")
                return
                
            token_name = self.token_list.item(selection[0])['text']
            token_file = os.path.join(self.token_dir, f"{token_name}.json")
            
            if os.path.exists(token_file):
                # Create new token
                self.current_token = TokenStats(token_name)
                
                # Load token data
                with open(token_file, 'r') as f:
                    data = json.load(f)
                    
                self.current_token.stats = data.get('stats', {})
                self.current_token.notes = data.get('notes', '')
                if 'image_path' in data:
                    self.current_token.image_path = data['image_path']
                
                # Update UI
                self.update_ui_from_token()
                
                # Display image if available
                if hasattr(self.current_token, 'image_path') and self.current_token.image_path:
                    self.display_image(self.current_token.image_path)
                    
        except Exception as e:
            print(f"Error loading token: {e}")
            messagebox.showerror("Error", f"Failed to load token: {str(e)}")
                
    def new_token(self):
        """Create a new token"""
        self.current_token = TokenStats()
        self.token_image = None
        self.image_label.configure(image='', text="No Image")
        self.update_ui_from_token()
    
    def delete_token(self):
        """Delete a selected token"""
        selection = self.token_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a token to delete")
            return
        
        token_name = self.token_list.item(selection[0])['text']
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {token_name}?"):
            token_path = os.path.join(self.token_dir, f"{token_name}.json")
            try:
                os.remove(token_path)
                self.load_token_list()
                self.new_token()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete token: {str(e)}")
    
    def create_default_json_files(self):
        """Create default JSON files for PNG files that don't have them"""
        try:
            # Get all PNG files
            png_files = [f for f in os.listdir(self.token_dir) if f.lower().endswith('.png')]
            
            for png_file in png_files:
                token_name = os.path.splitext(png_file)[0]
                json_file = os.path.join(self.token_dir, f"{token_name}.json")
                
                # Skip if JSON already exists
                if os.path.exists(json_file):
                    continue
                    
                # Create default stats
                token_stats = {
                    'name': token_name,
                    'stats': {
                        'Name': token_name,
                        'HP': '10',
                        'AC': '10',
                        'Initiative': '+0'
                    },
                    'image_path': png_file,
                    'notes': ''
                }
                
                # Save JSON file
                with open(json_file, 'w') as f:
                    json.dump(token_stats, f, indent=4)
                print(f"Created default JSON for: {token_name}")
                
        except Exception as e:
            print(f"Error creating default JSON files: {e}")
            
    def load_token_list(self):
        """Load the list of available tokens"""
        try:
            # First create any missing JSON files
            self.create_default_json_files()
            
            # Clear existing items
            for item in self.token_list.get_children():
                self.token_list.delete(item)
            
            # Get all JSON files
            json_files = [f for f in os.listdir(self.token_dir) if f.lower().endswith('.json')]
            
            # Add each token to the list
            for json_file in sorted(json_files):
                token_name = os.path.splitext(json_file)[0]
                self.token_list.insert('', 'end', text=token_name)
                
        except Exception as e:
            print(f"Error loading token list: {e}")

class NewTokenDialog:
    def __init__(self, parent, token_types_dir):
        """Initialize the new token dialog"""
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Create New Token")
        self.token_types_dir = token_types_dir
        
        # Name entry
        name_frame = ttk.Frame(self.top, padding="5")
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Token Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Token type selection
        type_frame = ttk.Frame(self.top, padding="5")
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="Token Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(type_frame, textvariable=self.type_var)
        self.type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Load token types
        self.load_token_types()
        
        # Buttons
        button_frame = ttk.Frame(self.top, padding="5")
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Create", command=self.create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        self.top.transient(parent)
        self.top.grab_set()
        parent.wait_window(self.top)
        
    def load_token_types(self):
        """Load available token types"""
        try:
            # Get all JSON files from token_types directory
            type_files = [f for f in os.listdir(self.token_types_dir) if f.endswith('.json')]
            
            # Load type names
            types = ['Custom (No Template)']
            for type_file in type_files:
                with open(os.path.join(self.token_types_dir, type_file), 'r') as f:
                    data = json.load(f)
                    types.append(data['name'])
                    
            # Update combobox
            self.type_combo['values'] = types
            self.type_combo.set(types[0])
            
        except Exception as e:
            print(f"Error loading token types: {e}")
            self.type_combo['values'] = ['Custom (No Template)']
            self.type_combo.set('Custom (No Template)')
            
    def create(self):
        """Create the new token"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a token name")
            return
            
        token_type = self.type_var.get()
        if token_type == 'Custom (No Template)':
            token_type = None
        else:
            # Find the corresponding file
            for file in os.listdir(self.token_types_dir):
                if file.endswith('.json'):
                    with open(os.path.join(self.token_types_dir, file), 'r') as f:
                        data = json.load(f)
                        if data['name'] == token_type:
                            token_type = os.path.splitext(file)[0]
                            break
                            
        self.result = {
            'name': name,
            'type': token_type
        }
        self.top.destroy()
        
    def cancel(self):
        """Cancel creating new token"""
        self.top.destroy()

class TokenSelectDialog:
    """DO NOT CHANGE THIS CLASS - Working correctly for token selection"""
    def __init__(self, parent, tokens_dir=None):
        """Initialize the token select dialog"""
        self.top = tk.Toplevel(parent)
        self.top.title("Select Token")
        self.result = None
        self.tokens_dir = tokens_dir or "D:/WorldWiki/Grid map/tokens"  # Use default if not provided
        
        # Create listbox for token selection
        name_frame = ttk.Frame(self.top, padding="5")
        name_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Select Token:").pack(side=tk.TOP, padx=5)
        
        # Create scrollbar and listbox
        scrollbar = ttk.Scrollbar(name_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.token_listbox = tk.Listbox(name_frame, yscrollcommand=scrollbar.set)
        self.token_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.token_listbox.yview)
        
        # Load token list from JSON files
        self.load_token_list()
        
        # Buttons
        button_frame = ttk.Frame(self.top, padding="5")
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Select", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the dialog
        window_width = 300
        window_height = 400
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.top.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        parent.wait_window(self.top)
        
    def load_token_list(self):
        """Load list of available tokens from JSON files"""
        try:
            # Clear existing items
            self.token_listbox.delete(0, tk.END)
            
            print(f"[TokenSelectDialog] Loading tokens from: {self.tokens_dir}")  # Debug print
            
            # Get list of JSON files
            if os.path.exists(self.tokens_dir):
                json_files = [f for f in os.listdir(self.tokens_dir) if f.endswith('.json')]
                print(f"[TokenSelectDialog] Found JSON files: {json_files}")  # Debug print
                
                # Add token names to listbox (without .json extension)
                for json_file in sorted(json_files):
                    token_name = os.path.splitext(json_file)[0]
                    print(f"[TokenSelectDialog] Adding token: {token_name}")  # Debug print
                    self.token_listbox.insert(tk.END, token_name)
            else:
                print(f"[TokenSelectDialog] Tokens directory not found: {self.tokens_dir}")  # Debug print
                    
        except Exception as e:
            print(f"[TokenSelectDialog] Error loading token list: {e}")
            messagebox.showerror("Error", f"Failed to load token list: {e}")
            
    def ok(self):
        """Handle OK button click"""
        try:
            # Get selected token name
            selection = self.token_listbox.curselection()
            if selection:
                self.result = self.token_listbox.get(selection[0])
                print(f"[TokenSelectDialog] Selected token: {self.result}")  # Debug print
                self.top.destroy()
            else:
                messagebox.showwarning("Warning", "Please select a token")
        except Exception as e:
            print(f"[TokenSelectDialog] Error handling OK click: {e}")
            messagebox.showerror("Error", f"Failed to select token: {e}")
            
    def cancel(self):
        """Handle Cancel button click"""
        self.result = None
        self.top.destroy()

if __name__ == '__main__':
    """Main entry point"""
    root = tk.Tk()
    app = TokenEditor(root)
    root.mainloop()
