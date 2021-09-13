"""
Name: IK3.py
Author: Hugh McCutcheon
Description: mainly a testing area but also used to hold parabola and inverse kinamatic calculations
"""
import math
import arcade
from pymunk import Vec2d

white = (255, 255, 255)


def parabola(f_: Vec2d = (0, 0), t_: Vec2d = (1, 0), x_: float = 0):
    """ Calculate a parabolic arc e.g for throwing, foot movement"""
    x = x_  # the current x position of the end joint (foot)
    f = f_  # the starting position
    t = t_  # the target position

    # s = ((f.y+t.y)/2)+1*((f.x+t.x)/200)  # the y position that the graph apexes at
    g = Vec2d(((f.x+t.x)/2), ((f.y+t.y)/2)+15)  # the apex of the graph
    a1 = -f.x**2+g.x**2
    b1 = -f.x+g.x
    d1 = -f.y+g.y
    a2 = -f.x**2+t.x**2
    b2 = -f.x+t.x
    d2 = -f.y+t.y
    b_multiplier = -(b2/b1)
    a3 = b_multiplier*a1+a2
    d3 = b_multiplier*d1+d2
    a = (d3/a3)
    b = ((d1-a1*a)/b1)
    c = f.y-(a*f.x**2)-b*f.x
    r = a*x**2+b*x+c  # the curve with respect to the x axcis
    return r


def trajectory(s_: Vec2d = (0, 0), e_: Vec2d = (1, 1), t_: float = 0):
    """ Calculate a trajectory e.g. for throwing or foot movement"""
    s = s_
    e = e_
    alpha = math.atan((s.y - e.y)/(s.x-e.x))
    # h = 0
    g = 1
    v = 50
    t = t_
    a = s.x+v*t*math.cos(alpha)
    b = s.y+v*t*math.sin(alpha)-1/2*g*t**2
    return Vec2d(a, b)


# an inverse kinamatic solver this is used to calculate the position of my character arms and legs.
# The whole function is basicly just an equation which is used for limbs
def IK_solverR(s_, h_, c_, a_, f_):
    """
    :param s_: The starting Point
    :param h_: The target point
    :param c_: The length of the firts segment
    :param a_: The length of the secong segment
    :param f_: What direction the knee should be facing
    :return: a point list of limbs
    """
    f = f_  # the direction that the bend should be pointing

    s = s_
    h = h_
    c = c_
    a = a_
    b = math.sqrt((h.x - s.x) ** 2 + (h.y - s.y) ** 2)

    # b=math.pi-beta

    if Vec2d.get_distance(s, h) > c+a or s.x == h.x:
        if (h.x-s.x) == 0:
            a1 = math.pi/2
            b = 0
        else:
            a1 = math.atan((h.y - s.y) / (h.x-s.x))
            b = 0
        a2 = a1  # to flip do A1-alpha
        # j = a1
    else:
        a1 = math.atan((h.y - s.y) / (h.x - s.x))
        alpha = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        beta = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))
        b = beta-math.pi
        facing = {
            'right': alpha + a1,
            'left': a1 - alpha
        }

        a2 = facing[f]  # to flip do A1-alpha
    facingj = {
        'right': b + a2,
        'left': a2 - b
    }
    j = facingj[f]
    if s.x >= h.x:
        x3 = s.x-c*math.cos(a2)
        y3 = s.y-c*math.sin(a2)
    else:
        x3 = s.x + c * math.cos(a2)
        y3 = s.y + c * math.sin(a2)
    e = Vec2d(x3, y3)
    if s.x >= h.x:
        x4 = e.x-a*math.cos(j)
        y4 = e.y-a*math.sin(j)
    else:
        x4 = e.x + a * math.cos(j)
        y4 = e.y + a * math.sin(j)
    r = Vec2d(x4, y4)

    point_list = [s, e, r]
    return point_list


# calculates the end point for the foot depending on where the foot my my character started
def foot_target(o_: Vec2d = (0, 0), d_: float = 16, h_: float = 10, p_: float = 0):
    """ Calculate the target point of the foot """
    o = o_  # origin
    d = d_  # distance till the foot has to move
    h = h_  # height of step
    p = p_  # x position of foot
    c = -h*math.cos((math.pi/d)*p)+o.y+h
    g = Vec2d(p, c)
    return g


# code that is used to read the pixels at a point of an image
def clip(surf, x, y, x_size, y_size):
    """ clip an image """
    handle_surf = surf.copy()
    clipr = arcade.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipr)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


# a view I used to test inverse kinamatics while i was making them this code is deprecated
class IK(arcade.Window):
    """ Used for testing of IK (depricated)"""
    def __init__(self):
        """
        Initializer
        """
        super().__init__(1280, 720, 'inverse Kinimatics')
        arcade.set_background_color((51, 51, 51))
        self.joint0 = None
        self.joint1 = None
        self.joint2 = None
        self.mouseX = None
        self.mouseY = None
        self.mouse = None
        self.current = None
        self.next = None
        self.key = None
        self.count = 1
        self.speed = 100.0

        self.startx = None
        self.starty = None
        self.endx = None
        self.endy = None
        self.distance = None
        self.direction_x = None
        self.direction_y = None
        self.X = None
        self.Y = None
        self.move = False

    def setup(self):
        self.X = 40
        self.Y = 40
        self.joint0 = Vec2d(500, 750)
        self.joint1 = Vec2d(250, 375)
        self.joint2 = Vec2d(600, 350)
        self.mouseX = 40
        self.mouseY = 40
        self.mouse = Vec2d(150, 150)

        self.move = False

    def on_draw(self):
        arcade.start_render()
        points = IK_solverR(self.joint2, self.mouse, 160, 160, 'right')
        npoint = Vec2d(self.mouseX+16, self.mouseY-32)
        arcade.draw_line_strip(points, white, 5)
        arcade.draw_point(npoint.x, npoint.y, white, 5)
        arcade.draw_point(self.X, self.Y, white, 5)
        arcade.draw_points((points[1], points[2]), white, 50)
        # speed = 100
        arcade.draw_text(str(self.Y), 100, 100, white)

    def on_update(self, delta_time: float):

        if self.move:
            if Vec2d.get_distance(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy)) > 1:
                self.X += (self.endx-self.X) * 0.2
                y = (parabola(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy), self.X))
                self.Y = y
                self.joint2 = Vec2d(self.X, self.Y)
            else:
                print('finish')
                self.X = self.endx
                self.Y = self.endy
                self.move = False
            """y = (parabola(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy), self.X))
            self.joint2 = Vec2d(self.X, self.Y)
            self.X += self.direction_x * self.speed * delta_time
            self.Y = y
            if math.sqrt(math.pow(self.X - self.startx, 2)+math.pow(self.Y-self.starty, 2)) >= self.distance:
                print('finish')
                self.X = self.endx
                self.Y = self.endy
                self.move = False"""

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.A:
            self.move = True
            self.startx = self.joint2.x
            self.starty = self.joint2.y
            self.endx = self.mouseX+16
            self.endy = self.mouseY - 32
            self.distance = Vec2d.get_distance(Vec2d(self.startx, self.starty), Vec2d(self.endx, self.endy))
            self.direction_x = (self.endx-self.startx)/self.distance
            self.direction_y = (self.endy-self.starty)/self.distance
            self.X = self.startx
            self.Y = self.starty
        """if key == arcade.key.E:
            e = text(Image.open('Sprites/Medievil text.png'))"""

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouseX = x
        self.mouseY = y
        self.mouse = Vec2d(x, y)


def main():
    window = IK()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
