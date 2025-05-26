import sqlite3
import json
import os
from config import DB_PATH

class Database:
    """Enhanced database with support for location icons, notes, timeline, and token actions."""
    
    def __init__(self):
        """Initialize the database connection for this instance."""
        # Create the data directory if it doesn't exist
        db_dir = os.path.dirname(DB_PATH)
        os.makedirs(db_dir, exist_ok=True)

        # Connect to the database (creates it if it doesn't exist)
        abs_db_path = os.path.abspath(DB_PATH)
        print(f"DEBUG: Connecting to database at: {abs_db_path}")
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._check_and_migrate_schema()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        # Existing tables
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS worlds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS maps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id INTEGER,
            parent_map_id INTEGER,
            name TEXT NOT NULL,
            image_path TEXT NOT NULL,
            grid_size INTEGER DEFAULT 50,
            grid_enabled INTEGER DEFAULT 1,
            width INTEGER DEFAULT 0,
            height INTEGER DEFAULT 0,
            grid_color TEXT DEFAULT '#FFFFFF',
            map_scale REAL DEFAULT 1.0,
            grid_style TEXT DEFAULT 'dashed',
            grid_opacity REAL DEFAULT 0.7,
            map_type TEXT DEFAULT 'world',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        # Enhanced location icons table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_icons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            name TEXT NOT NULL,
            location_type TEXT DEFAULT 'generic',
            sub_map_id INTEGER,
            notes TEXT,
            audio_file TEXT,
            icon_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE,
            FOREIGN KEY (sub_map_id) REFERENCES maps (id) ON DELETE SET NULL
        )
        ''')

        # Enhanced timeline table with more detailed tracking
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id INTEGER NOT NULL,
            map_id INTEGER,
            turn_number INTEGER NOT NULL DEFAULT 0,
            event_type TEXT NOT NULL,
            event_title TEXT,
            event_description TEXT,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        # Enhanced tokens table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_path TEXT NOT NULL,
            size INTEGER DEFAULT 1,
            color TEXT DEFAULT "255,0,0",
            type TEXT DEFAULT "character",
            notes TEXT,
            initiative INTEGER DEFAULT 0,
            max_hp INTEGER DEFAULT 10,
            current_hp INTEGER DEFAULT 10,
            armor_class INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Enhanced map_tokens table with turn tracking
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            token_id INTEGER NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            rotation INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            initiative INTEGER DEFAULT 0,
            has_moved BOOLEAN DEFAULT 0,
            current_turn INTEGER DEFAULT 0,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE,
            FOREIGN KEY (token_id) REFERENCES tokens (id) ON DELETE CASCADE
        )
        ''')

        # Token actions per turn
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_token_id INTEGER NOT NULL,
            turn_number INTEGER NOT NULL,
            action_text TEXT NOT NULL,
            action_type TEXT DEFAULT 'custom',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (map_token_id) REFERENCES map_tokens (id) ON DELETE CASCADE
        )
        ''')

        # Token positions history for timeline scrubbing
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_position_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_token_id INTEGER NOT NULL,
            turn_number INTEGER NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            hp INTEGER,
            status_effects TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (map_token_id) REFERENCES map_tokens (id) ON DELETE CASCADE
        )
        ''')

        # Enhanced notes table with audio support
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER,
            location_icon_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            audio_file TEXT,
            x INTEGER DEFAULT -1,
            y INTEGER DEFAULT -1,
            note_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE,
            FOREIGN KEY (location_icon_id) REFERENCES location_icons (id) ON DELETE CASCADE
        )
        ''')

        # Game state tracking
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            world_id INTEGER NOT NULL,
            current_turn INTEGER DEFAULT 0,
            current_map_id INTEGER,
            active_token_id INTEGER,
            state_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
            FOREIGN KEY (current_map_id) REFERENCES maps (id) ON DELETE SET NULL
        )
        ''')

        # Existing tables (keeping for backward compatibility)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_walls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            grid_x INTEGER NOT NULL,
            grid_y INTEGER NOT NULL,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_doors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            grid_x INTEGER NOT NULL,
            grid_y INTEGER NOT NULL,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS map_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        # Legacy timeline table (keeping for migration)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (map_id) REFERENCES maps (id) ON DELETE CASCADE
        )
        ''')

        self.conn.commit()

    # Location Icons Methods
    def add_location_icon(self, map_id, x, y, name, location_type="generic", sub_map_id=None, 
                         notes="", audio_file=None, icon_path=None):
        """Add a location icon to a map."""
        try:
            self.cursor.execute('''
                INSERT INTO location_icons 
                (map_id, x, y, name, location_type, sub_map_id, notes, audio_file, icon_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (map_id, x, y, name, location_type, sub_map_id, notes, audio_file, icon_path))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding location icon: {e}")
            return None

    def get_location_icons(self, map_id):
        """Get all location icons for a map."""
        try:
            self.cursor.execute('''
                SELECT id, x, y, name, location_type, sub_map_id, notes, audio_file, icon_path
                FROM location_icons WHERE map_id = ?
            ''', (map_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting location icons: {e}")
            return []

    def update_location_icon(self, icon_id, **kwargs):
        """Update a location icon."""
        try:
            valid_fields = ['x', 'y', 'name', 'location_type', 'sub_map_id', 'notes', 'audio_file', 'icon_path']
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in valid_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                return False
                
            query = f"UPDATE location_icons SET {', '.join(updates)} WHERE id = ?"
            params.append(icon_id)
            
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating location icon: {e}")
            return False

    def delete_location_icon(self, icon_id):
        """Delete a location icon."""
        try:
            self.cursor.execute("DELETE FROM location_icons WHERE id = ?", (icon_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting location icon: {e}")
            return False

    # Enhanced Timeline Methods
    def add_timeline_event(self, world_id, turn_number, event_type, event_title, 
                          event_description="", event_data=None, map_id=None):
        """Add an event to the timeline."""
        try:
            if isinstance(event_data, dict):
                event_data = json.dumps(event_data)
                
            self.cursor.execute('''
                INSERT INTO timeline_events 
                (world_id, map_id, turn_number, event_type, event_title, event_description, event_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (world_id, map_id, turn_number, event_type, event_title, event_description, event_data))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding timeline event: {e}")
            return None

    def get_timeline_events(self, world_id, start_turn=None, end_turn=None, limit=None):
        """Get timeline events for a world within a turn range."""
        try:
            query = "SELECT * FROM timeline_events WHERE world_id = ?"
            params = [world_id]
            
            if start_turn is not None:
                query += " AND turn_number >= ?"
                params.append(start_turn)
                
            if end_turn is not None:
                query += " AND turn_number <= ?"
                params.append(end_turn)
                
            query += " ORDER BY turn_number ASC, timestamp ASC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting timeline events: {e}")
            return []

    def get_max_turn_number(self, world_id):
        """Get the maximum turn number for a world."""
        try:
            self.cursor.execute('''
                SELECT MAX(turn_number) FROM timeline_events WHERE world_id = ?
            ''', (world_id,))
            result = self.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except Exception as e:
            print(f"Error getting max turn number: {e}")
            return 0

    # Token Actions Methods
    def add_token_action(self, map_token_id, turn_number, action_text, action_type="custom"):
        """Add an action for a token during a specific turn."""
        try:
            self.cursor.execute('''
                INSERT INTO token_actions (map_token_id, turn_number, action_text, action_type)
                VALUES (?, ?, ?, ?)
            ''', (map_token_id, turn_number, action_text, action_type))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding token action: {e}")
            return None

    def get_token_actions(self, map_token_id, turn_number=None):
        """Get actions for a token, optionally for a specific turn."""
        try:
            if turn_number is not None:
                self.cursor.execute('''
                    SELECT id, action_text, action_type, timestamp 
                    FROM token_actions 
                    WHERE map_token_id = ? AND turn_number = ?
                    ORDER BY timestamp ASC
                ''', (map_token_id, turn_number))
            else:
                self.cursor.execute('''
                    SELECT id, turn_number, action_text, action_type, timestamp 
                    FROM token_actions 
                    WHERE map_token_id = ?
                    ORDER BY turn_number ASC, timestamp ASC
                ''', (map_token_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting token actions: {e}")
            return []

    def save_token_position(self, map_token_id, turn_number, x, y, hp=None, status_effects=None):
        """Save token position and state for a specific turn."""
        try:
            if isinstance(status_effects, (list, dict)):
                status_effects = json.dumps(status_effects)
                
            self.cursor.execute('''
                INSERT OR REPLACE INTO token_position_history 
                (map_token_id, turn_number, x, y, hp, status_effects)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (map_token_id, turn_number, x, y, hp, status_effects))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving token position: {e}")
            return False

    def get_token_position_at_turn(self, map_token_id, turn_number):
        """Get token position and state at a specific turn."""
        try:
            self.cursor.execute('''
                SELECT x, y, hp, status_effects 
                FROM token_position_history 
                WHERE map_token_id = ? AND turn_number <= ?
                ORDER BY turn_number DESC LIMIT 1
            ''', (map_token_id, turn_number))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting token position at turn: {e}")
            return None

    def get_all_token_positions_at_turn(self, map_id, turn_number):
        """Get all token positions on a map at a specific turn."""
        try:
            self.cursor.execute('''
                SELECT mt.id, mt.token_id, t.name, tph.x, tph.y, tph.hp, tph.status_effects,
                       t.image_path, t.size, t.color, t.type
                FROM map_tokens mt
                JOIN tokens t ON mt.token_id = t.id
                LEFT JOIN token_position_history tph ON mt.id = tph.map_token_id 
                    AND tph.turn_number = (
                        SELECT MAX(turn_number) 
                        FROM token_position_history 
                        WHERE map_token_id = mt.id AND turn_number <= ?
                    )
                WHERE mt.map_id = ?
            ''', (turn_number, map_id))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting all token positions at turn: {e}")
            return []

    # Game State Methods
    def save_game_state(self, world_id, current_turn, current_map_id=None, active_token_id=None, state_data=None):
        """Save the current game state."""
        try:
            if isinstance(state_data, dict):
                state_data = json.dumps(state_data)
                
            self.cursor.execute('''
                INSERT OR REPLACE INTO game_state 
                (world_id, current_turn, current_map_id, active_token_id, state_data, last_updated)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            ''', (world_id, current_turn, current_map_id, active_token_id, state_data))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False

    def get_game_state(self, world_id):
        """Get the current game state for a world."""
        try:
            self.cursor.execute('''
                SELECT current_turn, current_map_id, active_token_id, state_data, last_updated
                FROM game_state WHERE world_id = ?
            ''', (world_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting game state: {e}")
            return None

    # Enhanced Notes Methods
    def add_note_with_audio(self, title, content, audio_file=None, map_id=None, location_icon_id=None, 
                           x=-1, y=-1, note_type="text"):
        """Add a note with optional audio support."""
        try:
            self.cursor.execute('''
                INSERT INTO notes 
                (map_id, location_icon_id, title, content, audio_file, x, y, note_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (map_id, location_icon_id, title, content, audio_file, x, y, note_type))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding note: {e}")
            return None

    def get_notes_for_location(self, location_icon_id):
        """Get all notes associated with a location icon."""
        try:
            self.cursor.execute('''
                SELECT id, title, content, audio_file, note_type, created_at
                FROM notes WHERE location_icon_id = ?
                ORDER BY created_at DESC
            ''', (location_icon_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting notes for location: {e}")
            return []

    # Enhanced Map Methods
    def create_sub_map(self, parent_map_id, world_id, name, image_path, map_type="location", **kwargs):
        """Create a sub-map linked to a parent map."""
        try:
            map_data = {
                'world_id': world_id,
                'parent_map_id': parent_map_id,
                'name': name,
                'image_path': image_path,
                'map_type': map_type,
                'grid_size': kwargs.get('grid_size', 50),
                'grid_enabled': int(kwargs.get('grid_enabled', True)),
                'width': kwargs.get('width', 0),
                'height': kwargs.get('height', 0),
                'grid_color': kwargs.get('grid_color', '#FFFFFF'),
                'map_scale': kwargs.get('map_scale', 1.0),
                'grid_style': kwargs.get('grid_style', 'dashed'),
                'grid_opacity': kwargs.get('grid_opacity', 0.7)
            }
            
            return self.save_or_update_map(map_data)
        except Exception as e:
            print(f"Error creating sub-map: {e}")
            return None

    def get_sub_maps(self, parent_map_id):
        """Get all sub-maps for a parent map."""
        try:
            self.cursor.execute('''
                SELECT id, name, image_path, map_type, created_at
                FROM maps WHERE parent_map_id = ?
                ORDER BY name
            ''', (parent_map_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting sub-maps: {e}")
            return []

    def get_map_hierarchy(self, world_id):
        """Get the complete map hierarchy for a world."""
        try:
            # Get root maps (no parent)
            self.cursor.execute('''
                SELECT id, name, parent_map_id, map_type
                FROM maps WHERE world_id = ? AND parent_map_id IS NULL
                ORDER BY name
            ''', (world_id,))
            root_maps = self.cursor.fetchall()
            
            hierarchy = []
            for root_map in root_maps:
                map_tree = self._build_map_tree(root_map[0])  # root_map[0] is the id
                hierarchy.append(map_tree)
            
            return hierarchy
        except Exception as e:
            print(f"Error getting map hierarchy: {e}")
            return []

    def _build_map_tree(self, map_id):
        """Recursively build a map tree structure."""
        try:
            # Get map info
            self.cursor.execute('''
                SELECT id, name, parent_map_id, map_type, image_path
                FROM maps WHERE id = ?
            ''', (map_id,))
            map_info = self.cursor.fetchone()
            
            if not map_info:
                return None
                
            # Get child maps
            self.cursor.execute('''
                SELECT id FROM maps WHERE parent_map_id = ?
            ''', (map_id,))
            child_ids = [row[0] for row in self.cursor.fetchall()]
            
            # Build children recursively
            children = []
            for child_id in child_ids:
                child_tree = self._build_map_tree(child_id)
                if child_tree:
                    children.append(child_tree)
            
            return {
                'id': map_info[0],
                'name': map_info[1],
                'parent_map_id': map_info[2],
                'map_type': map_info[3],
                'image_path': map_info[4],
                'children': children
            }
        except Exception as e:
            print(f"Error building map tree: {e}")
            return None

    # Token drag and drop support
    def update_token_position(self, map_token_id, x, y, current_turn, has_moved=True):
        """Update token position and mark as moved for current turn."""
        try:
            # Update the token position
            self.cursor.execute('''
                UPDATE map_tokens 
                SET x = ?, y = ?, has_moved = ?, current_turn = ?
                WHERE id = ?
            ''', (x, y, 1 if has_moved else 0, current_turn, map_token_id))
            
            # Save position history
            self.save_token_position(map_token_id, current_turn, x, y)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating token position: {e}")
            return False

    def reset_token_movement_flags(self, map_id, current_turn):
        """Reset all has_moved flags for tokens on a map at the start of a new turn."""
        try:
            self.cursor.execute('''
                UPDATE map_tokens 
                SET has_moved = 0, current_turn = ?
                WHERE map_id = ?
            ''', (current_turn, map_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error resetting movement flags: {e}")
            return False

    # Enhanced token methods
    def get_map_tokens_with_history(self, map_id, turn_number=None):
        """Get tokens on a map with their historical positions if specified."""
        try:
            if turn_number is not None:
                return self.get_all_token_positions_at_turn(map_id, turn_number)
            else:
                # Get current positions
                self.cursor.execute('''
                    SELECT mt.id, mt.token_id, t.name, t.image_path, t.size, t.color, t.type,
                           mt.x, mt.y, mt.rotation, mt.active, mt.initiative, mt.has_moved,
                           t.current_hp, t.max_hp
                    FROM map_tokens mt
                    JOIN tokens t ON mt.token_id = t.id
                    WHERE mt.map_id = ?
                    ORDER BY mt.initiative DESC
                ''', (map_id,))
                return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting map tokens with history: {e}")
            return []

    # Migration and schema methods
    def _check_and_migrate_schema(self):
        """Check for known schema issues and migrate if necessary."""
        try:
            print("DEBUG: Checking database schema...")
            
            # Check if maps.world_id has NOT NULL constraint
            self.cursor.execute("PRAGMA table_info(maps)")
            columns_info = self.cursor.fetchall()
            world_id_info = None
            
            for col in columns_info:
                if col[1] == 'world_id':
                    world_id_info = col
                    break
            
            if world_id_info and world_id_info[3] == 1:
                print("INFO: Detected incorrect NOT NULL constraint on maps.world_id. Attempting migration...")
                self._migrate_maps_table_remove_world_id_not_null()
            else:
                print("DEBUG: Schema for maps.world_id appears correct.")

            # Check for new columns and add them if missing
            self._add_missing_columns()

        except sqlite3.Error as e:
            print(f"ERROR: Failed during schema check/migration: {e}")

    def _add_missing_columns(self):
        """Add any missing columns to existing tables."""
        try:
            # Check for parent_map_id in maps table
            self.cursor.execute("PRAGMA table_info(maps)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'parent_map_id' not in columns:
                print("Adding parent_map_id column to maps table...")
                self.cursor.execute('''
                    ALTER TABLE maps ADD COLUMN parent_map_id INTEGER
                    REFERENCES maps (id) ON DELETE CASCADE
                ''')
                
            if 'map_type' not in columns:
                print("Adding map_type column to maps table...")
                self.cursor.execute('''
                    ALTER TABLE maps ADD COLUMN map_type TEXT DEFAULT 'world'
                ''')
                
            # Check for has_moved in map_tokens table
            self.cursor.execute("PRAGMA table_info(map_tokens)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'has_moved' not in columns:
                print("Adding has_moved column to map_tokens table...")
                self.cursor.execute('''
                    ALTER TABLE map_tokens ADD COLUMN has_moved BOOLEAN DEFAULT 0
                ''')
                
            if 'current_turn' not in columns:
                print("Adding current_turn column to map_tokens table...")
                self.cursor.execute('''
                    ALTER TABLE map_tokens ADD COLUMN current_turn INTEGER DEFAULT 0
                ''')
                
            # Check for enhanced token columns
            self.cursor.execute("PRAGMA table_info(tokens)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'max_hp' not in columns:
                print("Adding max_hp column to tokens table...")
                self.cursor.execute('''
                    ALTER TABLE tokens ADD COLUMN max_hp INTEGER DEFAULT 10
                ''')
                
            if 'current_hp' not in columns:
                print("Adding current_hp column to tokens table...")
                self.cursor.execute('''
                    ALTER TABLE tokens ADD COLUMN current_hp INTEGER DEFAULT 10
                ''')
                
            if 'armor_class' not in columns:
                print("Adding armor_class column to tokens table...")
                self.cursor.execute('''
                    ALTER TABLE tokens ADD COLUMN armor_class INTEGER DEFAULT 10
                ''')
                
            self.conn.commit()
            print("Schema migration completed successfully.")
            
        except sqlite3.Error as e:
            print(f"Error adding missing columns: {e}")

    def _migrate_maps_table_remove_world_id_not_null(self):
        """Recreate the maps table to remove the NOT NULL constraint from world_id."""
        try:
            self.conn.execute("BEGIN TRANSACTION")
            print("  - Renaming existing maps table to maps_old...")
            self.conn.execute("ALTER TABLE maps RENAME TO maps_old")
            
            print("  - Creating new maps table with correct schema...")
            self.conn.execute('''
            CREATE TABLE maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER,
                parent_map_id INTEGER,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                grid_size INTEGER DEFAULT 50,
                grid_enabled INTEGER DEFAULT 1,
                width INTEGER DEFAULT 0,
                height INTEGER DEFAULT 0,
                grid_color TEXT DEFAULT '#FFFFFF',
                map_scale REAL DEFAULT 1.0,
                grid_style TEXT DEFAULT 'dashed',
                grid_opacity REAL DEFAULT 0.7,
                map_type TEXT DEFAULT 'world',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (world_id) REFERENCES worlds (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_map_id) REFERENCES maps (id) ON DELETE CASCADE
            )
            ''')

            print("  - Copying data from maps_old to new maps table...")
            cursor_old = self.conn.execute("PRAGMA table_info(maps_old)")
            old_columns = [col[1] for col in cursor_old.fetchall()]
            cursor_new = self.conn.execute("PRAGMA table_info(maps)")
            new_columns = [col[1] for col in cursor_new.fetchall()]
            
            common_columns = [col for col in old_columns if col in new_columns]
            select_cols_str = ", ".join(common_columns)
            insert_cols_str = ", ".join(common_columns)
            
            self.conn.execute(f"INSERT INTO maps ({insert_cols_str}) SELECT {select_cols_str} FROM maps_old")
            
            print("  - Dropping the old maps_old table...")
            self.conn.execute("DROP TABLE maps_old")
            
            self.conn.execute("COMMIT")
            print("INFO: Maps table migration completed successfully.")

        except sqlite3.Error as e:
            print(f"ERROR: Failed to migrate maps table: {e}. Rolling back.")
            try:
                self.conn.execute("ROLLBACK")
                cursor_check = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='maps_old'")
                if cursor_check.fetchone():
                     self.conn.execute("ALTER TABLE maps_old RENAME TO maps")
                     print("Attempted to restore original maps table name.")
            except sqlite3.Error as rb_e:
                print(f"ERROR: Failed during rollback/restore: {rb_e}")

    # Keep all existing methods for backward compatibility
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def create_world(self, name, description="", active_map_id=None):
        """Create a new world with optional active map."""
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            
            self.cursor.execute(
                "INSERT INTO worlds (name, description, last_accessed) VALUES (?, ?, datetime('now'))",
                (name, description)
            )
            world_id = self.cursor.lastrowid
            print(f"Database: World '{name}' created with ID: {world_id}")
            
            if active_map_id:
                self.cursor.execute("UPDATE maps SET world_id = ? WHERE id = ?", (world_id, active_map_id))
                print(f"Database: Assigned map ID {active_map_id} to world ID {world_id}")
            
            self.conn.commit()
            return world_id
            
        except sqlite3.IntegrityError:
            print(f"Database Error: World with name '{name}' already exists.")
            self.conn.rollback()
            return None
        except Exception as e:
            print(f"Database Error creating world: {e}")
            self.conn.rollback()
            return None

    def get_worlds_simple(self):
        """Get a simple list of worlds (id, name)."""
        try:
            self.cursor.execute("SELECT id, name FROM worlds ORDER BY name")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error fetching worlds: {e}")
            return []
    
    def get_all_worlds(self):
        """Get all worlds with detailed information."""
        try:
            self.cursor.execute("""
                SELECT w.id, w.name, w.description, w.created_at, w.last_accessed,
                       (SELECT id FROM maps WHERE world_id = w.id ORDER BY id LIMIT 1) as active_map_id
                FROM worlds w
                ORDER BY w.last_accessed DESC
            """)
            rows = self.cursor.fetchall()
            
            worlds = []
            for row in rows:
                world = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'last_accessed': row[4],
                    'active_map_id': row[5]
                }
                
                self.cursor.execute("SELECT id, name, image_path FROM maps WHERE world_id = ?", (world['id'],))
                world['maps'] = [{'id': r[0], 'name': r[1], 'image_path': r[2]} for r in self.cursor.fetchall()]
                
                worlds.append(world)
            
            return worlds
        except Exception as e:
            print(f"Database Error fetching all worlds: {e}")
            return []

    def load_world(self, world_id):
        """Load a world and update its last_accessed timestamp."""
        try:
            self.cursor.execute("UPDATE worlds SET last_accessed = datetime('now') WHERE id = ?", (world_id,))
            self.conn.commit()
            
            self.cursor.execute("""
                SELECT id, name, description, created_at, last_accessed,
                       (SELECT id FROM maps WHERE world_id = ? ORDER BY id LIMIT 1) as active_map_id
                FROM worlds
                WHERE id = ?
            """, (world_id, world_id))
            
            row = self.cursor.fetchone()
            if not row:
                print(f"Database Error: World ID {world_id} not found.")
                return None
                
            world = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': row[3],
                'last_accessed': row[4],
                'active_map_id': row[5]
            }
            
            if world['active_map_id']:
                map_data = self.get_map_by_id(world['active_map_id'])
                if map_data:
                    world['active_map'] = map_data
                
            self.cursor.execute("""
                SELECT id, name, image_path, grid_size, grid_color, grid_enabled 
                FROM maps 
                WHERE world_id = ?
            """, (world_id,))
            
            world['maps'] = [
                {
                    'id': r[0], 
                    'name': r[1], 
                    'image_path': r[2],
                    'grid_size': r[3],
                    'grid_color': r[4],
                    'grid_enabled': r[5]
                } for r in self.cursor.fetchall()
            ]
            
            return world
        except Exception as e:
            print(f"Database Error loading world: {e}")
            return None

    def world_name_exists(self, name):
        """Check if a world with the given name already exists."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM worlds WHERE name = ?", (name,))
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"Database Error checking world name: {e}")
            return False

    def delete_world(self, world_id):
        """Delete a world by ID."""
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            
            self.cursor.execute("UPDATE maps SET world_id = NULL WHERE world_id = ?", (world_id,))
            print(f"Database: Unassigned maps from world ID {world_id}")
            
            self.cursor.execute("DELETE FROM worlds WHERE id = ?", (world_id,))
            print(f"Database: World ID {world_id} deleted successfully")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Database Error deleting world {world_id}: {e}")
            self.conn.rollback()
            return False

    # Keep all other existing methods...
    def get_maps(self, world_id):
        """Get a simple list of maps for a specific world."""
        try:
            self.cursor.execute("SELECT id, name, image_path, grid_size FROM maps WHERE world_id = ? ORDER BY name", (world_id,))
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            print("Falling back to rowid for maps query")
            self.cursor.execute("SELECT rowid, name, image_path, grid_size FROM maps WHERE world_id = ? ORDER BY name", (world_id,))
            return self.cursor.fetchall()
    
    def get_map_by_id(self, map_id):
        """Get full map data by ID, including all its attributes."""
        try:
            self.cursor.execute("""
                SELECT id, world_id, name, image_path, grid_size, grid_enabled,
                       width, height, grid_color, map_scale, grid_style, grid_opacity,
                       parent_map_id, map_type
                FROM maps WHERE id = ?
            """, (map_id,))
            row = self.cursor.fetchone()
            if not row:
                print(f"Database: No map found with ID {map_id}")
                return None
                
            map_data = {
                'id': row[0],
                'world_id': row[1],
                'name': row[2],
                'image_path': row[3],
                'grid_size': row[4],
                'grid_enabled': bool(row[5]),
                'map_width_pixels': row[6],
                'map_height_pixels': row[7],
                'grid_color': row[8],
                'map_scale': row[9],
                'grid_style': row[10],
                'grid_opacity': row[11],
                'parent_map_id': row[12] if len(row) > 12 else None,
                'map_type': row[13] if len(row) > 13 else 'world'
            }
            return map_data
        except Exception as e:
            print(f"Database Error fetching map by ID {map_id}: {e}")
            return None

    def save_or_update_map(self, map_data):
        """Save a new map or update an existing one."""
        map_id = map_data.get('id')
        world_id = map_data.get('world_id')
        name = map_data.get('name')
        image_path = map_data.get('image_path')

        if not all([name, image_path]):
            print("Error: Missing required map data (name, image_path)")
            return None

        params = {
            'world_id': world_id,
            'parent_map_id': map_data.get('parent_map_id'),
            'name': name,
            'image_path': image_path,
            'grid_size': map_data.get('grid_size', 50),
            'grid_enabled': int(map_data.get('grid_enabled', True)),
            'width': map_data.get('width', 0),
            'height': map_data.get('height', 0),
            'grid_color': map_data.get('grid_color', '#FFFFFF'),
            'map_scale': map_data.get('map_scale', 1.0),
            'grid_style': map_data.get('grid_style', 'dashed'),
            'grid_opacity': map_data.get('grid_opacity', 0.7),
            'map_type': map_data.get('map_type', 'world')
        }

        try:
            if map_id:
                update_params = {k: v for k, v in params.items() if v is not None}
                if not update_params:
                    return map_id
                set_clause = ", ".join([f"{key} = :{key}" for key in update_params])
                query = f"UPDATE maps SET {set_clause} WHERE id = :id"
                update_params['id'] = map_id
                self.cursor.execute(query, update_params)
                print(f"Database: Updated map ID: {map_id}")
            else:
                insert_params = {k: v for k, v in params.items() if v is not None}
                columns = ", ".join(insert_params.keys())
                placeholders = ", ".join([f":{key}" for key in insert_params])
                query = f"INSERT INTO maps ({columns}) VALUES ({placeholders})"
                self.cursor.execute(query, insert_params)
                map_id = self.cursor.lastrowid
                print(f"Database: Created new map ID: {map_id}")

            self.conn.commit()
            return map_id
        except sqlite3.Error as e:
            print(f"Database Error saving/updating map: {e}")
            self.conn.rollback()
            return None

    def get_unassigned_maps(self):
        """Get a list of maps not assigned to any world."""
        try:
            self.cursor.execute("""
                SELECT id, name 
                FROM maps
                WHERE world_id IS NULL
                ORDER BY name
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Database Error fetching unassigned maps: {e}")
            return []

    # Add other existing methods as needed...
    def get_tokens(self):
        """Get all tokens."""
        try:
            self.cursor.execute("SELECT id, name, image_path, size, color, type, notes, initiative, max_hp, current_hp FROM tokens ORDER BY name")
            return self.cursor.fetchall()
        except sqlite3.OperationalError:
            print("Falling back to rowid for tokens query")
            self.cursor.execute("SELECT rowid, name, image_path, size, color, type, notes, initiative FROM tokens ORDER BY name")
            return self.cursor.fetchall()

    def add_token(self, name, image_path, size=1, color="255,0,0", token_type="character", notes="", initiative=0, max_hp=10):
        """Add a new token."""
        if isinstance(color, (tuple, list)):
            color = ",".join(str(c) for c in color)
            
        self.cursor.execute(
            "INSERT INTO tokens (name, image_path, size, color, type, notes, initiative, max_hp, current_hp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, image_path, size, color, token_type, notes, initiative, max_hp, max_hp)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_map_tokens(self, map_id):
        """Get all tokens on a map."""
        return self.get_map_tokens_with_history(map_id)

    def add_map_token(self, map_id, token_id, x, y, rotation=0, active=True, initiative=0):
        """Add a token to a map."""
        self.cursor.execute(
            "INSERT INTO map_tokens (map_id, token_id, x, y, rotation, active, initiative, has_moved, current_turn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (map_id, token_id, x, y, rotation, active, initiative, 0, 0)
        )
        self.conn.commit()
        return self.cursor.lastrowid