import re
import random

class DiceRoller:
    """Logic for the dice roller."""
    
    def __init__(self):
        """Initialize the dice roller."""
        self.dice_pattern = re.compile(r'(\d+)d(\d+)([+-]\d+)?')
        self.last_roll = None
        self.last_result = None
        
    def parse_dice_string(self, dice_string):
        """Parse a dice expression like "2d6+3"."""
        # Strip whitespace and convert to lowercase
        dice_string = dice_string.strip().lower()
        
        # Extract dice info using regex
        match = self.dice_pattern.match(dice_string)
        if not match:
            return None
            
        # Extract number of dice, dice type, and modifier
        num_dice = int(match.group(1))
        dice_type = int(match.group(2))
        modifier_str = match.group(3)
        
        # Parse modifier if present
        modifier = 0
        if modifier_str:
            modifier = int(modifier_str)
            
        return {
            'num_dice': num_dice,
            'dice_type': dice_type,
            'modifier': modifier
        }
        
    def roll(self, dice_string):
        """Roll dice based on the provided dice expression."""
        # Parse the dice expression
        dice_info = self.parse_dice_string(dice_string)
        if not dice_info:
            return f"Invalid dice expression: {dice_string}"
            
        # Unpack dice info
        num_dice = dice_info['num_dice']
        dice_type = dice_info['dice_type']
        modifier = dice_info['modifier']
        
        # Validate dice parameters
        if num_dice <= 0 or dice_type <= 0:
            return f"Invalid dice parameters: {dice_string}"
        if num_dice > 100:  # Reasonable upper limit
            return f"Too many dice (max 100): {dice_string}"
            
        # Roll the dice
        rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
        
        # Calculate total
        total = sum(rolls) + modifier
        
        # Store roll info
        self.last_roll = {
            'expression': dice_string,
            'rolls': rolls,
            'modifier': modifier,
            'total': total
        }
        
        # Format result
        result = f"Rolled {dice_string}: {total}"
        if len(rolls) > 1 or modifier != 0:
            details = " + ".join(str(r) for r in rolls)
            if modifier > 0:
                details += f" + {modifier}"
            elif modifier < 0:
                details += f" - {abs(modifier)}"
            result += f" ({details})"
            
        self.last_result = result
        return result
        
    def get_last_roll(self):
        """Get details of the last roll."""
        return self.last_roll
        
    def get_last_result(self):
        """Get formatted result of the last roll."""
        return self.last_result or "No dice rolled yet."