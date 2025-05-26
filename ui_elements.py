import pygame
import tkinter as tk
from tkinter import scrolledtext
import os

class UIElement:
    """Base class for UI elements."""
    
    def __init__(self, x, y, width, height):
        """Initialize the UI element."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.id = None
        
    def draw(self, screen):
        """Draw the element on the screen."""
        pass
        
    def handle_event(self, event):
        """Handle pygame events."""
        pass
        
    def update(self):
        """Update the element state."""
        pass
        
    def set_position(self, x, y):
        """Set the position of the element."""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Button(UIElement):
    """Enhanced Button UI element with drag and drop support."""
    
    def __init__(self, x, y, width, height, text, action_data=None, bg_color=(100, 100, 100), 
                 hover_color=(150, 150, 150), text_color=(255, 255, 255), border_radius=5, 
                 draggable=False):
        """Initialize the button."""
        super().__init__(x, y, width, height)
        self.text = text
        self.action_data = action_data
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.hovered = False
        self.draggable = draggable
        self.dragging = False
        self.drag_offset = (0, 0)
        self.font = pygame.font.SysFont(None, 24)
        self.color = bg_color  # Current color
        
    def draw(self, screen):
        """Draw the button on the screen."""
        if not self.visible:
            return
            
        # Draw button background
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        """Handle pygame events for the button."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
            if self.dragging and self.draggable:
                # Update position while dragging
                new_x = event.pos[0] - self.drag_offset[0]
                new_y = event.pos[1] - self.drag_offset[1]
                self.set_position(new_x, new_y)
                return {"type": "token_drag", "data": {"element": self, "pos": event.pos}}
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.draggable:
                    self.dragging = True
                    self.drag_offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                    return {"type": "token_drag_start", "data": {"element": self}}
                else:
                    return self.action_data
                    
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return {"type": "token_drag_end", "data": {"element": self, "pos": event.pos}}
                
        return None

    def _check_text_fit(self):
        """Ensure text fits in button - helper method."""
        pass


