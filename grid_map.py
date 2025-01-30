import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json

class MapCreator:
    def __init__(self, root):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST"""
        self.root = root
        self.root.title("Grid Map Creator")
        
        # Set default grid size
        self.grid_size = 50
        
        # Initialize variables
        self.image = None
        self.photo = None
        self.image_item = None
        self.show_grid = True
        self.maps_dir = "D:/WorldWiki/dist/Places"
        self.scale_factor = 1.0  # Add scale factor
        self.original_image = None
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create canvas
        self.create_canvas()
        
    def create_toolbar(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Create the toolbar with buttons"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Add buttons
        ttk.Button(toolbar, text="Load PNG", command=self.load_png).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Save MAP", command=self.save_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Toggle Grid", command=self.toggle_grid).pack(side=tk.LEFT, padx=5)
        
        # Add grid size control
        ttk.Label(toolbar, text="Grid Size:").pack(side=tk.LEFT, padx=(20,5))
        self.grid_size_var = tk.StringVar(value="50")
        grid_size_entry = ttk.Entry(toolbar, textvariable=self.grid_size_var, width=5)
        grid_size_entry.pack(side=tk.LEFT)
        grid_size_entry.bind('<Return>', lambda e: self.update_grid_size())
        ttk.Button(toolbar, text="Apply", command=self.update_grid_size).pack(side=tk.LEFT, padx=5)
        
        # Add scale slider
        ttk.Label(toolbar, text="Map Scale:").pack(side=tk.LEFT, padx=(20,5))
        self.scale_slider = ttk.Scale(toolbar, from_=0.1, to=2.0, orient=tk.HORIZONTAL, 
                                    length=150, value=1.0, command=self.update_scale)
        self.scale_slider.pack(side=tk.LEFT, padx=5)
        
    def create_canvas(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Create the main canvas"""
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
        
    def load_png(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Load a PNG image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png")],
            initialdir=self.maps_dir
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)  # Store original image
                self.update_image_scale()  # Apply scaling
                self.draw_grid()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def save_map(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Save as MAP file"""
        try:
            if not self.image:
                messagebox.showwarning("Warning", "No image loaded")
                return
                
            # Get save location
            save_path = filedialog.asksaveasfilename(
                title="Save MAP",
                defaultextension=".MAP",
                filetypes=[("Map files", "*.MAP")],
                initialdir=self.maps_dir
            )
            
            if save_path:
                # Create map data
                map_data = {
                    "grid_size": self.grid_size,
                    "image_path": save_path.replace(".MAP", ".png")
                }
                
                # Save image as PNG next to MAP file
                png_path = save_path.replace(".MAP", ".png")
                self.image.save(png_path)
                
                # Save MAP file
                with open(save_path, 'w') as f:
                    json.dump(map_data, f, indent=4)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save MAP: {str(e)}")
            
    def toggle_grid(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Toggle grid visibility"""
        self.show_grid = not self.show_grid
        if self.image:
            self.canvas.delete("grid")
            if self.show_grid:
                self.draw_grid()
                
    def update_grid_size(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Update the grid size"""
        try:
            new_size = int(self.grid_size_var.get())
            if new_size > 0:
                self.grid_size = new_size
                if self.show_grid and self.image:
                    self.canvas.delete("grid")
                    self.draw_grid()
            else:
                messagebox.showwarning("Warning", "Grid size must be positive")
        except ValueError:
            messagebox.showwarning("Warning", "Invalid grid size")
            
    def update_scale(self, value):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Update the map scale"""
        self.scale_factor = float(value)
        if hasattr(self, 'original_image'):
            self.update_image_scale()
            self.draw_grid()

    def update_image_scale(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Update the image with current scale factor"""
        if hasattr(self, 'original_image'):
            # Calculate new dimensions
            new_width = int(self.original_image.width * self.scale_factor)
            new_height = int(self.original_image.height * self.scale_factor)
            
            # Resize the image
            self.image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            
            # Update canvas
            if self.image_item:
                self.canvas.delete(self.image_item)
            self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            
            # Update canvas scrollregion
            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
            
    def draw_grid(self):
        """DO NOT CHANGE ANYTHING IN THIS METHOD UNLESS IT IS DIRECTLY RELATED TO THE PROMPT REQUEST
        Draw grid on canvas"""
        if not self.image:
            return
            
        # Get image dimensions
        width = self.image.width
        height = self.image.height
        
        # Draw vertical lines
        for x in range(0, width, self.grid_size):
            self.canvas.create_line(
                x, 0, x, height,
                fill="white", dash=(2,2),
                tags="grid",
                stipple="gray50"
            )
            
        # Draw horizontal lines
        for y in range(0, height, self.grid_size):
            self.canvas.create_line(
                0, y, width, y,
                fill="white", dash=(2,2),
                tags="grid",
                stipple="gray50"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = MapCreator(root)
    root.mainloop()
