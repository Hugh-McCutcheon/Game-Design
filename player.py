import arcade
import IK3
import constants
import math
from pymunk import Vec2d


class PlayerCharacter(arcade.Sprite):
    """ The player class. """
    def __init__(self):
        super().__init__()
        # variables
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
        self.temp_grav = constants.GRAVITY

        # the limbs
        self.right_foot = Vec2d(self.center_x, self.center_y - 32)
        self.right_leg = [0, 1, 2]
        self.left_foot = Vec2d(self.center_x, self.center_y - 32)
        self.left_leg = [0, 1, 2]
        self.right_arm = [0, 1, 2]
        self.left_arm = [0, 1, 2]

        self.count = 1
        #self.speed = 300

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
        self.delta_time = 1/60
        # end of animations for the player
        #  javlin
        self.javlin = Javlin()
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


    def on_key_press(self, key: int):
        if key == arcade.key.SPACE or key == arcade.key.W:
            if self.physics_engines[self.level - 1].can_jump():
                self.change_y = constants.JUMP_SPEED
                self.space_held = True
                self.temp_grav = 0.5
        elif key == arcade.key.A:
            self.A = True
        elif key == arcade.key.D:
            self.D = True


    def on_key_release(self, key: int):
        if key == arcade.key.SPACE or key == arcade.key.W:
            self.space_held = False
            if self.change_y > 0:
                self.change_y *= constants.CUT_JUMP_HEIGHT
            self.temp_grav = constants.GRAVITY
        elif key == arcade.key.A:
            self.A = False
        elif key == arcade.key.D:
            self.D = False

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        if button == arcade.MOUSE_BUTTON_LEFT and self.R:
            self.L = True
            self.R = False
            self.JSX = self.javlin.center_x
            self.JSY = self.javlin.center_y
            self.JTX = self.mouseX
            self.JTY = self.mouseY
            self.throw = True
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.T = 0
            if self.javlin in self.wall_list:
                self.wall_list.remove(self.javlin)

            self.return_jav = True
            self.throw = False

    def on_mouse_release(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.L = False
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            #self.R = False
            print('nene')
    def limbs(self):
        facing = ['left', 'right']
        self.right_leg = IK3.IK_solverR(Vec2d(self.center_x, self.center_y+((self.right_foot.y - self.left_foot.y)/5)-7)
                                        , self.right_foot, 31, 31, facing[self.FACING])
        self.left_leg = IK3.IK_solverR(Vec2d(self.center_x, self.center_y+((self.right_foot.y - self.left_foot.y)/5)-7)
                                       , self.left_foot, 31, 31, facing[self.FACING])
        facing = ['right', 'left']
        angle = ((math.atan2((self.mouseY-self.javlin.center_y), (self.mouseX - self.javlin.center_x)))+(math.pi/2))
        x = self.javlin.center_x+(32*math.sin(-angle))
        y = self.javlin.center_y+(32*math.cos(-angle))
        self.right_arm = IK3.IK_solverR(Vec2d(self.center_x, self.center_y+30), Vec2d(x, y), 28, 28, facing[self.FACING])
        x = self.javlin.center_x + (32 * math.sin(-angle-math.pi))
        y = self.javlin.center_y + (32 * math.cos(-angle-math.pi))
        self.left_arm = IK3.IK_solverR(Vec2d(self.center_x, self.center_y + 30), Vec2d(x, y), 28, 28,
                                        facing[self.FACING])
        #self.left_arm = IK3.IK_solverR()
    def draw(self):
        facing = {
            0: True,
            1: False
        }
        grey = arcade.color.BATTLESHIP_GREY
        darkbrown = arcade.color.DARK_BROWN
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
        # Add some friction
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
            print(1)
        else:
            self.change_x = 0

        n = 64
        if self.right_foot.x < self.center_x - n:
            self.move = True
            self.startx = self.right_foot.x
            self.starty = self.right_foot.y
            self.endx = self.center_x + n
            self.endy = self.center_y-64
            self.X = self.startx
            self.Y = self.starty
        elif self.right_foot.x > self.center_x + n:
            self.move = True
            self.startx = self.right_foot.x
            self.starty = self.right_foot.y
            self.endx = self.center_x - n
            self.endy = self.center_y - 64
            self.X = self.startx
            self.Y = self.starty
        if self.left_foot.x < self.center_x - n:
            self.movel = True
            self.startxl = self.left_foot.x
            self.startyl = self.left_foot.y
            self.endxl = self.center_x + n
            self.endyl = self.center_y-64
            self.Xl = self.startxl
            self.Yl = self.startyl
        elif self.left_foot.x > self.center_x + n:
            self.movel = True
            self.startxl = self.left_foot.x
            self.startyl = self.left_foot.y
            self.endxl = self.center_x - n
            self.endyl = self.center_y - 64
            self.Xl = self.startxl
            self.Yl = self.startyl
        if self.change_x == 0 and self.change_y == 0:
            self.move = False
            self.movel = False
            self.right_foot = Vec2d(self.center_x+32, self.center_y-64)
            self.left_foot = Vec2d(self.center_x-32, self.center_y-64)
        if not self.physics_engines[0].can_jump():
            self.move = False
            self.movel = False
            self.airborne = True
            self.X = self.right_foot.x
            self.Y = self.right_foot.y
            self.Xl = self.left_foot.x
            self.Yl = self.left_foot.y
        else:
            self.airborne = False
        s = 20
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
        if self.airborne:
            self.X += ((self.center_x+24) - self.X) * 0.5
            self.Y += ((self.center_y-32) - self.Y) * 0.5
            self.right_foot = Vec2d(self.X, self.Y)
            self.Xl += ((self.center_x-24) - self.Xl) * 0.5
            self.Yl += ((self.center_y - 32) - self.Yl) * 0.5
            self.left_foot = Vec2d(self.Xl, self.Yl)
        self.limbs()
        if self.return_jav:
            if arcade.get_distance_between_sprites(self.javlin, self) > 50:
                self.javlin.center_x += (self.center_x-self.javlin.center_x)*0.2
                self.javlin.center_y += (self.center_y-self.javlin.center_y)*0.2
            else:
                self.return_jav = False
                self.R = True
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

        if self.throw:

            if not arcade.check_for_collision_with_list(self.javlin, self.wall_list):

                self.T += 0.5 * ((self.JTX - self.JSX)/abs(self.JTX - self.JSX))

                a = IK3.trajectory(Vec2d(self.JSX, self.JSY), Vec2d(self.JTX, self.JTY), self.T)
                self.javlin.center_x = a[0]
                self.javlin.center_y = a[1]
                a = IK3.trajectory(Vec2d(self.JSX, self.JSY), Vec2d(self.JTX, self.JTY), self.T+((self.JTX - self.JSX)/abs(self.JTX - self.JSX)))
                angle = math.atan2((a[1] - self.javlin.center_y), (a[0] - self.javlin.center_x))
                self.javlin.angle = math.degrees(angle)
            else:
                self.throw = False
                self.JSX = self.javlin.center_x
                self.JSY = self.javlin.center_y
                self.JTX = self.JSX
                self.JTY = self.JSY
                self.wall_list.insert(0, self.javlin)





    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0 and self.FACING == 0 or self.change_x > 0 and self.FACING == 1:
            self.cur_texture += 1
            if self.cur_texture >= 4 * constants.UPDATES_PER_FRAME:
                self.cur_texture = 0

        elif self.change_x != 0:
            self.cur_texture += 1
            if self.cur_texture >= 4 * constants.UPDATES_PER_FRAME:
                self.cur_texture = 0


class Javlin(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture('Sprites/Player/Javlin.png')
