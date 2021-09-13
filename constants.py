"""
Name: constants.py
Author: Hugh McCutcheon
Description: A file containing all of the constant variables used by my code
"""
import arcade

TILE_SPRITE_SCALING = 1
PLAYER_SCALING = 1

SCREEN_WIDTH = int(arcade.window_commands.get_display_size()[0]/1)
SCREEN_HEIGHT = int(arcade.window_commands.get_display_size()[1]/1)
SCREEN_TITLE = "Kinarough"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SPRITE_SCALING)
SCALING = 1

# Physics
JUMP_SPEED = 20
GRAVITY = 0.75
MAX_SPEED = 1000000000000
ACCELERATION_RATE = 0.5
HORIZONTAL_DAMPING = 0.17
HORIZONTAL_DAMPING_STOPPING = 0.4
CUT_JUMP_HEIGHT = 0.5
FRICTION = 0.0

BULLET_SPEED = 50

UPDATES_PER_FRAME = 5
MOVEMENT_SPEED = 7

SPRITE_SCALING_LASER = 1

ZOOM_AMMOUNT = 400
