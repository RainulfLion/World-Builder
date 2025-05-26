import os
import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, colorchooser
from config import *

class TokenCreator:
    """Standalone script or integrated UI for token creation."""
    
    def __init__(self, screen, database):
        """Initialize the token creator."""
        self.screen = screen
        self.db = database
        self.running = False
        self.token_image = None
        self.token_path = None
        self.token_name = ""
        self.token_size = 1  # Size in grid cells
        self.token_color = (255, 0, 0)  # Default color (red)
        self.token_type = "character"  # character, monster, object
        self.token_notes = ""
        self.token_initiative = 0
        
        # Initialize UI elements
        self.font = pygame.font.SysFont(None, 24)
        self.buttons = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI elements."""
        button_width = 150
        button_height = 30
        button_x = 10
        button_y = 10
        padding = 10
        
        # Create buttons for different actions
        actions = [
            ("Load Image", self._load_image),
            ("Set Name", self._set_name),
            ("Set Size", self._set_size),
            ("Set Color", self._set_color),
            ("Set Type", self._set_type),
            ("Set Notes", self._set_notes),
            ("Set Initiative", self._set_initiative),
            ("Save Token", self._save_token),
            ("Exit", self.exit)
        ]
        
        for i, (text, callback) in enumerate(actions):
            btn = {
                "rect": pygame.Rect(button_x, button_y + i * (button_height + padding), button_width, button_height),
                "text": text,
                "callback": callback
            }
            self.buttons.append(btn)
            
    def start(self):
        """Start the token creator."""
        self.running = True
        self.run()
        
    def exit(self):
        """Exit the token creator."""
        self.running = False
        
    def run(self):
        """Run the token creator loop."""
        # Main loop
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if a button was clicked
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(event.pos):
                            btn["callback"]()
                            break
                            
            # Draw everything
            self._draw()
            
            # Update display
            pygame.display.flip()
            
    def _draw(self):
        """Draw the token creator interface."""
        # Fill screen with background color
        self.screen.fill((40, 40, 40))
        
        # Draw buttons
        for btn in self.buttons:
            pygame.draw.rect(self.screen, (80, 80, 80), btn["rect"])
            
            text_surf = self.font.render(btn["text"], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn["rect"].center)
            self.screen.blit(text_surf, text_rect)
            
        # Draw token preview area
        preview_area = pygame.Rect(250, 50, 300, 300)
        pygame.draw.rect(self.screen, (60, 60, 60), preview_area)
        
        # Draw token image if available
        if self.token_image:
            # Scale token image to fit preview area while maintaining aspect ratio
            img_rect = self.token_image.get_rect()
            scale = min(preview_area.width / img_rect.width, preview_area.height / img_rect.height)
            new_width = int(img_rect.width * scale)
            new_height = int(img_rect.height * scale)
            
            scaled_img = pygame.transform.scale(self.token_image, (new_width, new_height))
            img_pos = (
                preview_area.x + (preview_area.width - new_width) // 2,
                preview_area.y + (preview_area.height - new_height) // 2
            )
            
            self.screen.blit(scaled_img, img_pos)
            
            # Draw colored outline to represent token color
            outline_rect = pygame.Rect(
                img_pos[0] - 5,
                img_pos[1] - 5,
                new_width + 10,
                new_height + 10
            )
            pygame.draw.rect(self.screen, self.token_color, outline_rect, 3)
            
        # Draw token information
        info_x = 600
        info_y = 50
        line_height = 30
        
        info_items = [
            f"Name: {self.token_name or 'None'}",
            f"Size: {self.token_size} grid cell(s)",
            f"Type: {self.token_type.capitalize()}",
            f"Initiative: {self.token_initiative}",
            f"Notes: {(self.token_notes[:20] + '...') if len(self.token_notes) > 20 else self.token_notes}"
        ]
        
        for i, info in enumerate(info_items):
            text_surf = self.font.render(info, True, (255, 255, 255))
            self.screen.blit(text_surf, (info_x, info_y + i * line_height))
            
    def _load_image(self):
        """Load a token image."""
        # Initialize tkinter for file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Token Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        
        if file_path:
            try:
                # Load image
                self.token_image = pygame.image.load(file_path).convert_alpha()
                self.token_path = file_path
                
                # Get token name from filename if not already set
                if not self.token_name:
                    self.token_name = os.path.splitext(os.path.basename(file_path))[0]
                    
                # Save a copy to assets/tokens
                token_dir = os.path.join("assets", "tokens")
                if not os.path.exists(token_dir):
                    os.makedirs(token_dir)
                    
                dest_path = os.path.join(token_dir, os.path.basename(file_path))
                pygame.image.save(self.token_image, dest_path)
                
            except Exception as e:
                print(f"Error loading image: {e}")
                
    def _set_name(self):
        """Set the token name."""
        # Initialize tkinter for dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open input dialog
        name = simpledialog.askstring(
            "Token Name",
            "Enter token name:",
            initialvalue=self.token_name
        )
        
        if name:
            self.token_name = name
            
    def _set_size(self):
        """Set the token size."""
        # Initialize tkinter for dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open input dialog
        size = simpledialog.askinteger(
            "Token Size",
            "Enter token size in grid cells:",
            minvalue=1,
            maxvalue=5,
            initialvalue=self.token_size
        )
        
        if size:
            self.token_size = size
            
    def _set_color(self):
        """Set the token color."""
        # Initialize tkinter for color chooser
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open color chooser dialog
        color = colorchooser.askcolor(
            title="Select Token Color",
            initialcolor=self.token_color
        )
        
        if color[0]:  # color is ((r,g,b), '#rrggbb')
            self.token_color = (int(color[0][0]), int(color[0][1]), int(color[0][2]))
            
    def _set_type(self):
        """Set the token type."""
        # Initialize tkinter for dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create a simple dialog for type selection
        types = ["character", "monster", "object"]
        type_dialog = tk.Toplevel(root)
        type_dialog.title("Token Type")
        type_dialog.geometry("200x150")
        type_dialog.resizable(False, False)
        
        # Create label
        tk.Label(type_dialog, text="Select token type:").pack(pady=10)
        
        # Create variable to store selection
        selected_type = tk.StringVar(value=self.token_type)
        
        # Create radio buttons
        for t in types:
            tk.Radiobutton(
                type_dialog,
                text=t.capitalize(),
                variable=selected_type,
                value=t
            ).pack(anchor=tk.W, padx=20)
            
        # Create OK button
        def on_ok():
            self.token_type = selected_type.get()
            type_dialog.destroy()
            
        tk.Button(type_dialog, text="OK", command=on_ok).pack(pady=10)
        
        # Wait for dialog to close
        type_dialog.transient(root)
        type_dialog.grab_set()
        root.wait_window(type_dialog)
        
    def _set_notes(self):
        """Set the token notes."""
        # Initialize tkinter for dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create a dialog for notes entry
        notes_dialog = tk.Toplevel(root)
        notes_dialog.title("Token Notes")
        notes_dialog.geometry("400x300")
        
        # Create label
        tk.Label(notes_dialog, text="Enter token notes:").pack(pady=10)
        
        # Create text entry
        text_entry = tk.Text(notes_dialog, height=10, width=40)
        text_entry.pack(padx=10, pady=5)
        text_entry.insert(tk.END, self.token_notes)
        
        # Create OK button
        def on_ok():
            self.token_notes = text_entry.get("1.0", tk.END).strip()
            notes_dialog.destroy()
            
        tk.Button(notes_dialog, text="OK", command=on_ok).pack(pady=10)
        
        # Wait for dialog to close
        notes_dialog.transient(root)
        notes_dialog.grab_set()
        root.wait_window(notes_dialog)
        
    def _set_initiative(self):
        """Set the token initiative."""
        # Initialize tkinter for dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Open input dialog
        initiative = simpledialog.askinteger(
            "Token Initiative",
            "Enter token initiative bonus:",
            initialvalue=self.token_initiative
        )
        
        if initiative is not None:
            self.token_initiative = initiative
            
    def _save_token(self):
        """Save the token to the database."""
        if not self.token_image or not self.token_path:
            messagebox.showerror("Error", "You must load a token image first.")
            return
            
        if not self.token_name:
            messagebox.showerror("Error", "You must set a token name first.")
            return
            
        # Save token to database
        try:
            # Get relative path to token image
            rel_path = os.path.join("assets", "tokens", os.path.basename(self.token_path))
            
            # Add token to database
            token_id = self.db.add_token(
                self.token_name,
                rel_path,
                self.token_size,
                self.token_color,
                self.token_type,
                self.token_notes,
                self.token_initiative
            )
            
            if token_id:
                messagebox.showinfo("Success", f"Token '{self.token_name}' saved successfully.")
            else:
                messagebox.showerror("Error", "Failed to save token.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving token: {e}")


def run_standalone():
    """Run the token creator as a standalone application."""
    import sqlite3
    from database import Database
    
    # Initialize pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Token Creator")
    
    # Create database connection
    db_path = os.path.join("data", "game_data.db")
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
        
    conn = sqlite3.connect(db_path)
    db = Database(conn)
    
    # Create and run token creator
    creator = TokenCreator(screen, db)
    creator.start()
    
    # Clean up
    pygame.quit()


if __name__ == "__main__":
    run_standalone()