class TimelineSlider(UIElement):
    """Timeline slider for navigating through game history."""
    
    def __init__(self, x, y, width, height, max_turns=100, current_turn=0, 
                 bg_color=(80, 80, 80), handle_color=(200, 200, 200), 
                 track_color=(120, 120, 120)):
        """Initialize the timeline slider."""
        super().__init__(x, y, width, height)
        self.max_turns = max_turns
        self.current_turn = current_turn
        self.bg_color = bg_color
        self.handle_color = handle_color
        self.track_color = track_color
        self.dragging = False
        self.handle_rect = pygame.Rect(0, 0, 20, height)
        self.timeline_events = []  # Store timeline events
        self._update_handle_position()
        
    def _update_handle_position(self):
        """Update handle position based on current turn."""
        if self.max_turns == 0:
            pos_pct = 0
        else:
            pos_pct = self.current_turn / self.max_turns
            
        handle_x = self.x + int(pos_pct * (self.width - self.handle_rect.width))
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.y
        
    def _update_turn_from_pos(self, x_pos):
        """Update current turn based on handle position."""
        relative_x = max(0, min(x_pos - self.x, self.width - self.handle_rect.width))
        if self.width - self.handle_rect.width == 0:
            self.current_turn = 0
        else:
            self.current_turn = int((relative_x / (self.width - self.handle_rect.width)) * self.max_turns)
        
    def draw(self, screen):
        """Draw the timeline slider."""
        if not self.visible:
            return
            
        # Draw slider track
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=3)
        
        # Draw timeline markers for events
        for i, event in enumerate(self.timeline_events):
            if i <= self.max_turns:
                marker_x = self.x + int((i / self.max_turns) * (self.width - 5))
                pygame.draw.circle(screen, self.track_color, (marker_x, self.y + self.height // 2), 3)
        
        # Draw slider handle
        pygame.draw.rect(screen, self.handle_color, self.handle_rect, border_radius=5)
        
        # Draw current turn text
        font = pygame.font.SysFont(None, 20)
        turn_text = font.render(f"Turn: {self.current_turn}", True, (255, 255, 255))
        screen.blit(turn_text, (self.x, self.y - 25))
        
    def handle_event(self, event):
        """Handle timeline slider events."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                return {"type": "timeline_drag_start"}
            elif self.rect.collidepoint(event.pos):
                # Click on track - jump to position
                self._update_turn_from_pos(event.pos[0])
                self._update_handle_position()
                return {"type": "timeline_jump", "data": {"turn": self.current_turn}}
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return {"type": "timeline_drag_end", "data": {"turn": self.current_turn}}
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_turn_from_pos(event.pos[0])
            self._update_handle_position()
            return {"type": "timeline_change", "data": {"turn": self.current_turn}}
            
        return None
        
    def set_max_turns(self, max_turns):
        """Set the maximum number of turns."""
        self.max_turns = max_turns
        self._update_handle_position()
        
    def set_current_turn(self, turn):
        """Set the current turn."""
        self.current_turn = max(0, min(turn, self.max_turns))
        self._update_handle_position()
        
    def add_timeline_event(self, turn, event_data):
        """Add an event to the timeline."""
        self.timeline_events.append({"turn": turn, "data": event_data})
        self.timeline_events.sort(key=lambda x: x["turn"])


class LocationIcon(UIElement):
    """Location icon that can be placed on maps and open sub-maps."""
    
    def __init__(self, x, y, name, location_type="generic", sub_map_id=None, 
                 notes="", audio_file=None):
        """Initialize the location icon."""
        super().__init__(x, y, 32, 32)  # Standard icon size
        self.name = name
        self.location_type = location_type
        self.sub_map_id = sub_map_id
        self.notes = notes
        self.audio_file = audio_file
        self.hovered = False
        self.selected = False
        
        # Define icons for different location types
        self.icons = {
            "city": "🏙️",
            "inn": "🏠",
            "dungeon": "🕳️",
            "forest": "🌲",
            "mountain": "⛰️",
            "castle": "🏰",
            "village": "🏘️",
            "generic": "📍"
        }
        
    def draw(self, screen):
        """Draw the location icon."""
        if not self.visible:
            return
            
        # Draw background circle
        color = (100, 150, 255) if self.selected else (80, 120, 200) if self.hovered else (60, 100, 180)
        pygame.draw.circle(screen, color, self.rect.center, 16)
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, 16, 2)
        
        # Draw icon (using text for now - could be replaced with actual icons)
        font = pygame.font.SysFont(None, 24)
        icon_text = self.icons.get(self.location_type, self.icons["generic"])
        text_surf = font.render(icon_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # Draw name below icon if hovered
        if self.hovered:
            name_font = pygame.font.SysFont(None, 18)
            name_surf = name_font.render(self.name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
            
            # Draw background for text
            bg_rect = name_rect.inflate(10, 4)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(name_surf, name_rect)
        
    def handle_event(self, event):
        """Handle location icon events."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1:  # Left click
                    if self.sub_map_id:
                        return {"type": "open_sub_map", "data": {"map_id": self.sub_map_id, "location": self}}
                    else:
                        return {"type": "select_location", "data": {"location": self}}
                elif event.button == 3:  # Right click
                    return {"type": "location_context_menu", "data": {"location": self, "pos": event.pos}}
                    
        return None


class NotesWindow:
    """Window for creating and editing notes with text and audio support."""
    
    def __init__(self, location_name="", existing_notes="", existing_audio=None):
        self.location_name = location_name
        self.notes_text = existing_notes
        self.audio_file = existing_audio
        self.result = None
        
    def show(self):
        """Show the notes window and return the result."""
        root = tk.Tk()
        root.title(f"Notes for {self.location_name}" if self.location_name else "Notes")
        root.geometry("500x400")
        root.resizable(True, True)
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Location name entry
        if not self.location_name:
            tk.Label(main_frame, text="Location Name:").pack(anchor=tk.W)
            self.name_entry = tk.Entry(main_frame, width=50)
            self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Notes text area
        tk.Label(main_frame, text="Notes:").pack(anchor=tk.W)
        self.text_area = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.text_area.insert(tk.END, self.notes_text)
        
        # Audio section
        audio_frame = tk.Frame(main_frame)
        audio_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(audio_frame, text="Audio:").pack(side=tk.LEFT)
        
        if self.audio_file:
            self.audio_label = tk.Label(audio_frame, text=f"Current: {os.path.basename(self.audio_file)}")
            self.audio_label.pack(side=tk.LEFT, padx=(10, 0))
        else:
            self.audio_label = tk.Label(audio_frame, text="No audio file")
            self.audio_label.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Button(audio_frame, text="Browse Audio", command=self.browse_audio).pack(side=tk.RIGHT)
        tk.Button(audio_frame, text="Record", command=self.record_audio).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Save", command=self.save_notes).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side=tk.RIGHT)
        
        # Center the window
        root.transient()
        root.grab_set()
        root.wait_window()
        
        return self.result
    
    def browse_audio(self):
        """Browse for an audio file."""
        from tkinter import filedialog
        
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=filetypes
        )
        
        if filename:
            self.audio_file = filename
            self.audio_label.config(text=f"Selected: {os.path.basename(filename)}")
    
    def record_audio(self):
        """Start audio recording (placeholder - would need actual implementation)."""
        tk.messagebox.showinfo("Recording", "Audio recording feature coming soon!")
    
    def save_notes(self):
        """Save the notes and close the window."""
        result = {
            "notes": self.text_area.get("1.0", tk.END).strip(),
            "audio_file": self.audio_file
        }
        
        if hasattr(self, 'name_entry'):
            result["name"] = self.name_entry.get().strip()
        
        self.result = result
        self.text_area.master.master.destroy()


class TokenActionsWindow:
    """Window for recording token actions during a turn."""
    
    def __init__(self, token_name="", existing_actions=None):
        self.token_name = token_name
        self.actions = existing_actions or []
        self.result = None
        
    def show(self):
        """Show the actions window."""
        root = tk.Tk()
        root.title(f"Actions for {self.token_name}" if self.token_name else "Token Actions")
        root.geometry("400x300")
        
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Actions list
        tk.Label(main_frame, text="Actions This Turn:").pack(anchor=tk.W)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.actions_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.actions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.actions_listbox.yview)
        
        # Populate existing actions
        for action in self.actions:
            self.actions_listbox.insert(tk.END, action)
        
        # Add action entry
        entry_frame = tk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.action_entry = tk.Entry(entry_frame)
        self.action_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.action_entry.bind("<Return>", self.add_action)
        
        tk.Button(entry_frame, text="Add", command=self.add_action).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Remove Selected", command=self.remove_action).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Save", command=self.save_actions).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="Cancel", command=root.destroy).pack(side=tk.RIGHT)
        
        root.transient()
        root.grab_set()
        root.wait_window()
        
        return self.result
    
    def add_action(self, event=None):
        """Add a new action to the list."""
        action_text = self.action_entry.get().strip()
        if action_text:
            self.actions_listbox.insert(tk.END, action_text)
            self.action_entry.delete(0, tk.END)
    
    def remove_action(self):
        """Remove the selected action."""
        selection = self.actions_listbox.curselection()
        if selection:
            self.actions_listbox.delete(selection[0])
    
    def save_actions(self):
        """Save the actions and close."""
        actions = []
        for i in range(self.actions_listbox.size()):
            actions.append(self.actions_listbox.get(i))
        
        self.result = actions
        self.action_entry.master.master.destroy()


