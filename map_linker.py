import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json

class MapLinker:
    def __init__(self, root):
        """Initialize the map linker
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        self.root = root
        self.root.title("Map Linker")
        
        # Initialize variables
        self.current_map = None
        self.current_photo = None
        self.map_buttons = {}  # Stores button widgets and their linked maps
        self.maps_dir = "D:/WorldWiki/dist/Places"
        self.placing_button = False
        self.button_name_counter = 1
        
        # Load token image
        token_path = os.path.join("images", "town.png")
        if os.path.exists(token_path):
            self.token_image = Image.open(token_path).resize((32, 32))
        else:
            # Create a simple house icon if image not found
            self.token_image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            # Draw a simple house shape
            from PIL import ImageDraw
            draw = ImageDraw.Draw(self.token_image)
            # Roof
            draw.polygon([(5, 15), (16, 5), (27, 15)], fill='red')
            # House body
            draw.rectangle([8, 15, 24, 28], fill='tan')
            # Door
            draw.rectangle([14, 20, 18, 28], fill='brown')
            
        self.token_photo = ImageTk.PhotoImage(self.token_image)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create canvas
        self.create_canvas()
        
        # Track cursor token
        self.cursor_token = None
        self.canvas.bind('<Motion>', self.update_cursor_token)
        self.canvas.bind('<Leave>', self.remove_cursor_token)
        
    def create_toolbar(self):
        """Create the toolbar with buttons
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add buttons
        ttk.Button(toolbar, text="Load Map", command=self.load_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save Links", command=self.save_links).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Load Links", command=self.load_links).pack(side=tk.LEFT, padx=5)
        
    def create_canvas(self):
        """Create the main canvas
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        # Create canvas frame
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='black')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set
        )
        
        # Bind right-click for button placement
        self.canvas.bind("<Button-3>", self.place_button)
        
    def update_cursor_token(self, event):
        """Update the token image at cursor position
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        if not self.current_map:
            return
            
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.cursor_token:
            self.canvas.delete(self.cursor_token)
            
        self.cursor_token = self.canvas.create_image(x, y, image=self.token_photo)
        
    def remove_cursor_token(self, event):
        """Remove the cursor token when mouse leaves canvas
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        if self.cursor_token:
            self.canvas.delete(self.cursor_token)
            self.cursor_token = None
        
    def load_map(self):
        """Load a map file
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Map File",
                filetypes=[
                    ("Map files", "*.MAP"),
                    ("PNG files", "*.png")
                ],
                initialdir=self.maps_dir
            )
            
            if file_path:
                if file_path.lower().endswith('.map'):
                    # Load MAP file
                    with open(file_path, 'r') as f:
                        map_data = json.load(f)
                    png_path = map_data["image_path"]
                    self.current_map = Image.open(png_path)
                else:
                    # Load PNG directly
                    self.current_map = Image.open(file_path)
                
                # Update display
                self.current_photo = ImageTk.PhotoImage(self.current_map)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, image=self.current_photo, anchor=tk.NW)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {str(e)}")
            
    def place_button(self, event):
        """Place a button on the canvas where right-clicked
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        if not self.current_map:
            return
            
        try:
            # Get click position
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            # Select map to link first
            file_path = filedialog.askopenfilename(
                title="Select Map to Link",
                filetypes=[
                    ("Map files", "*.MAP"),
                    ("PNG files", "*.png")
                ],
                initialdir=self.maps_dir
            )
            
            if not file_path:
                return
                
            # Create button name from linked map
            button_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Create button
            button = tk.Button(
                self.canvas,
                image=self.token_photo,
                compound=tk.CENTER
            )
            button_window = self.canvas.create_window(x, y, window=button, anchor=tk.CENTER)
            
            # Store button info
            self.map_buttons[button_name] = {
                "button": button,
                "window": button_window,
                "x": x,
                "y": y,
                "linked_map": file_path
            }
            
            # Configure button
            button.configure(command=lambda b=button_name: self.button_clicked(b))
            
            # Add tooltip
            self.create_tooltip(button, f"Click to load:\n{button_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place button: {str(e)}")
            
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Creates a toplevel window
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
            
    def button_clicked(self, button_name):
        """Handle button click - load the linked map
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        try:
            linked_map = self.map_buttons[button_name]["linked_map"]
            if linked_map:
                self.load_linked_map(linked_map)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to handle button click: {str(e)}")
            
    def load_linked_map(self, map_path):
        """Load the linked map
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        try:
            if map_path.lower().endswith('.map'):
                # Load MAP file
                with open(map_path, 'r') as f:
                    map_data = json.load(f)
                png_path = map_data["image_path"]
                self.current_map = Image.open(png_path)
            else:
                # Load PNG directly
                self.current_map = Image.open(map_path)
            
            # Update display
            self.current_photo = ImageTk.PhotoImage(self.current_map)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.current_photo, anchor=tk.NW)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Redraw all buttons
            for name, info in self.map_buttons.items():
                button_window = self.canvas.create_window(
                    info["x"], info["y"],
                    window=info["button"],
                    anchor=tk.CENTER
                )
                info["window"] = button_window
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load linked map: {str(e)}")
            
    def save_links(self):
        """Save the button links to a file
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        try:
            if not self.current_map:
                messagebox.showwarning("Warning", "No map loaded")
                return
                
            save_path = filedialog.asksaveasfilename(
                title="Save Map Links",
                defaultextension=".links",
                filetypes=[("Link files", "*.links")],
                initialdir=self.maps_dir
            )
            
            if save_path:
                # Create links data
                links_data = {}
                for name, info in self.map_buttons.items():
                    links_data[name] = {
                        "x": info["x"],
                        "y": info["y"],
                        "linked_map": info["linked_map"]
                    }
                
                # Save links
                with open(save_path, 'w') as f:
                    json.dump(links_data, f, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save links: {str(e)}")
            
    def load_links(self):
        """Load button links from a file
        DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        try:
            if not self.current_map:
                messagebox.showwarning("Warning", "Load a map first")
                return
                
            file_path = filedialog.askopenfilename(
                title="Load Map Links",
                filetypes=[("Link files", "*.links")],
                initialdir=self.maps_dir
            )
            
            if file_path:
                # Clear existing buttons
                for info in self.map_buttons.values():
                    self.canvas.delete(info["window"])
                self.map_buttons.clear()
                
                # Load and create buttons
                with open(file_path, 'r') as f:
                    links_data = json.load(f)
                    
                for name, info in links_data.items():
                    # Create button
                    button = tk.Button(
                        self.canvas,
                        image=self.token_photo,
                        compound=tk.CENTER
                    )
                    button_window = self.canvas.create_window(
                        info["x"], info["y"],
                        window=button,
                        anchor=tk.CENTER
                    )
                    
                    # Store button info
                    self.map_buttons[name] = {
                        "button": button,
                        "window": button_window,
                        "x": info["x"],
                        "y": info["y"],
                        "linked_map": info["linked_map"]
                    }
                    
                    # Configure button
                    button.configure(command=lambda b=name: self.button_clicked(b))
                    
                    # Add tooltip
                    self.create_tooltip(button, f"Click to load:\n{name}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load links: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MapLinker(root)
    root.mainloop()
