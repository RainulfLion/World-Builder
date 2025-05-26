Gemini TTS - Enhanced Tabletop RPG Simulator
A comprehensive digital tabletop simulator for role-playing games built with Python and Pygame, now with advanced timeline tracking, location management, and interactive storytelling features.
🎯 Overview
Gemini TTS is designed to enhance tabletop RPG sessions by providing Game Masters and players with a versatile virtual tabletop environment. Whether you're running a complex campaign or playing out character interactions, this tool helps visualize and manage your stories with intuitive map and token handling.
✨ Key Features
🌍 World Management System

Create and manage multiple campaign worlds
Organize maps within worlds with hierarchical structure
Cascading map system - click on city icons to open city maps, inn icons to open inn maps, etc.
Delete worlds when campaigns end
World-specific timeline tracking

🗺️ Enhanced Map Management

Interactive map viewer with grid system
Smooth camera controls with panning and zooming
Support for various map image formats
Hierarchical map system - world maps → city maps → building maps
Location icons with customizable types (cities, inns, dungeons, forests, etc.)

🎭 Advanced Token System

Drag-and-drop token movement
Track initiative order in combat
Manage token stats, HP, and status effects
Save token positions and stats every turn
Token action recording system
Visual indicators for tokens that have moved

⏰ Revolutionary Timeline System

Turn-based timeline tracking with scrubbing
Timeline slider - slide back and forth to see token positions and actions at different points
Complete history of all movements and actions
Visual timeline with event markers
Rewind functionality - see exactly where tokens were and what they did on any previous turn
Export timeline data for campaign records

📝 Notes and Location System

Location icons that open detailed notes
Text and audio note support for each location
Context-sensitive notes - click on a tavern icon to see/hear tavern-specific notes
Audio recording and playback for immersive storytelling
Searchable notes database

🎲 Built-in Dice Roller

Support for standard RPG dice (d4, d6, d8, d10, d12, d20, d100)
Roll multiple dice at once
Roll history tracking

🛠️ Map Creator Tools

Built-in map creation and editing
Customizable grid overlays
Wall and terrain placement tools

📊 Game State Management

Automatic saving of all game states
Complete session recovery
Campaign progress tracking
Statistical analysis of gameplay

🔧 Technical Architecture

Core Application: main.py - Main game loop and application flow
Configuration: config.py - Settings for screen dimensions, colors, and parameters
Database: database.py - Enhanced SQLite database with timeline support
Map Handling: map_view.py and map_creator.py - Map display and creation
Timeline System: timeline.py - Advanced turn tracking and history management
UI System: ui_manager.py and ui_elements.py - Enhanced user interface
Enhanced UI Elements: Support for drag-and-drop, timeline scrubbing, and location management

🚀 Getting Started
Prerequisites

Python 3.8 or higher
Git (for cloning the repository)

Installation

Clone the repository
bashgit clone https://github.com/your-username/gemini-tts.git
cd gemini-tts

Create a virtual environment (recommended)
bashpython -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

Install dependencies
bashpip install -r requirements.txt

Run the application
bashpython main.py


📖 Usage Guide
Getting Started

Launch the application with python main.py
Create your first world: File → Create World
Add maps to your world: Tools → Create Map
Create tokens: Tools → Create Token
Start your session!

World and Map Management

Creating Worlds: File → Create World, then assign existing maps or create new ones
Loading Worlds: File → Load World to continue previous sessions
Hierarchical Maps: Create location icons on world maps that link to detailed sub-maps
Map Navigation: Use breadcrumb navigation to move between map levels

Timeline and Turn Management

Timeline Slider: Use the slider at the bottom to scrub through game history
Turn Advancement: Click "Next Turn" to advance the timeline
History Viewing: Slide the timeline back to see exactly where tokens were at any point
Action Recording: Right-click tokens to record actions taken during their turn

Token Management

Adding Tokens: Drag tokens from the right panel onto the map
Moving Tokens: Click and drag tokens to new positions
Token Actions: Right-click tokens to open the actions window
Initiative Tracking: Set token initiative values to determine turn order

Location and Notes System

Adding Locations: Right-click on maps to place location icons
Location Types: Choose from cities, inns, dungeons, forests, mountains, etc.
Notes: Click location icons to add text or audio notes
Sub-Maps: Link location icons to detailed sub-maps for exploration

Advanced Features

Audio Notes: Record voice notes for locations and story elements
Timeline Export: Export your campaign timeline for record-keeping
Token State Tracking: Automatic HP and status effect tracking
Campaign Statistics: View detailed statistics about your sessions

🎮 Controls
Map Navigation

Arrow Keys: Pan the map view
Mouse Wheel: Scroll vertically
Middle Mouse Button: Click and drag to pan
Left Click: Select tokens or place items
Right Click: Context menus for advanced options

Timeline Controls

Timeline Slider: Drag to scrub through game history
Next/Previous Turn: Arrow buttons next to timeline
Current Turn Display: Shows active turn number

Token Controls

Click and Drag: Move tokens
Right Click: Open action/notes window
Double Click: Quick access to token stats

📁 Data Storage
All game data is stored in an SQLite database at data/game_data.db, including:

World definitions and hierarchies
Map data and images
Token information and positions
Complete timeline events
Turn-by-turn position history
Token actions and notes
Location data and audio files

🎨 Customization
Themes and Appearance

