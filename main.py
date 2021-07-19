import arcade
import time
import math
from pymunk import Vec2d
import json
import Characters
import IK3

import constants
import player
import enemy


class MyGame(arcade.View):
    """ Main application class. """

    def __init__(self, game_view):
        """
        Initializer
        """
        super().__init__()
        """Enemy and Player Things"""
        self.game_view = game_view
        self.player_list = None
        self.player = None
        self.javlin = None
        self.display_health_list = None
        self.display_health = None

        self.enemy_list = None
        self.enemy = None

        """Tilemap and Level Things"""
        self.wall_list = None
        self.map_wall_list = None
        self.stationary_spawn_list = None
        self.physics_engine = None
        self.physics_engine_enemy = None
        self.pspawn_list = None
        self.background = None
        self.interactable_list = None
        self.danger_list = None

        self.my_map = None

        self.tutorial = False
        self.key_prompt = []
        mouse_temp_hold = []
        for i in range(2):
            texture = arcade.load_texture('Sprites/keyprompt.png', x=i*522, y=0, width=522, height=171)
            mouse_temp_hold.append(texture)
        self.key_prompt.append(mouse_temp_hold)
        mouse_temp_hold = []
        for i in range(2):
            texture = arcade.load_texture('Sprites/Mouse.png', x=i*306, y=0, width=306, height=198)
            mouse_temp_hold.append(texture)
        self.key_prompt.append(mouse_temp_hold)
        print(self.key_prompt)

        self.cur_key_texture = 0
        """Back End Things"""
        # Performance stuff #
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None
        # Camera stuff #
        self.view_left = 0
        self.view_bottom = 0
        self.view_center = Vec2d(0, 0)
        self.x = 0
        self.y = 0
        # Pathfinding stuff #
        self.barrier_list = None
        self.path = None
        self.lastpos = 300

        self.dead_count = 0

    def setup(self):
        """Set all of the variables at the start"""

        """player things"""
        arcade.set_background_color(arcade.color.BLACK)
        #  arcade.play_sound(arcade.load_sound('Sounds/Music Test.wav', True), 0.5, 0, True)
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

        """Enemy things"""
        self.enemy_list = arcade.SpriteList()
        self.enemy = enemy.Enemy()
        self.enemy.center_x = constants.SCREEN_WIDTH // 2
        self.enemy.center_y = constants.SCREEN_HEIGHT // 2
        self.enemy_list.append(self.enemy)

        """Map Things"""
        self.wall_list = arcade.SpriteList()
        self.pspawn_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        self.load_level()
        self.player.setup()
        self.player.danger_list = self.danger_list

    def load_level(self):
        # Read in the tiled map
        with open('Map/Maps/Castle/Castle.world') as castle_world:
            data = json.load(castle_world)

        for i in range(len(data['maps'])):
            cur_map = data['maps'][i]['fileName']
            map_x = data['maps'][i]['x']
            map_y = -data['maps'][i]['y']
            height_diff = data['maps'][i]['height'] - data['maps'][0]['height']
            print(height_diff)
            self.my_map = arcade.tilemap.read_tmx(f'Map/Maps/Castle/{cur_map}')
            # --- Walls ---

            # Grab the layer of items we can't move through

            self.map_wall_list = arcade.tilemap.process_layer(self.my_map,
                                                              'Ground',
                                                              constants.TILE_SPRITE_SCALING,
                                                              use_spatial_hash=True)
            for wall in self.map_wall_list:
                wall.center_x += map_x
                wall.center_y += map_y  # (map_y - height_diff)

            self.wall_list.extend(self.map_wall_list)

            map_pspawn_list = arcade.tilemap.process_layer(self.my_map,
                                                           'Spawn Layer',
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)
            for node in map_pspawn_list:
                node.center_x += map_x
                node.center_y += map_y

            self.pspawn_list.extend(map_pspawn_list)
            print(cur_map)
            map_danger_list = arcade.tilemap.process_layer(self.my_map,
                                                           'Dangers',
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)
            for danger in map_danger_list:
                danger.center_x += map_x
                danger.center_y += map_y

            self.danger_list.extend(map_danger_list)
            # self.wall_list.extend(self.danger_list)
            """self.background = arcade.tilemap.process_layer(self.my_map,
                                                           'Background',
                                                           constants.TILE_SPRITE_SCALING,
                                                           use_spatial_hash=False)"""
            """self.interactable_list = arcade.tilemap.process_layer(self.my_map,
                                                                  'Interactable',
                                                                  constants.TILE_SPRITE_SCALING,
                                                                  use_spatial_hash=False)"""
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=constants.GRAVITY)

        self.physics_engine_enemy = arcade.PhysicsEnginePlatformer(self.enemy,
                                                                   self.wall_list,
                                                                   gravity_constant=constants.GRAVITY)

        self.enemy.level_list = self.wall_list
        self.player.physics_engines.append(self.physics_engine)
        self.player.wall_list = self.wall_list
        self.player.my_map = self.my_map
        self.player.spawn_list = self.pspawn_list
        self.enemy.physics_engines.append(self.physics_engine_enemy)

    def on_key_press(self, key, modifiers):
        self.player.on_key_press(key)
        self.enemy.on_key_press(key)
        if 49 <= key <= (48 + len(self.pspawn_list)):
            self.player.position = self.pspawn_list[key - 49].position
            self.player.checkpoint = self.pspawn_list[key - 49]
            self.player.checkpoint_num = key - 49
            self.enemy.position = self.pspawn_list[key - 49].position
        if key == arcade.key.ESCAPE:
            # self.window.close()
            game_view = MainMenu()

            self.window.show_view(game_view)
        elif key == arcade.key.LSHIFT:
            self.javlin.position = self.player.position

        if key == arcade.key.ENTER:
            self.save()

        if key == arcade.key.UP:
            self.player.health[0] += 1

    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key)
        self.enemy.on_key_release(key)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        self.player.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.player.on_mouse_release(x, y, button, modifiers)

    def on_draw(self):
        arcade.start_render()
        self.frame_count += 1
        self.view_center += Vec2d(self.player.center_x - self.view_center.x,
                                  self.player.center_y - self.view_center.y) * .2

        self.wall_list = self.player.wall_list
        self.view_left = (self.view_center.x - constants.SCREEN_WIDTH // 2)
        self.view_left = int(self.view_left)
        self.view_bottom = (self.view_center.y - constants.SCREEN_HEIGHT // 2)
        self.view_bottom = int(self.view_bottom)
        if not self.tutorial:
            self.display_health.center_x = self.view_left + self.display_health.width // 2 + 10
            self.display_health.center_y = self.view_bottom+constants.SCREEN_HEIGHT-self.display_health.height//2-10

            """if self.view_left < 0:
                pass
                #self.view_left = 0
            elif self.view_left > (len(self.my_map.layers[0].layer_data[0]) * 64) - constants.SCREEN_WIDTH:
                pass
                #self.view_left = (len(self.my_map.layers[0].layer_data[0])*64)-constants.SCREEN_WIDTH
            if self.view_bottom < 0:
                pass
                #self.view_bottom = 0
            elif self.view_bottom > (len(self.my_map.layers[0].layer_data) * 64) - constants.SCREEN_HEIGHT:
                pass
                #self.view_bottom = (len(self.my_map.layers[0].layer_data) * 64) - constants.SCREEN_HEIGHT"""

            arcade.set_viewport(self.view_left,
                                constants.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                constants.SCREEN_HEIGHT + self.view_bottom)
        # self.background.draw()
        self.player_list.draw()
        self.player.draw()
        self.enemy_list.draw()
        self.wall_list.draw()
        self.danger_list.draw()
        # len(self.interactable_list)
        # self.interactable_list.draw()
        # self.enemy_list.draw()
        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS:{fps:5.0f}"
            # take this out later
            print(self.fps_message)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        text1 = Characters.gen_letter_list(str(self.fps_message), self.view_left,
                                           self.view_bottom + constants.SCREEN_HEIGHT - 50)
        text1.draw()

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
        self.display_health.health = self.player.health[0]
        self.display_health.max_health = self.player.health[1]
        arcade.draw_rectangle_outline(x + width / 2, y + height / 2, width, height, (255, 0, 0), 5)
        self.display_health_list.draw()
        self.display_health.draw()
        if self.player.dead:
            self.dead_count += 3
            print(self.dead_count)
            arcade.draw_rectangle_filled(self.view_center.x, self.view_center.y,
                                         constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (0, 0, 0, self.dead_count))
            if self.dead_count >= 255:
                game_view = MainMenu()
                self.window.show_view(game_view)

        if self.tutorial:
            if self.view_left < 0:
                self.view_left = 0
            elif self.view_left > (len(self.my_map.layers[0].layer_data[0]) * 32) - constants.SCREEN_WIDTH:
                self.view_left = (len(self.my_map.layers[0].layer_data[0])*32)-constants.SCREEN_WIDTH
            if self.view_bottom < 0:
                self.view_bottom = 0
            elif self.view_bottom > (len(self.my_map.layers[0].layer_data) * 32) - constants.SCREEN_HEIGHT:
                self.view_bottom = (len(self.my_map.layers[0].layer_data) * 32) - constants.SCREEN_HEIGHT

            self.display_health.center_x = self.view_left + self.display_health.width // 2 + 10
            self.display_health.center_y = self.view_bottom+constants.SCREEN_HEIGHT-self.display_health.height//2 - 10

            arcade.set_viewport(self.view_left,
                                constants.SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                constants.SCREEN_HEIGHT + self.view_bottom)
            UPDATES_PER_FRAME = 10
            self.cur_key_texture += 1
            if self.cur_key_texture >= 2 * UPDATES_PER_FRAME:
                self.cur_key_texture = 0
            key_prompt = self.key_prompt[0][self.cur_key_texture // UPDATES_PER_FRAME]
            mouse_prompt = self.key_prompt[1][self.cur_key_texture // UPDATES_PER_FRAME]
            key_prompt_y = (self.view_bottom + constants.SCREEN_HEIGHT//2) + constants.SCREEN_HEIGHT//4
            text_prompt_y = (self.view_bottom + constants.SCREEN_HEIGHT//2) - constants.SCREEN_HEIGHT // 4
            prompt_x = self.view_left + constants.SCREEN_WIDTH//2
            if self.player.center_x < 550:
                arcade.draw_scaled_texture_rectangle(prompt_x,
                                                     key_prompt_y,
                                                     key_prompt)
                text = Characters.gen_letter_list("A, S, and D to move.",
                                                  prompt_x-411,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("Space or W to jump.",
                                                       prompt_x-424,
                                                       text_prompt_y-88))
                text.extend(Characters.gen_letter_list("Hold Space or W to jump higher.",
                                                       prompt_x-679,
                                                       text_prompt_y - 176))
                text.draw()
            elif self.player.center_x < 1400 and self.player.center_y < 600:
                text = Characters.gen_letter_list("Don't fall onto dangerous obstacles.",
                                                  prompt_x - 767,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("Doing so will make you lose health!",
                                                       prompt_x - 732,
                                                       text_prompt_y - 88))
                text.extend(Characters.gen_letter_list("Falling in here will hurt you!",
                                                       prompt_x - 611,
                                                       text_prompt_y - 176))
                text.draw()
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
            else:
                text = Characters.gen_letter_list("You finished the tutorial.",
                                                  prompt_x - 549,
                                                  text_prompt_y)
                text.extend(Characters.gen_letter_list("Head to the exit to play.",
                                                       prompt_x - 532,
                                                       text_prompt_y - 88))
                text.draw()

                # tell player to go to exit
    def on_update(self, delta_time: float):
        """ Game logic """
        if not self.player.dead:
            self.player.delta_time = delta_time
            self.player.physics_engines[0].update()
            self.display_health.update()
            self.physics_engine_enemy.update()
            self.player.update()
            if arcade.check_for_collision_with_list(self.player, self.danger_list):
                self.player.hurt = True
            # self.javlin.update()
            self.player.mouseX = self.x + self.view_left
            self.player.mouseY = self.y + self.view_bottom
            """playertestposx = (math.floor((self.player.center_x - 32) / 32))
            playertestposy = (math.floor(self.player.center_y / 32))

            if self.my_map.layers[2].layer_data[99 - playertestposy][playertestposx] == 0:
                enemypos = (int(self.enemy.center_x), int(self.enemy.center_y + 32))
                playerpos = (int(self.player.center_x), int(self.player.center_y + 32))
                self.path = arcade.astar_calculate_path(enemypos,
                                                        playerpos,
                                                        self.barrier_list,
                                                        diagonal_movement=True)
            else:
                enemypos = (int(self.enemy.center_x), int(self.enemy.center_y + 32))
                playerpos = (int(self.player.center_x + 32), int(self.player.center_y + 32))
                self.path = arcade.astar_calculate_path(enemypos,
                                                        playerpos,
                                                        self.barrier_list,
                                                        diagonal_movement=True)
            self.enemy.path = self.pa   th"""

        self.enemy_list.update()
        self.player_list.update()
        self.player_list.update_animation()

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """Called whenever the mouse moves. """

        self.x = x
        self.y = y

    def save(self, n: int = 1):
        with open("Saves/Save1.json", "r") as jsonFile:
            savedata = json.load(jsonFile)
        # """Location and level information"""
        savedata["location"]["load_position"] = self.player.checkpoint_num

        # """Equipment and gear information"""
        savedata["equipment"]["equipped"] = self.player.equipped_item

        # """Health information"""
        savedata["health"]["current_health"] = self.player.health[0]

        with open("Saves/Save1.json", "w") as jsonFile:
            json.dump(savedata, jsonFile, indent=4)

    def load_save(self):
        self.setup()
        self.player.setup()

    def run_tutorial(self):
        self.setup()
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.wall_list = arcade.SpriteList()
        self.pspawn_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        # self.player.setup()
        # Read in the tiled map
        self.my_map = arcade.tilemap.read_tmx(f'Map/Maps/Garden/tutorial.tmx')
        # --- Walls ---

        # Grab the layer of items we can't move through

        self.map_wall_list = arcade.tilemap.process_layer(self.my_map,
                                                          'Ground',
                                                          constants.TILE_SPRITE_SCALING,
                                                          use_spatial_hash=True)

        self.wall_list.extend(self.map_wall_list)

        map_pspawn_list = arcade.tilemap.process_layer(self.my_map,
                                                       'Spawn Layer',
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)

        self.pspawn_list.extend(map_pspawn_list)
        map_danger_list = arcade.tilemap.process_layer(self.my_map,
                                                       'Dangers',
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)

        self.danger_list.extend(map_danger_list)
        # self.wall_list.extend(self.danger_list)
        """self.background = arcade.tilemap.process_layer(self.my_map,
                                                       'Background',
                                                       constants.TILE_SPRITE_SCALING,
                                                       use_spatial_hash=False)"""
        """self.interactable_list = arcade.tilemap.process_layer(self.my_map,
                                                              'Interactable',
                                                              constants.TILE_SPRITE_SCALING,
                                                              use_spatial_hash=False)"""
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.wall_list,
                                                             gravity_constant=constants.GRAVITY)

        self.physics_engine_enemy = arcade.PhysicsEnginePlatformer(self.enemy,
                                                                   self.wall_list,
                                                                   gravity_constant=constants.GRAVITY)

        self.enemy.level_list = self.wall_list
        # self.player.physics_engines.append(self.physics_engine)
        self.player.physics_engines = (self.physics_engine, 1)
        self.player.wall_list = self.wall_list
        self.player.my_map = self.my_map
        self.player.spawn_list = self.pspawn_list
        self.enemy.physics_engines.append(self.physics_engine_enemy)
        self.player.position = self.pspawn_list[0].position


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, constants.SCREEN_WIDTH, 0, constants.SCREEN_HEIGHT)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_scaled_texture_rectangle(constants.SCREEN_WIDTH // 2,
                                             constants.SCREEN_HEIGHT // 2,
                                             arcade.load_texture('Sprites/Main Menu.png'),
                                             constants.SCREEN_WIDTH / 3240)
        text = Characters.gen_letter_list("Kinarough",
                                          constants.SCREEN_WIDTH//2 - 218, constants.SCREEN_HEIGHT//2)
        text.extend(Characters.gen_letter_list("LMB: Load Game  RMB: Play Tutorial",
                                               constants.SCREEN_WIDTH//2 - 760, constants.SCREEN_HEIGHT//2-88))
        text.draw()

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.window.close()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:

            game_view = MyGame(self)
            game_view.setup()
            game_view.tutorial = False
            self.window.show_view(game_view)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            game_view = MyGame(self)
            # game_view.setup()
            game_view.run_tutorial()
            game_view.tutorial = True
            self.window.show_view(game_view)


def main():
    window = arcade.Window(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE)
    window.set_mouse_visible(True)
    window.center_window()
    start_view = MainMenu()
    window.show_view(start_view)
    arcade.run()

    """window = MyGame()
    window.setup()
    arcade.run()"""


if __name__ == "__main__":
    main()
