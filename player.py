"""
Name: player.py
Author: Hugh McCutcheon
Description: holdes all of the player variables and functions for the player
"""
# importing libraries/other files required to run the game
import arcade
import IK3
import constants
import math
from pymunk import Vec2d
import json

ui = arcade.Sprite('Sprites/UI/HUD test.png')


# following is the player code it contains all of the variables and functions for the player
class PlayerCharacter(arcade.Sprite):
    """ The player class. """
    def __init__(self):
        super().__init__()
        # define variables and functions used by the player
        self.FACING = 0
        self.cur_texture = 0
        self.A = False
        self.D = False
        self.mouseX = 0
        self.mouseY = 0
        self.level = 1
        self.wall_list = None
        self.texture = arcade.load_texture('Sprites/Player/limbs/Outline Temp.png')
        self.scale = constants.PLAYER_SCALING
        self.space_held = False
        self.my_map = None
        self.spawn_list = None

        # the limbs variables - these set the locations of the limbs on the avatar
        self.right_foot = Vec2d(self.center_x, self.center_y - 32)
        self.right_leg = [0, 1, 2]
        self.left_foot = Vec2d(self.center_x, self.center_y - 32)
        self.left_leg = [0, 1, 2]
        self.right_arm = [0, 1, 2]
        self.left_arm = [0, 1, 2]

        self.count = 1

        self.startx = None
        self.starty = None
        self.endx = None
        self.endy = None
        self.X = None
        self.Y = None
        self.move = False
        self.startxl = None
        self.startyl = None
        self.endxl = None
        self.endyl = None
        self.Xl = None
        self.Yl = None
        self.movel = False
        self.idle = False
        self.airborne = False
        # end of animations/inverse kinamatics variables
        self.delta_time = 1/60

        #  javlin variables - the player throws this.
        self.javlin = Javlin()
        self.javlin_hitbox = Javlin().hit_point
        self.L = False
        self.R = False
        self.return_jav = False
        self.JTX = None
        self.JTY = None
        self.JSX = None
        self.JSY = None
        self.throw = False
        self.curve = None
        self.T = 0
        self.jump_point = (1552, 288)

        #  set/define other player variables
        self.dead = False
        self.hurt = False
        self.danger_list = arcade.SpriteList()
        self.checkpoint = None
        self.checkpoint_num = 0
        self.equipped_item = 'none'
        with open('equipment_data.json') as equipmentfile:
            self.equipmentjson = json.load(equipmentfile)
            self.health = [self.equipmentjson['none'].get('max_health', 3),
                           self.equipmentjson['none'].get('max_health', 3)]

    def setup(self):
        """Set all of the variables to default values at the start"""
        # opens the save files and sets all of the values to the saved values
        with open('Saves/Save1.json') as savefile:
            savejson = json.load(savefile)

        self.position = savejson['location']['jump_point']
        self.checkpoint = self.spawn_list[savejson['location']['load_position']]
        with open('equipment_data.json') as equipmentfile:
            self.equipmentjson = json.load(equipmentfile)
        self.health = [savejson['health'].get('current_health', 10),
                       self.equipmentjson[savejson['equipment']['equipped']].get('max_health', 10)]

    def on_key_press(self, key: int):
        """ Detects when the player presses a key """
        # detects when the user presses jump and makes the player jump
        if key == arcade.key.SPACE or key == arcade.key.W:
            if self.physics_engines[self.level - 1].can_jump():
                self.change_y = constants.JUMP_SPEED
                self.space_held = True
        # makes the player walk left
        elif key == arcade.key.A:
            self.A = True
        # makes the player walk right
        elif key == arcade.key.D:
            self.D = True
        # if the player is on the ground and presses enter the game is saved
        if key == arcade.key.ENTER and self.physics_engines[self.level - 1].can_jump():
            self.jump_point = (self.center_x, self.center_y)

    def on_key_release(self, key: int):
        """ Detects when the player releases a key """
        # detects when the player releases the jump key and cuts the players jump short
        if key == arcade.key.SPACE or key == arcade.key.W:
            self.space_held = False
            if self.change_y > 0:
                self.change_y *= constants.CUT_JUMP_HEIGHT
        # stops moving the player to the left
        elif key == arcade.key.A:
            self.A = False
        # stops moving the player to the right
        elif key == arcade.key.D:
            self.D = False

    def on_mouse_press(self, button):
        """ Called whenever the mouse button is clicked. """
        # throughts the javalin
        if button == arcade.MOUSE_BUTTON_LEFT and self.R:
            self.L = True
            self.R = False
            self.JSX = self.javlin.center_x
            self.JSY = self.javlin.center_y
            self.JTX = self.mouseX
            self.JTY = self.mouseY
            self.throw = True
            arcade.play_sound(arcade.load_sound('Sounds/Throw.m4a', True), 0.5, 0)
        # returned the javalin to the player
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.T = 0
            # if the javalin is stuck in a wall it playes a sound when returned
            if self.javlin in self.wall_list:
                self.wall_list.remove(self.javlin)
                arcade.play_sound(arcade.load_sound('Sounds/Retrieve.m4a', True), 0.5, 0)

            self.return_jav = True
            self.throw = False

    def on_mouse_release(self, button):
        """ Called whenever the mouse button is clicked. """
        # releases the left mouse button
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.L = False

    def limbs(self):
        """ Calculates the position of the arms and legs. using inverse kinamatics"""
        facing = ['left', 'right']
        # calles the IK solver to determan the joint position of the legs
        self.right_leg = IK3.IK_solverR(Vec2d(self.center_x, self.center_y +
                                              ((self.right_foot.y - self.left_foot.y)/5)-7),
                                        self.right_foot, 31, 31, facing[self.FACING])
        self.left_leg = IK3.IK_solverR(Vec2d(self.center_x, self.center_y +
                                             ((self.right_foot.y - self.left_foot.y)/5)-7),
                                       self.left_foot, 31, 31, facing[self.FACING])
        # does the same as the code above but for the arms and also joins the arms to the javalin.
        facing = ['right', 'left']
        angle = ((math.atan2((self.mouseY-self.javlin.center_y), (self.mouseX - self.javlin.center_x)))+(math.pi/2))
        x = self.javlin.center_x+(32*math.sin(-angle))
        y = self.javlin.center_y+(32*math.cos(-angle))
        self.right_arm = IK3.IK_solverR(Vec2d(self.center_x, self.center_y+30),
                                        Vec2d(x, y), 28, 28, facing[self.FACING])
        x = self.javlin.center_x + (32 * math.sin(-angle-math.pi))
        y = self.javlin.center_y + (32 * math.cos(-angle-math.pi))
        self.left_arm = IK3.IK_solverR(Vec2d(self.center_x, self.center_y + 30), Vec2d(x, y), 28, 28,
                                       facing[self.FACING])

    def draw(self):
        """ Draws the things relating to the player """
        global ui
        facing = {
            0: True,
            1: False
        }
        grey = arcade.color.BATTLESHIP_GREY
        darkbrown = arcade.color.DARK_BROWN
        # the following errors are nesicary for the game to run and I can't figure out how to make them not appear
        arcade.draw_line_strip((self.right_leg[0], self.right_leg[1]), grey, 6 * 2)
        arcade.draw_line_strip((self.right_leg[1], self.right_leg[2]), darkbrown, 4 * 2)

        arcade.draw_line_strip((self.left_leg[0], self.left_leg[1]), grey, 6 * 2)
        arcade.draw_line_strip((self.left_leg[1], self.left_leg[2]), darkbrown, 4 * 2)

        arcade.draw_line_strip(self.right_arm, grey, 8)
        arcade.draw_scaled_texture_rectangle(self.center_x, self.center_y+((self.right_foot.y - self.left_foot.y)/5),
                                             arcade.load_texture("Sprites/Player/limbs/player visual.png",
                                                                 mirrored=facing[self.FACING]))
        self.javlin.draw()
        arcade.draw_line_strip(self.left_arm, grey, 8)

    def update(self):
        """ Updates the player related things """
        # Add some friction (depricated)
        if self.change_x > constants.FRICTION:
            self.change_x -= constants.FRICTION
        elif self.change_x < -constants.FRICTION:
            self.change_x += constants.FRICTION
        else:
            self.change_x = 0

        # Apply acceleration based on the keys pressed
        if self.A and not self.D:
            self.change_x += -constants.ACCELERATION_RATE
            self.change_x *= math.pow(1 - constants.HORIZONTAL_DAMPING, self.delta_time * 10)
        elif self.D and not self.A:
            self.change_x += constants.ACCELERATION_RATE
            self.change_x *= math.pow(1 - constants.HORIZONTAL_DAMPING, self.delta_time * 10)
        elif not self.D and not self.A and abs(self.change_x) > 1:
            self.change_x *= math.pow(1 - constants.HORIZONTAL_DAMPING_STOPPING, self.delta_time * 10)
        elif self.D and self.A:
            pass
        else:
            self.change_x = 0

        n = 64
        # handles the position of the feet by moving them forward when they get to a certan point
        if self.right_foot.x < self.center_x - n:  # right foot facing right
            self.move = True
            self.startx = self.right_foot.x
            self.starty = self.right_foot.y
            self.endx = self.center_x + n
            self.endy = self.center_y-64
            self.X = self.startx
            self.Y = self.starty
        elif self.right_foot.x > self.center_x + n:  # right foot facing left
            self.move = True
            self.startx = self.right_foot.x
            self.starty = self.right_foot.y
            self.endx = self.center_x - n
            self.endy = self.center_y - 64
            self.X = self.startx
            self.Y = self.starty
        if self.left_foot.x < self.center_x - n:  # left foot facing right
            self.movel = True
            self.startxl = self.left_foot.x
            self.startyl = self.left_foot.y
            self.endxl = self.center_x + n
            self.endyl = self.center_y-64
            self.Xl = self.startxl
            self.Yl = self.startyl
        elif self.left_foot.x > self.center_x + n:  # left foot facing left
            self.movel = True
            self.startxl = self.left_foot.x
            self.startyl = self.left_foot.y
            self.endxl = self.center_x - n
            self.endyl = self.center_y - 64
            self.Xl = self.startxl
            self.Yl = self.startyl
        if self.change_x == 0 and self.change_y == 0:  # return to idle position when there is no movement
            self.move = False
            self.movel = False
            self.right_foot = Vec2d(self.center_x+32, self.center_y-64)
            self.left_foot = Vec2d(self.center_x-32, self.center_y-64)
        if not self.physics_engines[0].can_jump():  # detects when the player is jumping or falling and puts legs
            # in appropriate position
            self.move = False
            self.movel = False
            self.airborne = True
            self.X = self.right_foot.x
            self.Y = self.right_foot.y
            self.Xl = self.left_foot.x
            self.Yl = self.left_foot.y
        else:  # detects when the player is on the ground again and allows for regular movement
            self.airborne = False
        s = 20
        # calculates the parabolic arc that the foot is going to take to get to its destination
        if self.move:
            if Vec2d.get_distance(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy)) > 1:
                self.X += ((self.endx - self.X)/abs(self.endx - self.X))*s
                y = (IK3.parabola(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy), self.X))
                self.Y = y

                self.right_foot = Vec2d(self.X, self.Y)
            else:
                self.X = self.endx
                self.Y = self.endy
                self.move = False
        if self.movel:
            if Vec2d.get_distance(Vec2d(self.startxl, self.startyl), Vec2d(self.endxl, self.endyl)) > 1:
                self.Xl += ((self.endxl - self.Xl)/abs(self.endxl - self.Xl))*s
                y = (IK3.parabola(Vec2d(self.startxl, self.startyl), Vec2d(self.endxl, self.endyl), self.Xl))
                self.Yl = y

                self.left_foot = Vec2d(self.Xl, self.Yl)
            else:
                self.Xl = self.endxl
                self.Yl = self.endyl
                self.movel = False
        # moves the feet to a specific position when they are airborne
        if self.airborne:
            self.X += ((self.center_x+24) - self.X) * 0.5
            self.Y += ((self.center_y-32) - self.Y) * 0.5
            self.right_foot = Vec2d(self.X, self.Y)
            self.Xl += ((self.center_x-24) - self.Xl) * 0.5
            self.Yl += ((self.center_y - 32) - self.Yl) * 0.5
            self.left_foot = Vec2d(self.Xl, self.Yl)
        self.limbs()
        # makes the javalin move at a proportinal speed when returning to the player
        if self.return_jav:
            if arcade.get_distance_between_sprites(self.javlin, self) > 50:
                self.javlin.center_x += (self.center_x-self.javlin.center_x)*0.2
                self.javlin.center_y += (self.center_y-self.javlin.center_y)*0.2
            else:
                self.return_jav = False
                self.R = True
        # swaps the direction that the player and javalin are facingwhen they get to a certan angle
        if 1.6 >= math.atan2((self.mouseY-self.center_y), (self.mouseX - self.center_x)) >= -1.6:
            self.FACING = 1
        else:
            self.FACING = 0
        if self.R:
            self.javlin.position = self.position
            angle = math.atan2((self.mouseY-self.javlin.center_y), (self.mouseX - self.javlin.center_x))
            self.javlin.angle = math.degrees(angle)
        else:
            pass
        # runs when the javalin is thrown
        if self.throw:
            # saves the initial variables of the throw and gives them to the parabolic calculator to calculate
            # the path the javalin is going to take after being thrown
            c = [self.javlin.center_x, self.javlin.center_y]
            a = math.radians(self.javlin.angle + 90)
            f = (c[0] + 34 * math.sin(a), c[1] - 34 * math.cos(a))
            # sets the hitbox of the javalin so that only the tip can collide with the walls
            self.javlin_hitbox.center_x = f[0]
            self.javlin_hitbox.center_y = f[1]
            # adds the javalin to the wall list if the javalin hits a wall so that it can be jumped on
            if not arcade.check_for_collision_with_list(self.javlin_hitbox, self.wall_list):
                self.T += 0.5 * ((self.JTX - self.JSX)/abs(self.JTX - self.JSX))

                a = IK3.trajectory(Vec2d(self.JSX, self.JSY), Vec2d(self.JTX, self.JTY), self.T)
                self.javlin.center_x = a[0]
                self.javlin.center_y = a[1]
                a = IK3.trajectory(Vec2d(self.JSX, self.JSY), Vec2d(self.JTX, self.JTY),
                                   self.T+((self.JTX - self.JSX)/abs(self.JTX - self.JSX)))
                angle = math.atan2((a[1] - self.javlin.center_y), (a[0] - self.javlin.center_x))
                self.javlin.angle = math.degrees(angle)
            else:
                self.throw = False
                self.JSX = self.javlin.center_x
                self.JSY = self.javlin.center_y
                self.JTX = self.JSX
                self.JTY = self.JSY
                self.wall_list.insert(0, self.javlin)
        # if the player is hurt remove a health
        if self.hurt and self.health[0] > 1:
            self.position = self.jump_point
            self.health[0] -= 1
            self.hurt = False
        # if the player takes damage on 1 health kill the player
        elif self.hurt:
            self.health[0] -= 1
            self.dead = True
            self.hurt = False

        if self.javlin in self.wall_list:
            # if the javalin becomes solid while intersecting with the player this code attempts to put the player
            # on top of the javalin to avoid clipping issues that could cause the player to fall through the word
            if arcade.check_for_collision(self, self.javlin):
                c = [self.javlin.center_x, self.javlin.center_y]
                jav_angle = self.javlin.angle
                a = math.radians(jav_angle)
                # f = (c[0] + 64 * math.sin(a), c[1] - 64 * math.cos(a))
                b = (c[0] - 64 * math.sin(a), c[1] + 64 * math.cos(a))
                self.change_x = 0
                self.change_y = 0
                if (60*(math.pi/180)) <= a <= (120*(math.pi/180)) or (-120*(math.pi/180)) <= a <= (-60*(math.pi/180)):
                    # self.center_x = b[0]
                    self.center_y = b[1] + 128
                elif math.pi <= a <= 0:
                    self.center_x = self.javlin.center_x
                    y = self.center_y - self.javlin.center_y
                    self.center_y = c[1] + (y+70) * math.cos(a)
                elif -math.pi <= a <= 0:
                    self.center_x = self.javlin.center_x
                    y = self.center_y - self.javlin.center_y
                    self.center_y = c[1] - (y+70) * math.cos(a)