Theme files: Edit theme.json for custom UI colors
Configuration: Modify config.py for layout and behavior settings
Custom Assets: Add your own token and map images to appropriate folders

Map Types and Icons

Location Types: Customize location icon types in the database
Grid Settings: Adjust grid size, color, and opacity per map
Audio Support: Add custom audio files for immersive experiences

🔍 Troubleshooting
Common Issues
Database errors on startup:

Ensure the data/ directory has write permissions
Check that SQLite is properly installed
Try deleting data/game_data.db to reset (you'll lose save data)

Audio not working:

Install audio dependencies: pip install pydub simpleaudio
Check system audio drivers and permissions
Verify audio files are in supported formats (MP3, WAV, OGG)

Performance issues:

Reduce map image sizes (recommended: 2048x2048 max)
Close other applications to free up memory
Consider reducing the number of tokens on screen simultaneously

Import/Export problems:

Ensure file paths don't contain special characters
Check that source files aren't corrupted
Verify you have read/write permissions for the data directory

Debug Mode
Enable debug mode by setting DEBUG_MODE = True in config.py for additional logging and performance information.
🚧 Known Limitations

Maximum recommended tokens per map: 50 (for optimal performance)
Map image size limit: 4096x4096 pixels
Audio file size limit: 100MB per file
Timeline history: Limited by available disk space
Concurrent users: Single-user application (not networked)

🔄 Recent Updates
Version 2.0 - Enhanced Timeline and Location System

New Timeline Scrubbing: Slide through game history to see token positions at any turn
Location Icon System: Place interactive location markers that open sub-maps
Audio Notes Support: Record and play audio notes for immersive storytelling
Token Action Tracking: Record what each token does during their turn
Drag-and-Drop Tokens: Intuitive token movement with automatic position saving
Hierarchical Maps: Create cascading map systems (world → city → building)
Enhanced Database: Complete rewrite for better performance and features
Visual Timeline: See events and actions represented on an interactive timeline

Performance Improvements

Optimized rendering for large maps and many tokens
Caching system for timeline data and token positions
Reduced memory usage through better asset management
Faster database queries with indexed tables

🤝 Contributing
We welcome contributions! Here's how you can help:
Development Setup

Fork the repository
Create a feature branch: git checkout -b feature-name
Make your changes following the existing code style
Test thoroughly with different scenarios
Submit a pull request with a clear description

Areas for Contribution

New location icon types and visual improvements
Additional audio format support
Network multiplayer functionality
Advanced combat automation
Custom scripting system for game rules
Mobile/tablet interface adaptation
Integration with popular RPG systems

Bug Reports

Use the GitHub Issues template
Include steps to reproduce
Attach relevant log files from the console
Specify your operating system and Python version

📋 Roadmap
Planned Features

🌐 Network Multiplayer: Allow multiple players to connect to the same session
📱 Touch Interface: Better support for tablets and touch screens
🎵 Dynamic Audio: Background music and ambient sound management
📜 Character Sheets: Integrated character sheet management
🎲 Advanced Dice: Custom dice types and automated rule calculations
📊 Campaign Analytics: Detailed statistics and reporting
🔌 Plugin System: Allow community-created extensions
☁️ Cloud Sync: Save campaigns to cloud storage

Integration Goals

D&D Beyond API: Import character data
Roll20 Compatibility: Import existing campaigns
Foundry VTT Integration: Asset sharing capabilities
Discord Bot: Session notifications and dice rolling

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

Pygame Community for the excellent game development framework
pygame-gui developers for the UI components
SQLite Team for the robust database engine
RPG Community for feedback and feature suggestions
Beta Testers who helped identify bugs and usability issues

📞 Support
Getting Help

Documentation: Check this README and in-code comments
GitHub Issues: Report bugs and request features
Community Discord: Join our community server (link coming soon)
Email Support: contact@gemini-tts.dev (coming soon)

System Requirements
Minimum Requirements:

Python 3.8+
4GB RAM
1GB free disk space
DirectX 9.0c compatible graphics
Audio device for sound features

Recommended Requirements:

Python 3.10+
8GB RAM
2GB free disk space
Dedicated graphics card
Microphone for audio recording
Large display (1920x1080 or higher)

🎯 Use Cases
For Game Masters

Campaign Management: Organize multiple worlds and storylines
Session Preparation: Pre-place tokens and set up encounters
Story Documentation: Record important moments with audio notes
Player Engagement: Use visual and audio elements for immersion
Session Review: Go back through timeline to remember what happened

For Players

Character Tracking: See your character's journey through the timeline
Action Recording: Document what your character does each turn
Location Discovery: Explore detailed maps and locations
Story Participation: Add notes and observations to locations

For Content Creators

Campaign Streaming: Show viewers the visual timeline of events
Tutorial Creation: Demonstrate RPG concepts with visual aids
Story Documentation: Create detailed records of epic campaigns
Community Sharing: Export and share interesting campaign moments


🏁 Quick Start Checklist

 Install Python 3.8+
 Clone/download the repository
 Install requirements: pip install -r requirements.txt
 Run the application: python main.py
 Create your first world: File → Create World
 Add a map: Tools → Create Map
 Create some tokens: Tools → Create Token
 Place tokens on the map by dragging them
 Start your first turn and begin your adventure!

Ready to enhance your tabletop RPG experience? Download Gemini TTS today and bring your campaigns to life! 🎲✨