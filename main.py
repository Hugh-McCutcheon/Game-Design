"""
Name: main.py
Author: Hugh McCutcheon
Description: Runs the game - code collects functions
that run the game
"""
# importing libraries/other files required to run the game
import arcade
import time
from pymunk import Vec2d
import json
import Characters

import constants
import player


# following is the main game view
class MyGame(arcade.View):
    """ Main application class. """

    def __init__(self, game_view):
        """
        Initializer, initialises all the variables
        """
        super().__init__()
        # define variables and functions used by the player
        self.game_view = game_view
        self.player_list = None
        self.player = None
        self.javlin = None
        self.display_health_list = None
        self.display_health = None
        self.crosshair = arcade.Sprite("Sprites/Player/Crosshair.png", scale=2)
        self.crosshair.center_x = 0
        self.crosshair.center_y = 0

        # define variables and functions used to store data for levels and tilemap
        self.wall_list = None
        self.item_list = None
        self.detail_list = None
        self.map_wall_list = None
        self.stationary_spawn_list = None
        self.physics_engine = None
        self.pspawn_list = None
        self.background = None
        self.interactable_list = None
        self.danger_list = None

        self.my_map = None

        self.tutorial = False
        self.key_prompt = []
        mouse_temp_hold = []

        # creating prompt sprites for the tutorial from a sprite sheet using a loop
        for i in range(2):
            texture = arcade.load_texture('Sprites/keyprompt.png', x=i*522, y=0, width=522, height=171)
            mouse_temp_hold.append(texture)
        self.key_prompt.append(mouse_temp_hold)
        mouse_temp_hold = []
        for i in range(2):
            texture = arcade.load_texture('Sprites/Mouse.png', x=i*306, y=0, width=306, height=198)
            mouse_temp_hold.append(texture)
        self.key_prompt.append(mouse_temp_hold)

        self.cur_key_texture = 0

        """Back End variables and functions that the player wont encounter"""
        # dev variables that keep track of game performance (fps) #
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None
        # variables that control the position of the camera #
        self.view_left = 0
        self.view_bottom = 0
        self.view_center = Vec2d(0, 0)
        self.x = 0
        self.y = 0
        # variables used for pathfinding AI (deprecated) #
        self.barrier_list = None
        self.path = None
        self.lastpos = 300

        self.dead_count = 0

    def setup(self):
        """Set all of the variables to default values at the start"""

        # set player variables and functions #
        arcade.set_background_color((62, 53, 70))
        self.player_list = arcade.SpriteList()
        self.player = player.PlayerCharacter()
        self.javlin = player.Javlin()
        self.display_health_list = arcade.SpriteList()
        self.display_health = player.DisplayHealth()

        self.player.center_x = constants.SCREEN_WIDTH // 2
        self.player.center_y = constants.SCREEN_HEIGHT // 2
        self.player_list.append(self.player)

        self.display_health.center_x = 0
        self.display_health.center_y = 0
        self.display_health_list.append(self.display_health)

        # set variables and functions used to store data for levels and tilemap #
        self.wall_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.detail_list = arcade.SpriteList()
        self.pspawn_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        self.load_level()
        self.player.setup()
        self.player.danger_list = self.danger_list

    def load_level(self):
        """
         The world file is read and looped through to get the name of each tile map contained within and where
         it should be located on the game board relative to the origin.
         """
        # Read the castle "world" file #
        with open('Map/Maps/Castle/Castle.world') as castle_world:  # a JSON file of all the room tile maps #
            data = json.load(castle_world)
        # looping through each tile map to get the name and translation amount (offset from the origin)
        for i in range(len(data['maps'])):
            cur_map = data['maps'][i]['fileName']
            map_x = data['maps'][i]['x']
            map_y = -data['maps'][i]['y']
            self.my_map = arcade.tilemap.read_tmx(f'Map/Maps/Castle/{cur_map}')

            """ the following section of code looks at the layers within each tile.  These need separate lists so that
            the player can interact with them separately """

            # Grab the layer of items we can't move through e.g. floor and walls, and make them solid and add them
            # to the wall list
            self.map_wall_list = arcade.tilemap.process_layer(self.my_map,
                                                              'Ground',
                                                              constants.TILE_SPRITE_SCALING,
                                                              use_spatial_hash=True)
            for wall in self.map_wall_list:
                wall.center_x += map_x
                wall.center_y += map_y  # (map_y - height_diff)

            self.wall_list.extend(self.map_wall_list)

            # Grab the layer of items we can move through. These are aesthetics like floor and wall details.  Add these
            # to the detail list
            map_detail_list = arcade.tilemap.process_layer(self.my_map,
                                                           "Detail",
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)
            for detail in map_detail_list:
                detail.center_x += map_x
                detail.center_y += map_y

            self.detail_list.extend(map_detail_list)

            # This addresses the items you need to collect in the game.  This looks at the layers of the tilemaps and
            # if the tilemap has an item like this it adds it to the item list.
            map_item_list = arcade.tilemap.process_layer(self.my_map,
                                                         'Items',
                                                         constants.TILE_SPRITE_SCALING,
                                                         use_spatial_hash=False)

            for item in map_item_list:
                item.center_x += map_x
                item.center_y += map_y

            self.item_list.extend(map_item_list)

            # this addresses player spawn points. These are placed around the map in various positions.
            # This takes the player spawn points and adds them to the spawn list.
            map_pspawn_list = arcade.tilemap.process_layer(self.my_map,
                                                           'Spawn Layer',
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)
            for node in map_pspawn_list:
                node.center_x += map_x
                node.center_y += map_y

            self.pspawn_list.extend(map_pspawn_list)

            # 'Danger' are points on the map that you need to avoid.  This code takes the danger and adds it to the
            # danger list.
            map_danger_list = arcade.tilemap.process_layer(self.my_map,
                                                           'Dangers',
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)
            for danger in map_danger_list:
                danger.center_x += map_x
                danger.center_y += map_y

            self.danger_list.extend(map_danger_list)

        # this code takes the wall list created above and adds the laws of nature to it so the player experiences
        # this in the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=constants.GRAVITY)

        # the following code makes the lists that the player uses
        # and also knowledge of the physics engine available to the player
        self.player.physics_engines.append(self.physics_engine)
        self.player.wall_list = self.wall_list
        self.player.my_map = self.my_map
        self.player.spawn_list = self.pspawn_list

    def on_key_press(self, key, modifiers):
        # detects the key inputs from the player and performs actions depending on what they pressed
        self.player.on_key_press(key)
        if key == arcade.key.ESCAPE:
            # self.window.close()
            game_view = MainMenu()

            self.window.show_view(game_view)

        if key == arcade.key.ENTER:
            self.save()

    def on_key_release(self, key, modifiers):
        """ Called whenever a key is released """
        # detects the release of a key and tells the player it has happened
        self.player.on_key_release(key)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        # detects the click of the mouse and tells the player it has happened
        self.player.on_mouse_press(button)

    def on_mouse_release(self, x, y, button, modifiers):
        """ Called whenever the mouse button is released. """
        # detects the release of the mouse and tells the player it has happened
        self.player.on_mouse_release(button)

    def on_draw(self):
        """ Draws everything that is viewed by the player eg ground, player, walls """
        arcade.start_render()
        self.frame_count += 1
        # calculates the center of the view depending on the player
        self.view_center += Vec2d(self.player.center_x - self.view_center.x,
                                  self.player.center_y - self.view_center.y) * .2
        self.crosshair.center_x = self.x + self.view_left
        self.crosshair.center_y = self.y + self.view_bottom

        # draws the wall list so that the player can view it
        self.wall_list = self.player.wall_list

        # set the camera to the correct location
        self.view_left = (self.view_center.x - constants.SCREEN_WIDTH // 2)
        self.view_left = int(self.view_left)
        self.view_bottom = (self.view_center.y - constants.SCREEN_HEIGHT // 2)
        self.view_bottom = int(self.view_bottom)

        # if the player isnt in the tutorial level then the health is displayed and camera is moved
        if not self.tutorial:
            # calculates the location of the health relative to the camera
            self.display_health.center_x = self.view_left + self.display_health.width // 2 + 10
            self.display_health.center_y = self.view_bottom+constants.SCREEN_HEIGHT-self.display_health.height//2-10

            # changes the location of the camera so the character stays in the centre.
            arcade.set_viewport(self.view_left,
                                constants.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                constants.SCREEN_HEIGHT + self.view_bottom)
        # draws the gold line to the goal depending on wether or not the player is in the tutorial
        # this line indicates the link between the player and the goal.
        if not self.tutorial and len(self.item_list) > 0:
            for item in self.item_list:
                arcade.draw_line(self.player.center_x, self.player.center_y, item.center_x, item.center_y,
                                 (247, 150, 23, 70), 5)
        elif not self.tutorial and len(self.item_list) <= 0:
            # sets the win condition for the player and activates it when all of the prerequisits are met
            arcade.draw_line(self.player.center_x, self.player.center_y, 500, 960,
                             (247, 150, 23, 70), 5)
            if self.player.center_y > 960 and not self.tutorial:
                text = Characters.gen_letter_list("You WIN!", self.view_center.x - 396/2, self.view_center.y + 150)
                print((text[0].center_x - text[0].width // 2) +
                      (text[len(text) - 1].center_x + text[len(text) - 1].width // 2))
                text.draw()
                self.player.health[0] = 10
                self.player.jump_point = (1552, 288)
                self.save()
                self.player.dead = True
        # this runs if the player is in the tutorial. It draws the gold line that is specific to the tutorial.
        elif self.tutorial:
            arcade.draw_line(self.player.center_x, self.player.center_y, 930, 830,
                             (247, 150, 23, 70), 5)

        self.player_list.draw()
        self.player.draw()
        # draws the wall list when the player is in the tutorial
        self.wall_list.draw()
        # draws the details for the map
        self.detail_list.draw()
        # draws the items and dangers so they can be viewd and avoided/collected by the player
        self.item_list.draw()
        self.danger_list.draw()
        # calculates and prints the current FPS of the game once every second
        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS:{fps:5.0f}"
            print(self.fps_message)
        # only runs if the game has been cunning for more then a second
        if self.frame_count % 60 == 0:
            # how many seconds it was since the last frame
            self.last_time = time.time()

        # this was for calculating what cell the player was in but I couldn't get it working (deprecated)
        with open('Map/Maps/Castle/Castle.world') as castle_world:
            data = json.load(castle_world)
        width = data['maps'][0]['width']
        height = data['maps'][0]['height']
        x = data['maps'][0]['x']
        y = -data['maps'][0]['y']
        p = Vec2d(self.player.center_x, self.player.center_y)
        bl = Vec2d(x, y)
        tr = Vec2d(width+x, height+y)
        if bl.x < p.x < tr.x and bl.y < p.y < tr.y:
            pass
        else:
            pass
        # deprecated section ends

        # updates the health so it displays the right percentage
        self.display_health.health = self.player.health[0]
        self.display_health.max_health = self.player.health[1]
        # handles drawing the health
        self.display_health_list.draw()
        self.display_health.draw()
        # this runs if the player dies. it is a fade to black animation then loads the last save
        if self.player.dead:
            self.dead_count += 3
            arcade.draw_rectangle_filled(self.view_center.x, self.view_center.y,
                                         constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (0, 0, 0, self.dead_count))
            if self.dead_count >= 255:
                game_view = MainMenu()
                self.window.show_view(game_view)

        # this runs if the tutorial is selected it is alost the same as the code above but has some things removed
        if self.tutorial:
            # set the background colour to blue
            arcade.set_background_color(arcade.color.SKY_BLUE)

            # if the camera is at the edge of the screen stop moving it
            if self.view_left < 0:
                self.view_left = 0
            elif self.view_left > (len(self.my_map.layers[0].layer_data[0]) * 32) - constants.SCREEN_WIDTH:
                self.view_left = (len(self.my_map.layers[0].layer_data[0])*32)-constants.SCREEN_WIDTH
            if self.view_bottom < 0:
                self.view_bottom = 0
            elif self.view_bottom > (len(self.my_map.layers[0].layer_data) * 32) - constants.SCREEN_HEIGHT:
                self.view_bottom = (len(self.my_map.layers[0].layer_data) * 32) - constants.SCREEN_HEIGHT

            # displayes the health relative to the camera
            self.display_health.center_x = self.view_left + self.display_health.width // 2 + 10
            self.display_health.center_y = self.view_bottom+constants.SCREEN_HEIGHT-self.display_health.height//2 - 10

            # sets the camera to the calculated position
            arcade.set_viewport(self.view_left,
                                constants.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                constants.SCREEN_HEIGHT + self.view_bottom)
            """ Handles the drawing and animation of the tutorial prompts"""
            # advances the animation frame of the prompt
            updates_per_frame = 10
            self.cur_key_texture += 1
            if self.cur_key_texture >= 2 * updates_per_frame:
                self.cur_key_texture = 0
            # sets the handler for the frames in the prompt animation
            key_prompt = self.key_prompt[0][self.cur_key_texture // updates_per_frame]
            mouse_prompt = self.key_prompt[1][self.cur_key_texture // updates_per_frame]
            key_prompt_y = (self.view_bottom + constants.SCREEN_HEIGHT//2) + constants.SCREEN_HEIGHT//4
            text_prompt_y = (self.view_bottom + constants.SCREEN_HEIGHT//2) - constants.SCREEN_HEIGHT // 4
            prompt_x = self.view_left + constants.SCREEN_WIDTH//2
            """
            the following if else line showes worded promps instructing the player on what to do when
            they are at different sections of the level
            """
            # instructs the player on how to move
            if self.player.center_x < 550:
                arcade.draw_scaled_texture_rectangle(prompt_x,
                                                     key_prompt_y,
                                                     key_prompt)
                text = Characters.gen_letter_list("W, A, S, and D to move.",
                                                  prompt_x-474,
                                                  text_prompt_y)

                text.extend(Characters.gen_letter_list("Space or W to jump.",
                                                       prompt_x-424,
                                                       text_prompt_y-88))
                text.extend(Characters.gen_letter_list("Follow the gold line.",
                                                       prompt_x - 425,
                                                       text_prompt_y - 176))

                text.draw()
            # tells the player not do fall and die
            elif self.player.center_x < 1400 and self.player.center_y < 600:
                text = Characters.gen_letter_list("Don't fall onto dangerous obstacles.",
                                                  prompt_x - 767,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("Doing so will make you lose health!",
                                                       prompt_x - 732,
                                                       text_prompt_y - 88))
                text.extend(Characters.gen_letter_list("Press ENTER to set a checkpoint",
                                                       prompt_x - 703,
                                                       text_prompt_y - 176))

                text.draw()
            # instructs the player on how to throw the javalin
            elif self.player.center_x < 2000 and self.player.center_y < 670:
                arcade.draw_scaled_texture_rectangle(prompt_x,
                                                     key_prompt_y,
                                                     mouse_prompt)
                text = Characters.gen_letter_list("RMB to bring the javlin to you.",
                                                  prompt_x - 670,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("LMB to through the javlin.",
                                                       prompt_x - 576,
                                                       text_prompt_y - 88))
                text.extend(Characters.gen_letter_list("You can jump onto the javlin!",
                                                       prompt_x - 627,
                                                       text_prompt_y - 176))

                text.draw()
                # tells the player to go to the exit and how to return to the main menu
            else:
                text = Characters.gen_letter_list("You finished the tutorial.",
                                                  prompt_x - 549,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("Press escape to play.",
                                                       prompt_x - 455,
                                                       text_prompt_y - 88))

                text.draw()
        # draws the crosshair (customer mouse cursor)
        self.crosshair.draw()

    def on_update(self, delta_time: float):
        """ Updates the Game logic """
        # updates all player valiables and functions if the player isnt dead
        if not self.player.dead:
            self.player.delta_time = delta_time
            self.player.physics_engines[0].update()
            self.display_health.update()
            self.player.update()
            if arcade.check_for_collision_with_list(self.player, self.danger_list):
                self.player.hurt = True
            self.player.mouseX = self.x + self.view_left
            self.player.mouseY = self.y + self.view_bottom
        # updates the player regardless of if they are dead or not
        self.player_list.update()
        self.player_list.update_animation()
        # detects when the payer is colliding with an item and pickes it up
        for item in self.item_list:
            if arcade.check_for_collision(self.player, item):
                self.item_list.remove(item)

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """ Called whenever the mouse moves. """
        self.x = x
        self.y = y

    def save(self):
        """ added the save data to a JSON file """
        with open("Saves/Save1.json", "r") as jsonFile:
            savedata = json.load(jsonFile)
        # """Location and level information"""
        savedata["location"]["load_position"] = self.player.checkpoint_num
        savedata["location"]["jump_point"] = self.player.jump_point

        # """Equipment and gear information"""
        savedata["equipment"]["equipped"] = self.player.equipped_item

        # """Health information"""
        savedata["health"]["current_health"] = self.player.health[0]

        with open("Saves/Save1.json", "w") as jsonFile:
            json.dump(savedata, jsonFile, indent=4)

    def load_save(self):
        """ Runs the setups after a save load """
        self.setup()
        self.player.setup()

    def run_tutorial(self):
        """ Code that runs when the player runs the tutorial """
        self.setup()
        arcade.set_background_color((62, 53, 70))
        self.wall_list = arcade.SpriteList()
        self.pspawn_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        # Read the tutorial tiled file and handles creating the level #
        self.my_map = arcade.tilemap.read_tmx(f'Map/Maps/Garden/tutorial.tmx')

        # Grab the layer of items we can't move through e.g. floor and walls, and make them solid and add them
        # to the wall list
        self.map_wall_list = arcade.tilemap.process_layer(self.my_map,
                                                          'Ground',
                                                          constants.TILE_SPRITE_SCALING,
                                                          use_spatial_hash=True)

        self.wall_list.extend(self.map_wall_list)
        # Grab the layer of items we can move through. These are aesthetics like floor and wall details.  Add these
        # to the detail list
        self.detail_list = arcade.SpriteList()
        map_detail_list = arcade.tilemap.process_layer(self.my_map,
                                                       "Detail",
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)

        self.detail_list.extend(map_detail_list)
        # this addresses player spawn points. These are placed around the map in various positions.
        # This takes the player spawn points and adds them to the spawn list.
        map_pspawn_list = arcade.tilemap.process_layer(self.my_map,
                                                       'Spawn Layer',
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)

        self.pspawn_list.extend(map_pspawn_list)
        # 'Danger' are points on the map that you need to avoid.  This code takes the danger and adds it to the
        # danger list.
        map_danger_list = arcade.tilemap.process_layer(self.my_map,
                                                       'Dangers',
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)

        self.danger_list.extend(map_danger_list)
        # this code takes the wall list created above and adds the laws of nature to it so the player experiences
        # this in the game
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=constants.GRAVITY)
        # the following code makes the lists that the player uses
        # and also knowledge of the physics engine available to the player
        self.player.physics_engines = (self.physics_engine, 1)
        self.player.wall_list = self.wall_list
        self.player.my_map = self.my_map
        self.player.spawn_list = self.pspawn_list
        self.player.position = self.pspawn_list[0].position


class MainMenu(arcade.View):
    """ The class of the main menu """
    def __init__(self):
        super().__init__()

    def on_show(self):
        """ Run when the player is first shown the main menu """
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, constants.SCREEN_WIDTH, 0, constants.SCREEN_HEIGHT)

    def on_draw(self):
        """ Draws everything seen by the player on the main menu"""
        arcade.start_render()

        arcade.draw_scaled_texture_rectangle(constants.SCREEN_WIDTH // 2,
                                             constants.SCREEN_HEIGHT // 2,
                                             arcade.load_texture('Sprites/Main Menu.png'),
                                             constants.SCREEN_WIDTH / 3240)

        text = (Characters.gen_letter_list("LMB: Load Game  RMB: Play Tutorial",
                                           constants.SCREEN_WIDTH//2 - 760, constants.SCREEN_HEIGHT//2-88))
        text.draw()

    def on_key_press(self, key: int, modifiers: int):
        """ Detects when the player presses escape """
        if key == arcade.key.ESCAPE:
            self.window.close()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Detects when the player clicks the mouse button """
        if button == arcade.MOUSE_BUTTON_LEFT:  # loads the main game

            game_view = MyGame(self)
            game_view.setup()
            game_view.tutorial = False
            self.window.show_view(game_view)
        elif button == arcade.MOUSE_BUTTON_RIGHT:  # loads the tutorial
            game_view = MyGame(self)
            # game_view.setup()
            game_view.run_tutorial()
            game_view.tutorial = True
            self.window.show_view(game_view)


def main():
    """ Runs the game """
    window = arcade.Window(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE, fullscreen=True)
    window.set_mouse_visible(False)
    window.center_window()
    start_view = MainMenu()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
