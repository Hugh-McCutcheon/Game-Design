import arcade
import time
import math
from pymunk import Vec2d
import json
import Characters

import constants
import player
import enemy

# I know this is bad but I couldn't think of another way.
constants.SCREEN_WIDTH = arcade.window_commands.get_display_size()[0]
constants.SCREEN_HEIGHT = arcade.window_commands.get_display_size()[1]


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE, fullscreen=False)
        """Enemy and Player Things"""
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

        self.center_window()


        """Map Things"""
        self.wall_list = arcade.SpriteList()
        self.pspawn_list = arcade.SpriteList()
        self.danger_list = arcade.SpriteList()
        self.load_level()
        #self.player.position = self.pspawn_list[0].position
        self.player.setup()
        self.player.danger_list = self.danger_list

        """pathfinding"""
        grid_size = 32

        # Calculate the playing field size. We can't generate paths outside of
        # this.
        playing_field_left_boundary = 0
        playing_field_right_boundary = 3200
        playing_field_top_boundary = 3200
        playing_field_bottom_boundary = 0

        self.barrier_list = arcade.AStarBarrierList(self.enemy,
                                                    self.wall_list,
                                                    grid_size,
                                                    playing_field_left_boundary,
                                                    playing_field_right_boundary,
                                                    playing_field_bottom_boundary,
                                                    playing_field_top_boundary)
        self.enemy.barrier_list = self.barrier_list

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
                wall.center_y += map_y #(map_y - height_diff)

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
            #self.wall_list.extend(self.danger_list)
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
            self.close()
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
        self.display_health.center_x = self.view_left + self.display_health.width // 2 + 10
        self.display_health.center_y = self.view_bottom + constants.SCREEN_HEIGHT - self.display_health.height // 2 - 10

        if self.view_left < 0:
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
            #self.view_bottom = (len(self.my_map.layers[0].layer_data) * 64) - constants.SCREEN_HEIGHT

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

        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.RED, 5)

        text1 = Characters.gen_letter_list(str(self.fps_message), self.view_left,
                                           self.view_bottom + constants.SCREEN_HEIGHT - 50)
        text1.draw()

        Characters.gen_letter_list(str(f'health:{self.player.health[0]}/{self.player.health[1]}'),
                                   self.view_left, self.view_bottom + constants.SCREEN_HEIGHT - 120).draw()


        with open('Map/Maps/Castle/Castle.world') as castle_world:
            data = json.load(castle_world)
        width = data['maps'][0]['width']
        height = data['maps'][0]['height']
        x = data['maps'][0]['x']
        y = -data['maps'][0]['y']
        p = Vec2d(self.player.center_x, self.player.center_y)
        bl = Vec2d(x, y)
        tr = Vec2d(width+x, height+y)
        if p.x > bl.x and p.x < tr.x and p.y > bl.y and p.y < tr.y:
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
                #self.load_save()
                #self.player.dead = False
                print('done')





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
            playertestposx = (math.floor((self.player.center_x - 32) / 32))
            playertestposy = (math.floor(self.player.center_y / 32))

            """if self.my_map.layers[2].layer_data[99 - playertestposy][playertestposx] == 0:
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


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
