import tkinter as tk
from tkinter import ttk
from token_manager import TokenStats

class CharacterInfoBox:
    def __init__(self, parent, token, position=None):
        """Initialize the character info box"""
        try:
            print(f"[CharacterInfoBox] Creating info box for {token.name}")  # Debug print
            
            self.window = tk.Toplevel(parent)
            self.window.title(f"Character Info: {token.name}")
            self.token = token
            
            # Configure window style
            self.window.configure(bg='#2b2b2b')  # Dark theme
            self.style = ttk.Style()
            
            # Configure style
            self.style.configure('Dark.TFrame', background='#2b2b2b')
            self.style.configure('Dark.TLabel', background='#2b2b2b', foreground='white')
            self.style.configure('Dark.TButton', background='#2b2b2b', foreground='white')
            self.style.configure('Dark.TCheckbutton', background='#2b2b2b', foreground='white')
            self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
            self.style.configure('Dead.Header.TLabel', font=('Arial', 12, 'bold'), foreground='red')
            
            # Create main frame
            self.main_frame = ttk.Frame(self.window, style='Dark.TFrame')
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Title section with name
            title_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
            title_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Name label
            self.name_label = ttk.Label(title_frame, text=token.name,
                                      style='Dead.Header.TLabel' if token.is_dead else 'Header.TLabel')
            self.name_label.pack(side=tk.TOP, pady=5)
            
            # Position label
            pos_frame = ttk.Frame(title_frame, style='Dark.TFrame')
            pos_frame.pack(fill=tk.X)
            ttk.Label(pos_frame, text=f"Position: ({token.x}, {token.y})", 
                     style='Dark.TLabel').pack(side=tk.LEFT)
            
            # Grid snap and death toggles
            toggle_frame = ttk.Frame(title_frame, style='Dark.TFrame')
            toggle_frame.pack(fill=tk.X, pady=5)
            
            self.snap_var = tk.BooleanVar(value=token.snap_to_grid)
            snap_check = ttk.Checkbutton(toggle_frame, text="Snap to Grid", 
                                       variable=self.snap_var, style='Dark.TCheckbutton',
                                       command=self.toggle_grid_snap)
            snap_check.pack(side=tk.LEFT, padx=5)
            
            self.dead_var = tk.BooleanVar(value=token.is_dead)
            dead_check = ttk.Checkbutton(toggle_frame, text="Dead", 
                                       variable=self.dead_var, style='Dark.TCheckbutton',
                                       command=self.toggle_death)
            dead_check.pack(side=tk.LEFT, padx=5)
            
            # Stats section
            stats = token.token_stats.stats
            print(f"[CharacterInfoBox] Token stats: {stats}")  # Debug print
            self.stat_entries = {}
            
            # Core stats
            core_frame = ttk.LabelFrame(self.main_frame, text="Core Stats", style='Dark.TFrame')
            core_frame.pack(fill=tk.X, padx=5, pady=5)
            
            core_stats = [
                ('HP', f"{stats.get('HP', '10')}/{stats.get('Max HP', '10')}"),
                ('AC', stats.get('AC', '10')),
                ('Initiative', stats.get('Initiative', '+0')),
                ('Speed', stats.get('Speed', '30'))
            ]
            
            print(f"[CharacterInfoBox] Core stats: {core_stats}")  # Debug print
            for stat_name, stat_value in core_stats:
                row = ttk.Frame(core_frame, style='Dark.TFrame')
                row.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(row, text=f"{stat_name}:", style='Dark.TLabel', width=10).pack(side=tk.LEFT)
                entry = ttk.Entry(row, width=10)
                entry.insert(0, str(stat_value))
                entry.configure(state='readonly')
                entry.pack(side=tk.LEFT, padx=5)
                self.stat_entries[stat_name] = entry
                print(f"[CharacterInfoBox] Added {stat_name} = {stat_value}")  # Debug print
            
            # Ability scores
            ability_frame = ttk.LabelFrame(self.main_frame, text="Ability Scores", style='Dark.TFrame')
            ability_frame.pack(fill=tk.X, padx=5, pady=5)
            
            abilities = [
                'Strength', 'Dexterity', 'Constitution',
                'Intelligence', 'Wisdom', 'Charisma'
            ]
            
            for ability_name in abilities:
                row = ttk.Frame(ability_frame, style='Dark.TFrame')
                row.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(row, text=f"{ability_name}:", style='Dark.TLabel', width=10).pack(side=tk.LEFT)
                entry = ttk.Entry(row, width=10)
                entry.insert(0, str(stats.get(ability_name, '10')))
                entry.configure(state='readonly')
                entry.pack(side=tk.LEFT, padx=5)
                self.stat_entries[ability_name] = entry
                print(f"[CharacterInfoBox] Added {ability_name} = {stats.get(ability_name, '10')}")  # Debug print
            
            # Other stats
            other_frame = ttk.LabelFrame(self.main_frame, text="Other", style='Dark.TFrame')
            other_frame.pack(fill=tk.X, padx=5, pady=5)
            
            other_stats = [
                ('Proficiency', stats.get('Proficiency', '+2')),
                ('Level', stats.get('Level', '1'))
            ]
            
            for stat_name, stat_value in other_stats:
                row = ttk.Frame(other_frame, style='Dark.TFrame')
                row.pack(fill=tk.X, padx=5, pady=2)
                ttk.Label(row, text=f"{stat_name}:", style='Dark.TLabel', width=10).pack(side=tk.LEFT)
                entry = ttk.Entry(row, width=10)
                entry.insert(0, str(stat_value))
                entry.configure(state='readonly')
                entry.pack(side=tk.LEFT, padx=5)
                self.stat_entries[stat_name] = entry
                print(f"[CharacterInfoBox] Added {stat_name} = {stat_value}")  # Debug print
            
            # Notes section
            notes_frame = ttk.LabelFrame(self.main_frame, text="Notes", style='Dark.TFrame')
            notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.notes_text = tk.Text(notes_frame, height=10, width=40, bg='#2b2b2b', fg='white')
            self.notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.notes_text.insert('1.0', token.token_stats.notes)
            self.notes_text.configure(state='disabled')
            
            # Close button
            close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
            close_button.pack(pady=10)
            
            # Configure window position
            if position:
                self.window.geometry(f"+{position[0]}+{position[1]}")
            
            # Make window draggable
            self.window.bind("<Button-1>", self.start_move)
            self.window.bind("<B1-Motion>", self.do_move)
            
            # Protocol for window close button (X)
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Bind escape key to close
            self.window.bind("<Escape>", lambda e: self.on_closing())
            
            # Focus window
            self.window.focus_set()
            
            print("[CharacterInfoBox] Successfully created info box")  # Debug print
            
        except Exception as e:
            print(f"[CharacterInfoBox] Error creating info box: {e}")  # Debug print
            if hasattr(self, 'window'):
                self.window.destroy()
            raise

    def toggle_death(self):
        """Toggle token death state"""
        self.token.is_dead = self.dead_var.get()
        self.name_label.configure(style='Dead.Header.TLabel' if self.token.is_dead else 'Header.TLabel')
        
    def toggle_grid_snap(self):
        """Toggle token grid snap"""
        self.token.snap_to_grid = self.snap_var.get()
        
    def start_move(self, event):
        """Start window drag"""
        self.x = event.x
        self.y = event.y
    
    def do_move(self, event):
        """Handle window drag"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def on_closing(self):
        """Handle window closing"""
        try:
            print("[CharacterInfoBox] Closing window")  # Debug print
            # Remove reference to info box in token
            if self.token:
                self.token.info_box = None
            self.window.destroy()
        except Exception as e:
            print(f"[CharacterInfoBox] Error closing window: {e}")  # Debug print
            if self.token:
                self.token.info_box = None
            self.window.destroy()