class Javlin(arcade.Sprite):
    """ The class for the javelin """
    def __init__(self):
        super().__init__()
        # define variables and functions used by the javalin
        self.texture = arcade.load_texture('Sprites/Player/Javlin.png')

        self.hit_point_list = arcade.SpriteList()
        self.hit_point = arcade.Sprite('Sprites/Player/Crosshair_Center.png')
        self.hit_point.center_x = 0
        self.hit_point.center_y = 0
        self.hit_point_list.append(self.hit_point)


class DisplayHealth(arcade.Sprite):
    """ The class for the players health """
    def __init__(self):
        super().__init__()
        # define variables and functions used by the player for health
        self.texture = arcade.load_texture('Sprites/UI/HealthBar.png')
        self.view_left = 0
        self.view_bottom = 0
        self.view_center = 0
        self.health = 3
        self.max_health = 3
        self.bar = arcade.Sprite('Sprites/UI/HealthBarBar.png')
        self.bar_list = arcade.SpriteList()
        self.bar.center_x = self.center_x
        self.bar.center_y = self.center_y
        self.bar_list.append(self.bar)

    def draw(self):
        """ Draws the players health """
        width = 492*(self.health/self.max_health)
        self.bar.center_x = self.center_x + 60 - (492 - width)/2
        self.bar.center_y = self.center_y
        self.bar.width = width
        self.bar_list.draw()
