# Monkey Jax

A 3D platformer game built with PyOpenGL where you control a monkey navigating through platforms, dodging barrels, and collecting coins while avoiding enemies.

## Overview

Monkey Jax is an action-packed 3D game inspired by classic arcade platformers. Guide your monkey character through increasingly difficult levels, climb ladders, jump between platforms, and use your rock-throwing skills to defeat enemies while avoiding their barrel attacks.

## Features

- **Three Difficulty Levels**: Easy, Medium, and Hard with varying enemy counts and speeds
- **3D Graphics**: Full 3D environment with OpenGL rendering
- **Platform Mechanics**: Jump and climb ladders to navigate between platforms
- **Combat System**: Throw rocks at enemies and deflect barrels
- **Dynamic Camera**: Switch between first-person and third-person views
- **Progressive Difficulty**: Each level increases challenge with more enemies and faster gameplay
- **Cheat Mode**: Invincibility option for practice or exploration

## Requirements

- Python 3.x
- PyOpenGL
- PyOpenGL-accelerate (recommended)
- GLUT (usually included with PyOpenGL)

### Installation

```bash
pip install PyOpenGL PyOpenGL-accelerate
```

## How to Play

### Starting the Game
1. Run the game: `python monkey_game.py`
2. Select difficulty level:
   - Press **E** for Easy (3 enemies, slower speed)
   - Press **M** for Medium (7 enemies, normal speed)  
   - Press **H** for Hard (10 enemies, faster speed)

### Controls

#### Movement
- **W** - Move forward/up
- **A** - Move left
- **S** - Move backward/down
- **D** - Move right
- **Space** - Jump
- **Arrow Keys** - Control camera direction and monkey facing direction

#### Combat & Interaction
- **Left Mouse Button** - Throw rock
- **F** - Alternative rock throwing
- **Right Mouse Button** - Toggle camera view (first-person/third-person)

#### Special Controls
- **X** - Rotate monkey 90 degrees
- **C** - Toggle cheat mode (invincibility)
- **R** - Restart game (when game over)
- **ESC** - Exit game

### Objective

1. **Survive**: Avoid enemy guards and their barrel attacks
2. **Fight Back**: Throw rocks to defeat enemies (they respawn automatically)
3. **Collect Coins**: Reach the golden coin on the highest platform to complete the level
4. **Progress**: Complete all three difficulty levels to win

### Game Mechanics

#### Platforms and Ladders
- Use ladders to climb between platforms
- Monkey automatically detects platform edges
- Jump between nearby platforms or fall safely to lower levels

#### Combat System
- Enemies continuously move toward the monkey
- Enemies throw barrels at regular intervals
- Hit enemies with rocks to score points (20 points per hit)
- Deflect barrels with rocks for bonus points (10 points)
- Dodging barrels without being hit grants 5 points

#### Health and Lives
- Start with 3 lives
- Lose 1 life when hit by barrels or touching enemies
- Game ends when all lives are lost
- Shield power-up provides temporary invincibility

### Scoring System

- **Enemy Hit**: 20 points
- **Barrel Deflected**: 10 points
- **Barrel Dodged**: 5 points
- **Level Completion**: Bonus based on remaining lives

## Game Elements

### Environment
- **Checkered Ground**: Green grass-textured playing field
- **Wooden Platforms**: Multiple levels at different heights
- **Ladders**: Connect platforms vertically
- **Palm Trees**: Decorative elements at map corners
- **Boundary Walls**: Prevent falling off the map

### Characters
- **Monkey**: Player character with detailed 3D model
- **Enemy Guards**: Red uniformed guards that chase the player
- **Scaling Animation**: Enemies pulse in size continuously

### Items
- **Golden Coin**: Level completion objective
- **Barrels**: Enemy projectiles with physics simulation
- **Rocks**: Player projectiles for combat

## Technical Features

- **3D Transformations**: Full matrix-based 3D positioning and rotation
- **Physics Simulation**: Gravity, jumping, and projectile physics
- **Collision Detection**: Player-enemy, projectile-target interactions
- **Dynamic Lighting**: OpenGL lighting for 3D depth
- **Perspective Camera**: Configurable field of view and camera positioning

## Game States

1. **Start Screen**: Difficulty selection with animated swinging monkey
2. **Game Play**: Main game loop with all mechanics active
3. **Level Complete**: Victory screen with score display
4. **Game Over**: Restart option when lives are depleted
5. **Final Victory**: Completion of all difficulty levels

## Tips for Players

- Use ladders strategically to avoid enemy clusters
- Time your jumps carefully between platforms
- Aim rocks ahead of moving enemies for better accuracy
- Use the camera toggle to get better aiming angles
- In first-person mode, mouse movement affects aiming direction
- Higher platforms are generally safer but harder to reach

## Development Notes

This game demonstrates:
- 3D graphics programming with OpenGL
- Game state management
- Physics simulation
- User input handling
- Collision detection algorithms
- Progressive difficulty scaling

## Troubleshooting

- **Game won't start**: Ensure PyOpenGL is properly installed
- **Graphics issues**: Update graphics drivers
- **Performance problems**: Reduce window size or close other applications
- **Control issues**: Check that GLUT is properly configured

## Credits

Built using Python and PyOpenGL for educational purposes. Game design inspired by classic arcade platformers.