# Additional UI Elements for the new features

class MapNavigationBreadcrumb(UIElement):
    """Breadcrumb navigation for nested maps."""
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.map_stack = []  # Stack of (map_id, map_name) tuples
        self.font = pygame.font.SysFont(None, 20)
        
    def push_map(self, map_id, map_name):
        """Add a map to the navigation stack."""
        self.map_stack.append((map_id, map_name))
        
    def pop_map(self):
        """Remove the last map from the stack."""
        if len(self.map_stack) > 1:
            return self.map_stack.pop()
        return None
        
    def draw(self, screen):
        """Draw the breadcrumb navigation."""
        if not self.visible or not self.map_stack:
            return
            
        # Draw background
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (80, 80, 80), self.rect, 1)
        
        # Draw breadcrumbs
        x_offset = self.x + 10
        y_center = self.y + self.height // 2
        
        for i, (map_id, map_name) in enumerate(self.map_stack):
            if i > 0:
                # Draw separator
                sep_surf = self.font.render(" > ", True, (160, 160, 160))
                screen.blit(sep_surf, (x_offset, y_center - sep_surf.get_height() // 2))
                x_offset += sep_surf.get_width()
            
            # Draw map name (clickable if not the current map)
            color = (255, 255, 255) if i == len(self.map_stack) - 1 else (100, 150, 255)
            name_surf = self.font.render(map_name, True, color)
            screen.blit(name_surf, (x_offset, y_center - name_surf.get_height() // 2))
            x_offset += name_surf.get_width()
            
    def handle_event(self, event):
        """Handle breadcrumb clicks."""
        if not self.visible or event.type != pygame.MOUSEBUTTONDOWN:
            return None
            
        if self.rect.collidepoint(event.pos) and event.button == 1:
            # Calculate which breadcrumb was clicked
            x_offset = self.x + 10
            mouse_x = event.pos[0]
            
            for i, (map_id, map_name) in enumerate(self.map_stack[:-1]):  # Exclude current map
                if i > 0:
                    sep_width = self.font.size(" > ")[0]
                    x_offset += sep_width
                
                name_width = self.font.size(map_name)[0]
                if x_offset <= mouse_x <= x_offset + name_width:
                    # Clicked on this breadcrumb
                    return {"type": "navigate_to_map", "data": {"map_id": map_id, "depth": i}}
                
                x_offset += name_width
                
        return None


# Existing classes with enhancements...

class Panel(UIElement):
    """Panel UI element."""
    
    def __init__(self, x, y, width, height, bg_color=(50, 50, 50), close_button=False):
        """Initialize the panel."""
        super().__init__(x, y, width, height)
        self.bg_color = bg_color
        self.has_close_button = close_button
        self.close_button = None
        
        if close_button:
            self.close_button = Button(
                x + width - 30, y + 10, 20, 20, "×", 
                action_data={"type": "close_panel"},
                bg_color=(200, 50, 50), hover_color=(250, 50, 50)
            )
            
    def draw(self, screen):
        """Draw the panel on the screen."""
        if not self.visible:
            return
            
        # Draw panel background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # Draw close button if present
        if self.has_close_button and self.close_button:
            self.close_button.draw(screen)
            
    def handle_event(self, event):
        """Handle pygame events for the panel."""
        if not self.visible:
            return None
            
        if self.has_close_button and self.close_button:
            return self.close_button.handle_event(event)
            
        return None
        
    def set_visible(self, visible):
        """Set the visibility of the panel."""
        self.visible = visible


class TextInput(UIElement):
    """Text input UI element."""
    
    def __init__(self, x, y, width, height, default_text="", bg_color=(80, 80, 80), 
                 text_color=(255, 255, 255), active_color=(100, 100, 200)):
        """Initialize the text input."""
        super().__init__(x, y, width, height)
        self.text = default_text
        self.bg_color = bg_color
        self.text_color = text_color
        self.active_color = active_color
        self.active = False
        self.font = pygame.font.SysFont(None, 24)
        self.cursor_pos = len(default_text)
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def draw(self, screen):
        """Draw the text input on the screen."""
        if not self.visible:
            return
            
        # Draw input background
        color = self.active_color if self.active else self.bg_color
        pygame.draw.rect(screen, color, self.rect, border_radius=3)
        
        # Draw input text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(self.x + 10, self.y + self.height // 2))
        screen.blit(text_surf, text_rect)
        
        # Draw cursor
        if self.active and self.cursor_visible:
            cursor_x = text_rect.x + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(
                screen, 
                self.text_color, 
                (cursor_x, self.y + 5), 
                (cursor_x, self.y + self.height - 5), 
                2
            )
            
    def handle_event(self, event):
        """Handle pygame events for the text input."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                # Set cursor position based on click position (simplified)
                self.cursor_pos = len(self.text)
                
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                self.active = False
                return {"type": "text_input_submit", "data": {"text": self.text}}
            elif event.unicode:
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            return {"type": "text_input_change", "data": {"text": self.text}}
                
        return None
        
    def update(self):
        """Update the text input state."""
        # Blink cursor
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Adjust speed as needed
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0


class Slider(UIElement):
    """Slider UI element."""
    
    def __init__(self, x, y, width, height, min_value=0, max_value=100, 
                 value=50, on_change=None, bg_color=(80, 80, 80), 
                 handle_color=(200, 200, 200)):
        """Initialize the slider."""
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change = on_change
        self.bg_color = bg_color
        self.handle_color = handle_color
        self.dragging = False
        self.handle_rect = pygame.Rect(0, 0, 20, height)
        self._update_handle_position()
        
    def _update_handle_position(self):
        """Update handle position based on value."""
        value_range = self.max_value - self.min_value
        if value_range == 0:
            pos_pct = 0
        else:
            pos_pct = (self.value - self.min_value) / value_range
            
        handle_x = self.x + int(pos_pct * (self.width - self.handle_rect.width))
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.y
        
    def _update_value_from_pos(self, x_pos):
        """Update value based on handle position."""
        relative_x = max(0, min(x_pos - self.x, self.width - self.handle_rect.width))
        value_range = self.max_value - self.min_value
        self.value = self.min_value + (relative_x / (self.width - self.handle_rect.width)) * value_range
        
        if self.on_change:
            self.on_change(self.value)
        
    def draw(self, screen):
        """Draw the slider on the screen."""
        if not self.visible:
            return
            
        # Draw slider track
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=3)
        
        # Draw slider handle
        pygame.draw.rect(screen, self.handle_color, self.handle_rect, border_radius=5)
        
    def handle_event(self, event):
        """Handle pygame events for the slider."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                return {"type": "slider_drag_start"}
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_pos(event.pos[0])
            self._update_handle_position()
            return {"type": "slider_change", "data": {"value": self.value}}
            
        return None
        
    def set_value(self, value):
        """Set the slider value."""
        self.value = max(self.min_value, min(self.max_value, value))
        self._update_handle_position()
        
        if self.on_change:
            self.on_change(self.value)


class Label(UIElement):
    """Label UI element."""
    
    def __init__(self, x, y, width, height, text, font=None, text_color=(255, 255, 255), 
                 bg_color=None, align="left"):
        """Initialize the label."""
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font or pygame.font.SysFont(None, 24)
        self.text_color = text_color
        self.bg_color = bg_color
        self.align = align  # "left", "center", "right"
        
    def draw(self, screen):
        """Draw the label on the screen."""
        if not self.visible:
            return
            
        # Draw background if specified
        if self.bg_color:
            pygame.draw.rect(screen, self.bg_color, self.rect)
            
        # Draw text
        text_surf = self.font.render(self.text, True, self.text_color)
        
        if self.align == "left":
            text_rect = text_surf.get_rect(midleft=(self.x + 5, self.y + self.height // 2))
        elif self.align == "right":
            text_rect = text_surf.get_rect(midright=(self.x + self.width - 5, self.y + self.height // 2))
        else:  # center
            text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            
        screen.blit(text_surf, text_rect)


class ListBox(UIElement):
    """List box UI element."""
    
    def __init__(self, x, y, width, height, items, on_select=None, 
                 bg_color=(60, 60, 60), hover_color=(80, 80, 80),
                 select_color=(100, 100, 200), text_color=(255, 255, 255)):
        """Initialize the list box."""
        super().__init__(x, y, width, height)
        self.items = items  # Should be [(id, name), ...] or [name, ...]
        self.on_select = on_select
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.select_color = select_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 24)
        self.scroll_y = 0
        self.item_height = 30
        self.hovered_index = -1
        self.selected_index = -1
        self.max_visible_items = height // self.item_height
        
    def draw(self, screen):
        """Draw the list box on the screen."""
        if not self.visible:
            return
            
        # Draw list box background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # Draw visible items
        visible_count = min(len(self.items), self.max_visible_items)
        start_idx = max(0, min(len(self.items) - visible_count, self.scroll_y // self.item_height))
        
        for i in range(visible_count):
            item_idx = start_idx + i
            item = self.items[item_idx]
            
            # Determine item text - handle both tuple and string items
            if isinstance(item, tuple) and len(item) >= 2:
                item_text = str(item[1])  # Use name from (id, name) tuple
            else:
                item_text = str(item)
                
            # Determine item background color
            if item_idx == self.selected_index:
                item_bg = self.select_color
            elif item_idx == self.hovered_index:
                item_bg = self.hover_color
            else:
                item_bg = self.bg_color
                
            # Draw item background
            item_rect = pygame.Rect(
                self.x, 
                self.y + i * self.item_height, 
                self.width, 
                self.item_height
            )
            pygame.draw.rect(screen, item_bg, item_rect)
            
            # Draw item text
            text_surf = self.font.render(item_text, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(self.x + 10, self.y + i * self.item_height + self.item_height // 2))
            screen.blit(text_surf, text_rect)
            
    def handle_event(self, event):
        """Handle pygame events for the list box."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.y
                self.hovered_index = self.scroll_y // self.item_height + rel_y // self.item_height
                
                # Ensure hovered index is valid
                if self.hovered_index >= len(self.items):
                    self.hovered_index = -1
            else:
                self.hovered_index = -1
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if event.button == 1:  # Left click
                    rel_y = event.pos[1] - self.y
                    click_index = self.scroll_y // self.item_height + rel_y // self.item_height
                    
                    if 0 <= click_index < len(self.items):
                        self.selected_index = click_index
                        if self.on_select:
                            item = self.items[click_index]
                            if isinstance(item, tuple) and len(item) >= 1:
                                self.on_select(item[0])  # Pass id from (id, name) tuple
                            else:
                                self.on_select(item)
                        return {"type": "listbox_select", "data": {"index": click_index, "item": self.items[click_index]}}
                        
                elif event.button == 4:  # Scroll up
                    self.scroll_y = max(0, self.scroll_y - self.item_height)
                    return {"type": "listbox_scroll"}
                    
                elif event.button == 5:  # Scroll down
                    max_scroll = max(0, (len(self.items) - self.max_visible_items) * self.item_height)
                    self.scroll_y = min(max_scroll, self.scroll_y + self.item_height)
                    return {"type": "listbox_scroll"}
                    
        return None


class ToggleButton(UIElement):
    """Toggle button UI element that can switch between two states."""
    
    def __init__(self, x, y, width, height, text, options=["Off", "On"], current_value="Off", action=None, 
                 bg_color=(100, 100, 100), active_color=(150, 150, 200), text_color=(255, 255, 255)):
        """Initialize the toggle button."""
        super().__init__(x, y, width, height)
        self.text = text
        self.options = options
        self.current_value = current_value
        self.action = action
        self.bg_color = bg_color
        self.active_color = active_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 20)
        self.hovered = False
        
    def draw(self, screen):
        """Draw the toggle button on the screen."""
        if not self.visible:
            return
            
        # Choose color based on state
        current_bg = self.active_color if self.current_value == self.options[1] else self.bg_color
        if self.hovered:
            current_bg = tuple(min(255, c + 30) for c in current_bg)
            
        # Draw button background
        pygame.draw.rect(screen, current_bg, self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=5)
        
        # Draw text
        display_text = f"{self.text}: {self.current_value}"
        text_surface = self.font.render(display_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        """Handle pygame events for the toggle button."""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                # Toggle between options
                current_index = self.options.index(self.current_value)
                self.current_value = self.options[(current_index + 1) % len(self.options)]
                
                if self.action:
                    return self.action(self.current_value)
                else:
                    return {"type": "toggle_change", "data": {"value": self.current_value}}
                    
        return None