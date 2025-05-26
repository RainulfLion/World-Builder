# ui_manager.py 
import pygame
import config
from ui_elements import Button, Label, Slider, TextInput, ToggleButton

class UIManager:
    def __init__(self, app_ref):
        self.app = app_ref
        self.elements = [] # List of *currently active* UI elements
        self.all_elements = {} # Dictionary to store all elements, including inactive menu items
        self.menu_buttons = [] # List to track top menu buttons
        self.creator_elements = []
        
        # --- Define UI Areas ---
        self.top_bar_rect = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.TOP_BAR_HEIGHT)
        self.right_panel_rect = pygame.Rect(config.SCREEN_WIDTH - config.RIGHT_PANEL_WIDTH, config.TOP_BAR_HEIGHT, config.RIGHT_PANEL_WIDTH, config.SCREEN_HEIGHT - config.TOP_BAR_HEIGHT - config.BOTTOM_PANEL_HEIGHT)
        self.bottom_panel_rect = pygame.Rect(0, config.SCREEN_HEIGHT - config.BOTTOM_PANEL_HEIGHT, config.SCREEN_WIDTH, config.BOTTOM_PANEL_HEIGHT)
        self.timeline_area_height = 100
        self.token_info_panel_rect = pygame.Rect(
            config.MAP_AREA_LEFT + 5,
            config.SCREEN_HEIGHT - config.BOTTOM_PANEL_HEIGHT + 5,
            config.MAP_AREA_WIDTH - 10,
            config.BOTTOM_PANEL_HEIGHT - 40
        )

        # --- Menu State ---
        self.active_menu = None
        self.menu_items = {
            'file': [],
            'tools': [],
            'settings': [],
            'help': []
        }

        # Store references to dynamic elements for easy updating
        self.token_list_elements = []
        self.dice_result_label = None
        self.timeline_slider = None
        self.timeline_label = None
        self.token_info_labels = {}
        
        # Dice roller state
        self.selected_dice_type = "D20"
        self.num_dice = 1
        self.dice_type_buttons = {}
        self.num_dice_buttons = {}
        
        # Token info state
        self.active_token_tab = 'stats'

        # --- Create Base UI Elements ---
        self.create_main_ui()
        
        # Create map creator UI elements (but don't add to main elements yet)
        self.create_creator_ui()

    def create_main_ui(self):
        # --- Create Base UI Elements for GAME mode ---
        self.create_menu_bar()
        self.create_token_list_panel()
        self.create_dice_roller_panel()
        self.create_timeline_panel()
        self.create_token_info_panel()

    def create_menu_bar(self):
        bw = 60
        bh = config.TOP_BAR_HEIGHT - 4
        margin = 5
        x_pos = margin

        # --- Top Level Menu Buttons ---
        file_button = Button(x_pos, 2, bw, bh, "File", {"type": "toggle_menu", "menu": "file"})
        self.all_elements['menu_file'] = file_button
        x_pos += bw + margin

        tools_button = Button(x_pos, 2, bw, bh, "Tools", {"type": "toggle_menu", "menu": "tools"})
        self.all_elements['menu_tools'] = tools_button
        x_pos += bw + margin

        settings_button = Button(x_pos, 2, bw, bh, "Settings", {"type": "toggle_menu", "menu": "settings"})
        self.all_elements['menu_settings'] = settings_button
        x_pos += bw + margin

        help_button = Button(x_pos, 2, bw, bh, "Help", {"type": "toggle_menu", "menu": "help"})
        self.all_elements['menu_help'] = help_button
        x_pos += bw + margin

        # Right-aligned buttons
        fullscreen_btn = Button(
            config.SCREEN_WIDTH - 40 - margin, 2, 40, bh, 
            "⛶", 
            {"type": "toggle_fullscreen"}
        )
        self.all_elements['fullscreen_btn'] = fullscreen_btn

        # --- Define Submenu Items ---
        menu_item_width = 140
        menu_item_height = 25

        # File Menu Items
        self.menu_items['file'] = [
            Button(file_button.rect.left, file_button.rect.bottom + 1, menu_item_width, menu_item_height,
                   "Create World", {"type": "menu_create_world"}),
            Button(file_button.rect.left, file_button.rect.bottom + 1 + menu_item_height, menu_item_width, menu_item_height,
                   "Load World", {"type": "menu_load_world"}),
            Button(file_button.rect.left, file_button.rect.bottom + 1 + menu_item_height * 2, menu_item_width, menu_item_height,
                   "Delete World", {"type": "menu_delete_world"}),
        ]

        # Tools Menu Items
        self.menu_items['tools'] = [
             Button(tools_button.rect.left, tools_button.rect.bottom + 1, menu_item_width, menu_item_height,
                   "Create Map", {"type": "menu_create_map"}),
             Button(tools_button.rect.left, tools_button.rect.bottom + 1 + menu_item_height, menu_item_width, menu_item_height,
                   "Create Token", {"type": "menu_create_token"}),
             Button(tools_button.rect.left, tools_button.rect.bottom + 1 + menu_item_height * 2, menu_item_width, menu_item_height,
                   "Create Note", {"type": "menu_create_note"}),
             Button(tools_button.rect.left, tools_button.rect.bottom + 1 + menu_item_height * 3, menu_item_width, menu_item_height,
                   "Create Location", {"type": "menu_create_location"}),
        ]

        # Settings Menu Items
        self.menu_items['settings'] = [
            Button(settings_button.rect.left, settings_button.rect.bottom + 1, menu_item_width, menu_item_height,
                  "Preferences", {"type": "show_settings"}),
        ]

        # Help Menu Items
        self.menu_items['help'] = [
            Button(help_button.rect.left, help_button.rect.bottom + 1, menu_item_width, menu_item_height,
                  "About", {"type": "show_about"}),
            Button(help_button.rect.left, help_button.rect.bottom + 1 + menu_item_height, menu_item_width, menu_item_height,
                  "Help", {"type": "show_help"}),
        ]

        # Add all top-level menu buttons to elements
        self.elements.append(file_button)
        self.elements.append(tools_button)
        self.elements.append(settings_button)
        self.elements.append(help_button)
        self.elements.append(fullscreen_btn)

        # Add top-level menu buttons to menu_buttons list
        self.menu_buttons.extend([file_button, tools_button, settings_button, help_button])

    def create_creator_ui(self):
        """Create UI elements specific to map creator mode - STORED SEPARATELY."""
        # Define button dimensions and layout parameters
        bw = 110
        bh = config.TOP_BAR_HEIGHT - 6
        margin = 25
        
        # Create a visual separator section for map creator tools
        separator_color = (80, 80, 80)
        separator_rect = pygame.Rect(
            config.SCREEN_WIDTH - config.RIGHT_PANEL_WIDTH - margin * 3 - bw * 3, 
            0, 
            bw * 3 + margin * 4, 
            config.TOP_BAR_HEIGHT
        )
        
        # Create a background panel for the map creator buttons
        self.creator_background = {
            "rect": separator_rect,
            "color": separator_color
        }
        
        # Position buttons within the separator area with equal spacing
        x_pos = separator_rect.left + margin
        
        # Create creator buttons - stored in creator_elements, NOT added to main elements
        self.creator_elements.append(Button(
            x_pos, 3, bw, bh, "Load Image", {"type": "creator_load_image"}
        ))
        x_pos += bw + margin
        
        self.creator_elements.append(Button(
            x_pos, 3, bw, bh, "Save Map", {"type": "creator_save_map"}
        ))
        x_pos += bw + margin
        
        self.creator_elements.append(Button(
            x_pos, 3, bw, bh, "<< Back", {"type": "creator_back_to_game"}
        ))
        
        # Create grid control panel - ONLY FOR MAP CREATOR MODE
        panel_width = config.RIGHT_PANEL_WIDTH - 20
        panel_height = 350
        panel_x = config.SCREEN_WIDTH - config.RIGHT_PANEL_WIDTH + 10
        panel_y = config.TOP_BAR_HEIGHT + 20
        
        self.grid_control_panel = {
            "rect": pygame.Rect(panel_x, panel_y, panel_width, panel_height),
            "color": config.UI_ALT_PANEL_COLOR,
            "border_color": config.UI_BORDER_COLOR,
            "title": "Grid Settings",
            "visible": False  # Initially hidden
        }
        
        # Create grid control elements - stored separately for creator mode
        control_x = panel_x + 15
        control_y = panel_y + 35
        control_width = panel_width - 30
        control_height = 30
        control_spacing = 10
        
        # Get default grid values (safe access)
        default_grid_size = 50
        default_grid_opacity = 0.7
        default_grid_style = "dashed"
        default_grid_visible = True
        default_scale = 1.0
        
        try:
            if hasattr(self.app, 'map_creator_state') and self.app.map_creator_state is not None:
                default_grid_size = self.app.map_creator_state["grid_settings"]["grid_size"]
                default_grid_opacity = self.app.map_creator_state["grid_settings"]["grid_opacity"]
                default_grid_style = self.app.map_creator_state["grid_settings"]["grid_style"]
                default_grid_visible = self.app.map_creator_state["grid_settings"]["grid_visible"]
                default_scale = self.app.map_creator_state["preview_scale"]
        except (KeyError, AttributeError) as e:
            print(f"Warning: Couldn't access map creator state: {e}")
        
        # Grid control sliders - stored in creator_elements
        self.creator_grid_size_slider = Slider(
            control_x, control_y, control_width, control_height,
            min_value=10, max_value=200, 
            value=default_grid_size
        )
        control_y += control_height + control_spacing
        
        self.creator_grid_opacity_slider = Slider(
            control_x, control_y, control_width, control_height,
            min_value=0.1, max_value=1.0,
            value=default_grid_opacity
        )
        control_y += control_height + control_spacing
        
        self.creator_grid_style_slider = Slider(
            control_x, control_y, control_width, control_height,
            min_value=0, max_value=1, 
            value=0 if default_grid_style == "dashed" else 1
        )
        control_y += control_height + control_spacing
        
        self.creator_grid_visible_slider = Slider(
            control_x, control_y, control_width, control_height,
            min_value=0, max_value=1, 
            value=1 if default_grid_visible else 0
        )
        control_y += control_height + control_spacing
        
        self.creator_scale_slider = Slider(
            control_x, control_y, control_width, control_height,
            min_value=0.25, max_value=2.0,
            value=default_scale
        )
        
        # Store grid control sliders for creator mode only
        self.creator_grid_controls = [
            self.creator_grid_size_slider,
            self.creator_grid_opacity_slider,
            self.creator_grid_style_slider,
            self.creator_grid_visible_slider,
            self.creator_scale_slider
        ]
        
        # Create creator map name label
        self.creator_map_name_label = {
            "rect": pygame.Rect(config.MAP_AREA_LEFT + 10, config.MAP_AREA_TOP + 10, 400, 25),
            "text": "Untitled Map",
            "color": config.UI_TEXT_COLOR,
            "font": config.DEFAULT_FONT
        }

    def create_token_list_panel(self):
        """Create the token list panel for GAME mode."""
        panel_x = self.right_panel_rect.left + 5
        panel_y = self.right_panel_rect.top + 5
        panel_w = self.right_panel_rect.width - 10
        self.token_list_y_start = panel_y + 55

        # Token list header
        token_list_header = Label(
            panel_x, panel_y, panel_w, 25,
            "Tokens On Map",
            font=config.DEFAULT_FONT
        )
        self.elements.append(token_list_header)
        
        # Column headers
        token_name_header = Label(
            panel_x + 15, panel_y + 30, panel_w - 50, 20,
            "Token Name",
            font=config.SMALL_FONT
        )
        self.elements.append(token_name_header)
        
        moved_header = Label(
            panel_x + panel_w - 50, panel_y + 30, 40, 20,
            "Moved",
            font=config.SMALL_FONT
        )
        self.elements.append(moved_header)

        # Token list buttons
        btn_w = (panel_w - 10) // 2
        btn_y = self.right_panel_rect.top + 180
        
        add_btn = Button(panel_x, btn_y, btn_w, 25, "Add From Created", {"type": "add_token"})
        remove_btn = Button(panel_x + btn_w + 10, btn_y, btn_w, 25, "Remove", {"type": "remove_token"})
        self.all_elements['token_add'] = add_btn
        self.all_elements['token_remove'] = remove_btn
        self.elements.extend([add_btn, remove_btn])

    def create_dice_roller_panel(self):
        """Create the dice roller panel for GAME mode."""
        panel_x = self.right_panel_rect.left + 5
        panel_y = self.right_panel_rect.top + 250
        panel_w = self.right_panel_rect.width - 10
        
        # Header
        dice_header = Label(
            panel_x, panel_y, panel_w, 25,
            "Dice Roller",
            font=config.DEFAULT_FONT
        )
        self.elements.append(dice_header)
        
        # Create dice type buttons
        dice_types = ["D4", "D6", "D8", "D10", "D12", "D20", "D100"]
        btn_width = panel_w // 4
        btn_height = 30
        btn_margin = 5
        
        # Create a row of dice type buttons
        for i, dice_type in enumerate(dice_types):
            col = i % 4
            row = i // 4
            
            btn_x = panel_x + col * (btn_width + btn_margin)
            btn_y = panel_y + 30 + row * (btn_height + btn_margin)
            
            button_color = (120, 120, 200) if dice_type == self.selected_dice_type else config.UI_BUTTON_COLOR
            
            btn = Button(
                btn_x, btn_y, btn_width, btn_height,
                dice_type,
                {"type": "select_dice_type", "data": {"dice_type": dice_type}}
            )
            if dice_type == self.selected_dice_type:
                btn.color = (120, 120, 200)
                
            self.dice_type_buttons[dice_type] = btn
            self.elements.append(btn)
        
        # Number of dice selector (1-10)
        num_text = Label(
            panel_x, panel_y + 110, 80, 25,
            "Number of dice:",
            font=config.SMALL_FONT
        )
        self.elements.append(num_text)
        
        # Number buttons (1-10)
        for i in range(1, 11):
            btn_x = panel_x + ((i-1) % 5) * 30
            btn_y = panel_y + 135 + ((i-1) // 5) * 35
            
            button_color = (120, 200, 120) if i == self.num_dice else config.UI_BUTTON_COLOR
            
            btn = Button(
                btn_x, btn_y, 25, 25,
                str(i),
                {"type": "select_num_dice", "data": {"num_dice": i}}
            )
            if i == self.num_dice:
                btn.color = (120, 200, 120)
                
            self.num_dice_buttons[i] = btn
            self.elements.append(btn)
        
        # Roll button
        roll_btn = Button(
            panel_x + panel_w//4, panel_y + 210, panel_w//2, 35,
            f"Roll {self.num_dice} {self.selected_dice_type}",
            {"type": "roll_dice", "data": {"dice_type": self.selected_dice_type, "num_dice": self.num_dice, "custom_sides": None}}
        )
        self.roll_button = roll_btn
        self.elements.append(roll_btn)
        
        # Results label
        self.dice_result_label = Label(
            panel_x, panel_y + 255, panel_w, 60,
            "Results: Roll some dice!",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.dice_result_label)

    def create_timeline_panel(self):
        """Create the timeline panel for GAME mode."""
        self.timeline_area_rect = pygame.Rect(
            self.bottom_panel_rect.left,
            self.bottom_panel_rect.top,
            self.bottom_panel_rect.width,
            self.timeline_area_height
        )
        padding = 5
        panel_x = self.timeline_area_rect.left + padding
        panel_y = self.timeline_area_rect.top + padding
        panel_w = self.timeline_area_rect.width - 2 * padding
        content_h = self.timeline_area_rect.height - 2 * padding

        # Timeline header
        timeline_header = Label(
            panel_x, panel_y, 100, 24,
            "Timeline",
            font=config.DEFAULT_FONT
        )
        self.elements.append(timeline_header)

        # Navigation buttons
        button_size = 25
        prev_button = Button(
            panel_x + 110, panel_y, button_size, button_size,
            "◀",
            {"type": "timeline_prev"}
        )
        self.elements.append(prev_button)

        next_button = Button(
            panel_x + 110 + button_size + 5, panel_y, button_size, button_size,
            "▶",
            {"type": "timeline_next"}
        )
        self.elements.append(next_button)

        # Add/remove time point buttons
        add_button = Button(
            panel_x + panel_w - 80, panel_y, button_size, button_size,
            "+",
            {"type": "timeline_add"}
        )
        self.elements.append(add_button)

        remove_button = Button(
            panel_x + panel_w - 30, panel_y, button_size, button_size,
            "-",
            {"type": "timeline_remove"}
        )
        self.elements.append(remove_button)

        # Timeline label
        self.timeline_label = Label(
            panel_x, panel_y + button_size + 5, panel_w, 24,
            "Time: 0",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.timeline_label)

    def create_token_info_panel(self):
        """Create the token info panel for GAME mode."""
        padding = 5
        panel_x = self.bottom_panel_rect.left + padding
        panel_y = self.bottom_panel_rect.top + self.timeline_area_height + padding
        panel_w = self.bottom_panel_rect.width - 2 * padding
        panel_h = self.bottom_panel_rect.height - self.timeline_area_height - 2 * padding

        self.token_info_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        # Create header
        token_info_header = Label(
            panel_x + 5, panel_y + 5, panel_w - 10, 24,
            "Token Information",
            font=config.DEFAULT_FONT
        )
        self.elements.append(token_info_header)

        # Initialize labels
        self.token_info_labels['Name'] = Label(
            panel_x + 5, panel_y + 30, panel_w - 10, 20,
            "Name: None selected",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.token_info_labels['Name'])

        self.token_info_labels['Position'] = Label(
            panel_x + 5, panel_y + 50, panel_w - 10, 20,
            "Position: -",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.token_info_labels['Position'])

        # Tabs
        tab_width = 60
        tab_height = 20
        stats_tab_btn = Button(
            panel_x + 5, panel_y + 75, tab_width, tab_height,
            "Stats",
            {"type": "token_tab", "tab": "stats"}
        )
        actions_tab_btn = Button(
            panel_x + 70, panel_y + 75, tab_width, tab_height,
            "Actions",
            {"type": "token_tab", "tab": "actions"}
        )
        
        self.all_elements['token_tab_stats'] = stats_tab_btn
        self.all_elements['token_tab_actions'] = actions_tab_btn
        self.elements.extend([stats_tab_btn, actions_tab_btn])

        # Stats content
        y_offset = panel_y + 100
        self.token_info_labels['HP'] = Label(
            panel_x + 5, y_offset, panel_w // 2 - 10, 20,
            "HP: 0/0",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.token_info_labels['HP'])

        self.token_info_labels['Status'] = Label(
            panel_x + panel_w // 2, y_offset, panel_w // 2 - 10, 20,
            "Status: None",
            font=config.DEFAULT_FONT
        )
        self.elements.append(self.token_info_labels['Status'])

    def switch_to_creator_mode(self):
        """Switch UI to map creator mode."""
        print("UI: Switching to creator mode")
        
        # Clear current game mode elements (but keep menu buttons)
        self.elements = [elem for elem in self.elements if elem in self.menu_buttons or elem == self.all_elements.get('fullscreen_btn')]
        
        # Add creator elements
        self.elements.extend(self.creator_elements)
        
        # Show grid control panel
        if hasattr(self, 'grid_control_panel'):
            self.grid_control_panel["visible"] = True

    def switch_to_game_mode(self):
        """Switch UI back to game mode."""
        print("UI: Switching to game mode")
        
        # Hide grid control panel
        if hasattr(self, 'grid_control_panel'):
            self.grid_control_panel["visible"] = False
        
        # Clear creator elements
        self.elements = [elem for elem in self.elements if elem not in self.creator_elements]
        
        # Recreate game mode UI
        self.create_main_ui()

    def open_menu(self, menu_name):
        """Adds submenu items to the active elements list."""
        if menu_name in self.menu_items:
            self.close_menu()
            self.active_menu = menu_name
            self.elements.extend(self.menu_items[menu_name])

    def close_menu(self):
        """Removes submenu items from the active elements list."""
        if self.active_menu and self.active_menu in self.menu_items:
            submenu = self.menu_items[self.active_menu]
            self.elements = [elem for elem in self.elements if elem not in submenu]
        self.active_menu = None

    def process_event(self, event):
        """Handle UI events. Returns an action if one should be taken."""
        if event.type == pygame.MOUSEMOTION:
            for menu, items in self.menu_items.items():
                if self.active_menu == menu:
                    for item in items:
                        item.handle_event(event)

            # Handle creator elements if in creator mode
            if self.app.app_mode == "MAP_CREATOR":
                for element in self.creator_elements:
                    element.handle_event(event)
                
                # Handle grid control sliders in creator mode
                if hasattr(self, 'creator_grid_controls'):
                    for slider in self.creator_grid_controls:
                        slider.handle_event(event)
            
            # Handle regular elements
            for btn in self.elements:
                if isinstance(btn, Button):
                    btn.handle_event(event)
        
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            # Check regular elements first
            for btn in self.elements:
                if isinstance(btn, Button):
                    action = btn.handle_event(event)
                    if action:
                        if action.get("type") == "toggle_menu":
                            menu_name = action.get("menu")
                            if self.active_menu == menu_name:
                                self.close_menu()
                            else:
                                self.open_menu(menu_name)
                            return None
                        return action
            
            # Check active menu items
            if self.active_menu and self.active_menu in self.menu_items:
                for item in self.menu_items[self.active_menu]:
                    action = item.handle_event(event)
                    if action:
                        self.close_menu()
                        return action
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_rect = self._get_menu_panel_rect(self.active_menu)
                    if not menu_rect.collidepoint(event.pos):
                        self.close_menu()
                        return None
                
                return None
            
            # Handle creator mode elements
            if self.app.app_mode == "MAP_CREATOR":
                for element in self.creator_elements:
                    action = element.handle_event(event)
                    if action:
                        return action
                
                # Handle grid control sliders
                if hasattr(self, 'creator_grid_controls'):
                    for slider in self.creator_grid_controls:
                        action = slider.handle_event(event)
                        if action:
                            return action
                
                # Handle map clicks for wall placement
                map_rect = pygame.Rect(
                    config.MAP_AREA_LEFT, 
                    config.MAP_AREA_TOP,
                    config.MAP_AREA_WIDTH,
                    config.MAP_AREA_HEIGHT
                )
                
                if map_rect.collidepoint(event.pos):
                    map_x, map_y = self.app.map_to_grid_coords(event.pos)
                    if event.button == 1:  # Left click
                        self.app.toggle_wall_at_grid(map_x, map_y)
        
        return None

    def _update_dice_buttons(self):
        """Update the visual state of dice type and number buttons"""
        for dice_type, btn in self.dice_type_buttons.items():
            if dice_type == self.selected_dice_type:
                btn.color = (120, 120, 200)
            else:
                btn.color = config.UI_BUTTON_COLOR
                
        for num, btn in self.num_dice_buttons.items():
            if num == self.num_dice:
                btn.color = (120, 200, 120)
            else:
                btn.color = config.UI_BUTTON_COLOR
    
    def _update_roll_button(self):
        """Update the roll button to reflect current selections"""
        self.roll_button.text = f"Roll {self.num_dice} {self.selected_dice_type}"

    def _get_menu_panel_rect(self, menu_name):
        """Calculate the rectangle for a dropdown menu panel."""
        if menu_name in ['file', 'tools', 'settings', 'help']:
            menu_button = self.all_elements.get(f'menu_{menu_name}')
            if menu_button:
                items = self.menu_items.get(menu_name, [])
                if items:
                    item_height = 30
                    total_height = len(items) * item_height
                    width = 200
                    
                    return pygame.Rect(
                        menu_button.rect.left, 
                        menu_button.rect.bottom, 
                        width, 
                        total_height
                    )
        
        return pygame.Rect(0, 0, 200, 100)

    def draw_panels(self, surface):
        """Draw the basic UI panels based on current app mode."""
        if self.app.app_mode in ["GAME", "MAP_CREATOR"]:
            # Draw top bar for all modes
            pygame.draw.rect(surface, config.UI_PANEL_COLOR, self.top_bar_rect)
            pygame.draw.rect(surface, config.UI_BORDER_COLOR, self.top_bar_rect, 1)
            
    def draw_panels(self, surface):
        """Draw the basic UI panels based on current app mode."""
        if self.app.app_mode in ["GAME", "MAP_CREATOR"]:
            # Draw top bar for all modes
            pygame.draw.rect(surface, config.UI_PANEL_COLOR, self.top_bar_rect)
            pygame.draw.rect(surface, config.UI_BORDER_COLOR, self.top_bar_rect, 1)
            
        if self.app.app_mode == "GAME":
            # Draw right panel for game mode
            pygame.draw.rect(surface, config.UI_PANEL_COLOR, self.right_panel_rect)
            pygame.draw.rect(surface, config.UI_BORDER_COLOR, self.right_panel_rect, 1)
            
            # Draw bottom panel for game mode
            if hasattr(self, 'bottom_panel_rect'):
                pygame.draw.rect(surface, config.UI_PANEL_COLOR, self.bottom_panel_rect)
                pygame.draw.rect(surface, config.UI_BORDER_COLOR, self.bottom_panel_rect, 1)
                
    def draw(self, surface):
        """Draw all UI elements based on current mode."""
        # Draw panels first
        self.draw_panels(surface)
        
        # Always draw the top menu elements
        for element_key in ['menu_file', 'menu_tools', 'menu_settings', 'menu_help', 'fullscreen_btn']:
            element = self.all_elements.get(element_key)
            if element is not None:
                element.draw(surface)
        
        # Draw elements based on app mode
        if self.app.app_mode == "GAME":
            # Draw all game mode elements
            for element in self.elements:
                if element is not None and element not in self.menu_buttons:
                    element.draw(surface)
                
        elif self.app.app_mode == "MAP_CREATOR":
            # Draw creator background panel
            if hasattr(self, 'creator_background'):
                pygame.draw.rect(surface, self.creator_background['color'], self.creator_background['rect'])
            
            # Draw creator buttons
            for element in self.creator_elements:
                if element is not None:
                    element.draw(surface)
            
            # Draw grid control panel ONLY in creator mode
            if hasattr(self, 'grid_control_panel') and self.grid_control_panel.get("visible", False):
                try:
                    pygame.draw.rect(surface, self.grid_control_panel['color'], self.grid_control_panel['rect'])
                    pygame.draw.rect(surface, self.grid_control_panel['border_color'], self.grid_control_panel['rect'], 1)
                    
                    # Draw grid control panel title
                    if 'title' in self.grid_control_panel:
                        title_text = self.grid_control_panel['title']
                        if hasattr(config, 'DEFAULT_FONT') and config.DEFAULT_FONT is not None:
                            title_surface = config.DEFAULT_FONT.render(title_text, True, config.UI_TEXT_COLOR)
                            surface.blit(title_surface, (self.grid_control_panel['rect'].left + 10, self.grid_control_panel['rect'].top + 5))
                    
                    # Draw grid control sliders
                    if hasattr(self, 'creator_grid_controls'):
                        for slider in self.creator_grid_controls:
                            if slider is not None:
                                slider.draw(surface)
                                
                except Exception as e:
                    print(f"Error rendering grid control panel: {e}")
            
            # Update and draw map name label in creator mode
            if hasattr(self, 'creator_map_name_label') and self.creator_map_name_label is not None:
                try:
                    current_name = self.app.map_creator_state.get("map_name", "")
                    is_saved = self.app.map_creator_state.get("image_path") is not None
                    suffix = "" if is_saved else " *"
                    self.creator_map_name_label["text"] = f"Map: {current_name}{suffix}" if current_name else "Untitled Map"
                    
                    if "font" in self.creator_map_name_label and self.creator_map_name_label["font"] is not None:
                        text_surface = self.creator_map_name_label["font"].render(
                            self.creator_map_name_label["text"], 
                            True, 
                            self.creator_map_name_label["color"]
                        )
                        surface.blit(text_surface, self.creator_map_name_label["rect"].topleft)
                except Exception as e:
                    print(f"Error rendering map name label: {e}")
        
        # Draw active menu items last (on top)
        if self.active_menu and self.active_menu in self.menu_items:
            panel_rect = self._get_menu_panel_rect(self.active_menu)
            pygame.draw.rect(surface, config.UI_PANEL_COLOR, panel_rect)
            pygame.draw.rect(surface, config.UI_BORDER_COLOR, panel_rect, 1)
            
            for item in self.menu_items[self.active_menu]:
                if item is not None:
                    item.draw(surface)

    def update_token_info(self, token_data):
        """Update token information display."""
        if token_data:
            stats = token_data.get('current_stats', {})
            base_stats = token_data.get('base_stats', {})
            max_hp = base_stats.get('HP', 0)
            current_hp = stats.get('HP', max_hp)
            pos_x = token_data.get('pos_x', '-')
            pos_y = token_data.get('pos_y', '-')

            self.token_info_labels['Name'].text = f"Name: {token_data.get('name', 'N/A')}"
            self.token_info_labels['Position'].text = f"Position: ({pos_x}, {pos_y})"
            self.token_info_labels['HP'].text = f"HP: {current_hp} / {max_hp}"
            self.token_info_labels['Status'].text = f"Status: {stats.get('Status', 'None')}"
        else:
            self.token_info_labels['Name'].text = "Name: None selected"
            self.token_info_labels['Position'].text = "Position: -"
            self.token_info_labels['HP'].text = "HP: 0/0"
            self.token_info_labels['Status'].text = "Status: None"

    def update_timeline_slider(self, current_turn, max_turn):
        """Update timeline display."""
        if self.timeline_label:
            self.timeline_label.text = f"Time: {current_turn}"

    def update_token_list(self, tokens_on_map):
        """Update the token list display."""
        # Clear existing token list elements
        self.elements = [e for e in self.elements if e not in self.token_list_elements]
        self.token_list_elements.clear()

        y_offset = self.token_list_y_start
        item_height = 20
        list_width = self.right_panel_rect.width - 10

        for i, token_data in enumerate(tokens_on_map):
             list_item_y = self.right_panel_rect.top + y_offset + i * (item_height + 2)
             if list_item_y + item_height > self.right_panel_rect.bottom:
                 break

             name = token_data.get('name', 'Unknown')
             instance_id = token_data.get('instance_id')
             moved = token_data.get('current_stats', {}).get('HasMoved', False)

             token_button = Button(
                 self.right_panel_rect.left + 5, list_item_y, list_width, item_height,
                 f"{name[:15]}" if len(name) > 15 else name,
                 {"type": "select_token_from_list", "data": {"instance_id": instance_id}}
             )
             
             token_button.color = config.UI_LIST_ITEM_COLOR
             token_button.hover_color = config.UI_LIST_HOVER_COLOR

             moved_indicator = Label(
                 self.right_panel_rect.left + list_width - 30, list_item_y, 20, item_height,
                 "✓" if moved else "✗",
                 color=(100, 200, 100) if moved else (200, 100, 100)
             )

             self.elements.append(token_button)
             self.elements.append(moved_indicator)
             self.token_list_elements.append(token_button)
             self.token_list_elements.append(moved_indicator)

             y_offset += item_height + 2

    def update_dice_results(self, results):
        """Update the dice roller results display"""
        if isinstance(results, str):
            self.dice_result_label.text = f"Results: {results}"
        elif isinstance(results, list):
            if len(results) == 1 and isinstance(results[0], str) and "Error" in results[0]:
                self.dice_result_label.text = f"Error: {results[0]}"
            else:
                total = sum(results) if all(isinstance(r, (int, float)) for r in results) else "N/A"
                rolls_str = ", ".join(str(r) for r in results)
                
                if len(results) > 1:
                    self.dice_result_label.text = f"Results: [{rolls_str}] = {total}"
                else:
                    self.dice_result_label.text = f"Result: {total}"
        else:
            self.dice_result_label.text = f"Results: {results}"

    def update_creator_map_name(self, name):
        """Update the map name displayed in the creator."""
        if hasattr(self, 'creator_map_name_label'):
            self.creator_map_name_label["text"] = f"Map: {name}" if name else "Untitled Map"