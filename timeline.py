import json
import datetime
from config import *

class Timeline:
    """Enhanced timeline system with turn-by-turn tracking and history scrubbing."""
    
    def __init__(self, database):
        """Initialize the timeline."""
        self.db = database
        self.current_world_id = None
        self.current_map_id = None
        self.current_turn = 0
        self.max_turn = 0
        self.initiative_order = []  # List of token instance IDs in initiative order
        self.is_scrubbing = False  # Whether we're in timeline scrubbing mode
        self.scrub_turn = 0  # The turn we're currently viewing while scrubbing
        
        # Cache for timeline data
        self.timeline_cache = {}
        self.token_positions_cache = {}
    
    def update(self, time_delta):
        """Update timeline state if needed."""
        # No time-based updates needed for now
        pass
    
    def set_world(self, world_id):
        """Set the current world and load its state."""
        self.current_world_id = world_id
        self.load_world_state()
    
    def set_map(self, map_id):
        """Set the current map and load its initiative order."""
        self.current_map_id = map_id
        self.load_initiative_order()
        self.load_map_timeline()
    
    def load_world_state(self):
        """Load the current state for the world."""
        if not self.current_world_id:
            return
            
        # Get the saved game state
        state = self.db.get_game_state(self.current_world_id)
        if state:
            self.current_turn = state[0]  # current_turn
            self.current_map_id = state[1]  # current_map_id
            # active_token_id = state[2]
            # state_data = state[3]
            # last_updated = state[4]
        
        # Get the maximum turn number from timeline events
        self.max_turn = self.db.get_max_turn_number(self.current_world_id)
        if self.max_turn < self.current_turn:
            self.max_turn = self.current_turn
    
    def load_initiative_order(self):
        """Load the initiative order for the current map."""
        if not self.current_map_id:
            return
        
        # Get tokens on the map with initiative values
        tokens = self.db.get_map_tokens_with_history(self.current_map_id)
        
        # Sort by initiative value, descending
        self.initiative_order = []
        
        for token in sorted(tokens, key=lambda t: t[11] if len(t) > 11 else 0, reverse=True):
            # token[11] should be initiative, token[0] should be map_token_id
            if len(token) > 11 and token[11] > 0:
                self.initiative_order.append(token[0])
    
    def load_map_timeline(self):
        """Load timeline events for the current map."""
        if not self.current_world_id:
            return
            
        # Load timeline events into cache
        events = self.db.get_timeline_events(self.current_world_id)
        self.timeline_cache = {}
        
        for event in events:
            turn = event[2]  # turn_number
            if turn not in self.timeline_cache:
                self.timeline_cache[turn] = []
            self.timeline_cache[turn].append({
                'id': event[0],
                'event_type': event[3],
                'title': event[4],
                'description': event[5],
                'data': json.loads(event[6]) if event[6] else None,
                'timestamp': event[7]
            })
    
    def next_turn(self):
        """Advance to the next turn in the initiative order."""
        if self.is_scrubbing:
            return None  # Can't advance turns while scrubbing
            
        self.current_turn += 1
        
        # Reset movement flags for all tokens on the current map
        if self.current_map_id:
            self.db.reset_token_movement_flags(self.current_map_id, self.current_turn)
        
        # Update max turn if needed
        if self.current_turn > self.max_turn:
            self.max_turn = self.current_turn
        
        # Save the game state
        self._save_current_state()
        
        # Log the turn advancement
        self.log_event("turn_start", f"Turn {self.current_turn} begins", {
            "turn": self.current_turn,
            "initiative_order": self.initiative_order.copy()
        })
        
        return self.get_current_token()
    
    def previous_turn(self):
        """Go back to the previous turn (only available when scrubbing)."""
        if not self.is_scrubbing:
            self.start_scrubbing()
        
        if self.scrub_turn > 0:
            self.scrub_turn -= 1
            return self.get_current_token_at_turn(self.scrub_turn)
        
        return None
    
    def start_scrubbing(self):
        """Enter timeline scrubbing mode."""
        self.is_scrubbing = True
        self.scrub_turn = self.current_turn
        print(f"Timeline: Started scrubbing at turn {self.scrub_turn}")
    
    def stop_scrubbing(self):
        """Exit timeline scrubbing mode and return to current turn."""
        self.is_scrubbing = False
        self.scrub_turn = self.current_turn
        print(f"Timeline: Stopped scrubbing, returned to turn {self.current_turn}")
    
    def scrub_to_turn(self, turn_number):
        """Scrub to a specific turn number."""
        if not self.is_scrubbing:
            self.start_scrubbing()
        
        self.scrub_turn = max(0, min(turn_number, self.max_turn))
        print(f"Timeline: Scrubbed to turn {self.scrub_turn}")
        return self.get_token_positions_at_turn(self.scrub_turn)
    
    def get_current_token(self):
        """Get the token instance ID for the current turn."""
        if not self.initiative_order:
            return None
        
        if self.is_scrubbing:
            return self.get_current_token_at_turn(self.scrub_turn)
        
        # Calculate which token's turn it is based on current turn
        if len(self.initiative_order) > 0:
            token_index = (self.current_turn - 1) % len(self.initiative_order)
            return self.initiative_order[token_index]
        
        return None
    
    def get_current_token_at_turn(self, turn_number):
        """Get the active token at a specific turn."""
        if not self.initiative_order or turn_number <= 0:
            return None
            
        token_index = (turn_number - 1) % len(self.initiative_order)
        return self.initiative_order[token_index]
    
    def get_token_positions_at_turn(self, turn_number):
        """Get all token positions at a specific turn."""
        if not self.current_map_id:
            return []
        
        # Check cache first
        cache_key = f"{self.current_map_id}_{turn_number}"
        if cache_key in self.token_positions_cache:
            return self.token_positions_cache[cache_key]
        
        # Get positions from database
        positions = self.db.get_all_token_positions_at_turn(self.current_map_id, turn_number)
        
        # Cache the result
        self.token_positions_cache[cache_key] = positions
        
        return positions
    
    def get_current_display_turn(self):
        """Get the turn number currently being displayed."""
        return self.scrub_turn if self.is_scrubbing else self.current_turn
    
    def get_timeline_events_for_turn(self, turn_number):
        """Get all events that occurred during a specific turn."""
        return self.timeline_cache.get(turn_number, [])
    
    def get_timeline_summary(self, start_turn=None, end_turn=None):
        """Get a summary of timeline events within a range."""
        if start_turn is None:
            start_turn = max(0, self.current_turn - 10)
        if end_turn is None:
            end_turn = self.current_turn
        
        summary = []
        for turn in range(start_turn, end_turn + 1):
            events = self.get_timeline_events_for_turn(turn)
            if events:
                summary.append({
                    'turn': turn,
                    'event_count': len(events),
                    'events': events
                })
        
        return summary
    
    def log_event(self, event_type, title, data=None, description=""):
        """Log an event to the timeline."""
        if not self.current_world_id:
            return None
        
        current_turn = self.current_turn
        if self.is_scrubbing:
            print("Warning: Cannot log events while scrubbing timeline")
            return None
        
        event_id = self.db.add_timeline_event(
            self.current_world_id,
            current_turn,
            event_type,
            title,
            description,
            data,
            self.current_map_id
        )
        
        # Update cache
        if current_turn not in self.timeline_cache:
            self.timeline_cache[current_turn] = []
        
        self.timeline_cache[current_turn].append({
            'id': event_id,
            'event_type': event_type,
            'title': title,
            'description': description,
            'data': data,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        return event_id
    
    def log_token_moved(self, map_token_id, token_name, from_pos, to_pos):
        """Log a token movement event."""
        return self.log_event(
            "token_move", 
            f"{token_name} moved",
            {
                "map_token_id": map_token_id,
                "from": from_pos,
                "to": to_pos,
                "distance": self._calculate_distance(from_pos, to_pos)
            },
            f"Moved from ({from_pos[0]}, {from_pos[1]}) to ({to_pos[0]}, {to_pos[1]})"
        )
    
    def log_token_action(self, map_token_id, token_name, action_text, action_type="custom"):
        """Log a token action and save it to the database."""
        # Save the action to the database
        self.db.add_token_action(map_token_id, self.current_turn, action_text, action_type)
        
        # Log it as a timeline event
        return self.log_event(
            "token_action",
            f"{token_name}: {action_text}",
            {
                "map_token_id": map_token_id,
                "action_type": action_type,
                "action_text": action_text
            }
        )
    
    def log_token_added(self, map_token_id, token_name, position):
        """Log a token added event."""
        return self.log_event(
            "token_add", 
            f"{token_name} enters the battlefield",
            {
                "map_token_id": map_token_id,
                "position": position
            }
        )
    
    def log_token_removed(self, map_token_id, token_name, position):
        """Log a token removed event."""
        return self.log_event(
            "token_remove", 
            f"{token_name} leaves the battlefield",
            {
                "map_token_id": map_token_id,
                "position": position
            }
        )
    
    def log_combat_event(self, attacker_name, target_name, damage=None, hit=True):
        """Log a combat event."""
        if hit and damage:
            title = f"{attacker_name} hits {target_name} for {damage} damage"
        elif hit:
            title = f"{attacker_name} hits {target_name}"
        else:
            title = f"{attacker_name} misses {target_name}"
        
        return self.log_event(
            "combat",
            title,
            {
                "attacker": attacker_name,
                "target": target_name,
                "damage": damage,
                "hit": hit
            }
        )
    
    def log_note_added(self, note_id, title, location=None):
        """Log a note added event."""
        return self.log_event(
            "note_add", 
            f"Note added: {title}",
            {
                "note_id": note_id,
                "location": location
            }
        )
    
    def log_location_discovered(self, location_name, location_type="generic"):
        """Log a location discovery event."""
        return self.log_event(
            "location_discover",
            f"Discovered {location_name}",
            {
                "location_name": location_name,
                "location_type": location_type
            }
        )
    
    def log_map_change(self, old_map_name, new_map_name, new_map_id):
        """Log a map change event."""
        return self.log_event(
            "map_change",
            f"Moved to {new_map_name}",
            {
                "old_map": old_map_name,
                "new_map": new_map_name,
                "new_map_id": new_map_id
            },
            f"Party moved from {old_map_name} to {new_map_name}"
        )
    
    def save_token_state(self, map_token_id, x, y, hp=None, status_effects=None):
        """Save token position and state for the current turn."""
        if self.is_scrubbing:
            print("Warning: Cannot save token state while scrubbing")
            return False
        
        return self.db.save_token_position(
            map_token_id, 
            self.current_turn, 
            x, y, 
            hp, 
            status_effects
        )
    
    def update_token_position(self, map_token_id, x, y, token_name=None):
        """Update a token's position and log the movement."""
        if self.is_scrubbing:
            print("Warning: Cannot move tokens while scrubbing")
            return False
        
        # Get the old position first
        old_pos = None
        if token_name:  # Only log if we have the token name
            # Get current position from database
            current_tokens = self.db.get_map_tokens_with_history(self.current_map_id)
            for token in current_tokens:
                if token[0] == map_token_id:  # map_token_id
                    old_pos = (token[7], token[8])  # x, y
                    break
        
        # Update the position in the database
        success = self.db.update_token_position(map_token_id, x, y, self.current_turn, has_moved=True)
        
        if success:
            # Save the position state
            self.save_token_state(map_token_id, x, y)
            
            # Log the movement if we have the necessary info
            if token_name and old_pos and old_pos != (x, y):
                self.log_token_moved(map_token_id, token_name, old_pos, (x, y))
            
            # Clear position cache since positions have changed
            self.token_positions_cache.clear()
        
        return success
    
    def get_recent_events(self, limit=10):
        """Get the most recent events from the timeline."""
        if not self.current_world_id:
            return []
        
        # Get events around the current display turn
        display_turn = self.get_current_display_turn()
        start_turn = max(0, display_turn - 5)
        end_turn = display_turn + 1
        
        return self.db.get_timeline_events(self.current_world_id, start_turn, end_turn, limit)
    
    def reset_initiative(self):
        """Clear the initiative order."""
        self.initiative_order = []
    
    def set_token_initiative(self, map_token_id, initiative_value):
        """Set the initiative value for a token and update the order."""
        # Update token initiative in database would go here
        # For now, just reload the initiative order
        self.load_initiative_order()
    
    def _save_current_state(self):
        """Save the current game state to the database."""
        if self.current_world_id and not self.is_scrubbing:
            self.db.save_game_state(
                self.current_world_id,
                self.current_turn,
                self.current_map_id
            )
    
    def _calculate_distance(self, pos1, pos2):
        """Calculate the distance between two positions."""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return round((dx**2 + dy**2)**0.5, 2)
    
    def export_timeline(self, start_turn=None, end_turn=None):
        """Export timeline events as JSON for backup or sharing."""
        if not self.current_world_id:
            return None
        
        events = self.db.get_timeline_events(self.current_world_id, start_turn, end_turn)
        
        export_data = {
            'world_id': self.current_world_id,
            'current_turn': self.current_turn,
            'max_turn': self.max_turn,
            'export_timestamp': datetime.datetime.now().isoformat(),
            'events': []
        }
        
        for event in events:
            export_data['events'].append({
                'turn_number': event[2],
                'event_type': event[3],
                'title': event[4],
                'description': event[5],
                'data': json.loads(event[6]) if event[6] else None,
                'timestamp': event[7]
            })
        
        return json.dumps(export_data, indent=2)
    
    def get_timeline_statistics(self):
        """Get statistics about the timeline."""
        if not self.current_world_id:
            return {}
        
        events = self.db.get_timeline_events(self.current_world_id)
        
        stats = {
            'total_turns': self.max_turn,
            'total_events': len(events),
            'events_by_type': {},
            'most_active_turn': None,
            'most_active_turn_events': 0
        }
        
        turn_counts = {}
        
        for event in events:
            event_type = event[3]  # event_type
            turn = event[2]  # turn_number
            
            # Count by type
            if event_type not in stats['events_by_type']:
                stats['events_by_type'][event_type] = 0
            stats['events_by_type'][event_type] += 1
            
            # Count by turn
            if turn not in turn_counts:
                turn_counts[turn] = 0
            turn_counts[turn] += 1
        
        # Find most active turn
        if turn_counts:
            most_active = max(turn_counts.items(), key=lambda x: x[1])
            stats['most_active_turn'] = most_active[0]
            stats['most_active_turn_events'] = most_active[1]
        
        return stats