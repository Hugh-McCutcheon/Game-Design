import math
import arcade
from pymunk import Vec2d
from PIL import Image

white = (255, 255, 255)


def parabola(f_: Vec2d = (0, 0), t_: Vec2d = (1, 0), x_: float = 0):
    x = x_  # the current x position of the end joint (foot)
    f = f_  # the starting position
    t = t_  # the target position

    s = ((f.y+t.y)/2)+1*((f.x+t.x)/200)  # the y position that the graph apexes at
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
    s = s_
    e = e_
    alpha = math.atan((s.y - e.y)/(s.x-e.x))
    h = 0
    g = 1
    v = 50
    t = t_
    a = s.x+v*t*math.cos(alpha)
    b = s.y+v*t*math.sin(alpha)-1/2*g*t**2
    return Vec2d(a, b)

"""
def IK_solverR(s_, h_, c_, a_, f_):
    f = f_  # the direction that the bend should be pointing

    S = s_
    H = h_
    c = c_
    a = a_
    b = math.sqrt((H.x - S.x) ** 2 + (H.y - S.y) ** 2)


    #B=math.pi-beta


    if Vec2d.get_distance(S, H) > c+a:# or S.x == H.x:
        if (H.x-S.x) == 0:
            A1 = math.pi/2
            B = 0
        else:
            A1 = math.atan((H.y - S.y) / (H.x-S.x))
        A = A1  # to flip do A1-alpha

    else:
        A1 = math.atan((H.y - S.y) / (H.x - S.x))
        alpha = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        beta = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))
        gamma = math.pi - (alpha + beta)
        facing = {
            'right': alpha + A1,
            'left': A1 - alpha
        }
        A = facing[f]  # to flip do A1-alpha


    if S.x >= H.x:
        x3 = S.x-c*math.cos(A)
        y3 = S.y-c*math.sin(A)
    else:
        x3 = S.x + c * math.cos(A)
        y3 = S.y + c * math.sin(A)
    E = Vec2d(x3, y3)



    point_list = [S, E, H]
    return point_list"""


def IK_solverR(s_, h_, c_, a_, f_):
    """

    :param s_: The starting Point
    :param h_: The target point
    :param c_: The length of the firts segment
    :param a_: The length of the secong segment
    :param f_: What direction the knee should be facing
    :return: a point list of the legs
    """
    f = f_  # the direction that the bend should be pointing

    S = s_
    H = h_
    c = c_
    a = a_
    b = math.sqrt((H.x - S.x) ** 2 + (H.y - S.y) ** 2)


    #B=math.pi-beta


    if Vec2d.get_distance(S, H) > c+a or S.x == H.x:
        if (H.x-S.x) == 0:
            A1 = math.pi/2
            B = 0
        else:
            A1 = math.atan((H.y - S.y) / (H.x-S.x))
            B = 0
        A = A1  # to flip do A1-alpha
        j = A1
    else:
        A1 = math.atan((H.y - S.y) / (H.x - S.x))
        alpha = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
        beta = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))
        B = beta-math.pi
        facing = {
            'right': alpha + A1,
            'left': A1 - alpha
        }

        A = facing[f]  # to flip do A1-alpha
    facingj = {
        'right': B + A,
        'left': A - B
    }
    j = facingj[f]
    if S.x >= H.x:
        x3 = S.x-c*math.cos(A)
        y3 = S.y-c*math.sin(A)
    else:
        x3 = S.x + c * math.cos(A)
        y3 = S.y + c * math.sin(A)
    E = Vec2d(x3, y3)
    if S.x >= H.x:
        x4 = E.x-a*math.cos(j)
        y4 = E.y-a*math.sin(j)
    else:
        x4 = E.x + a * math.cos(j)
        y4 = E.y + a * math.sin(j)
    r = Vec2d(x4, y4)


    point_list = [S, E, r]
    return point_list


def foot_target(o_: Vec2d = (0, 0), d_: float = 16, h_: float = 10, p_: float = 0):
    o = o_  # origin
    d = d_  # distance till the foot has to move
    h = h_  # height of step
    p = p_  # x position of foot
    c = -h*math.cos((math.pi/d)*p)+o.y+h
    g = Vec2d(p, c)
    return g


def simple_ik(Joint0_: Vec2d=(0,0), Joint1_: Vec2d = (0,0), Hand_: Vec2d = (0,0), Target_: Vec2d = (0,0)):
    Joint0 = Joint0_
    Joint1 = Joint1_
    Hand = Hand_
    Target = Target_
    length0 = Vec2d.get_distance(Joint0, Joint1)
    length1 = Vec2d.get_distance(Joint1, Hand)
    # update
    length2 = Vec2d.get_distance(Joint0, Target)
    diff = Target-Joint0
    atan = math.atan2(diff.y, diff.x)

    if length0+length1 < length2:
        jointAngle0 = atan
        jointAngle1 = 0

    else:

        """alpha"""
        cosAngle0 = ((length2 ** 2+length0**2-length1**2)/(2*length2*length0))
        angle0 = math.acos(cosAngle0)
        """beta"""
        cosAngle1 = ((length1**2+length0**2-length2**2)/(2*length1*length0))
        angle1 = math.acos(cosAngle1)
        """angle from joint0 and target"""

        jointAngle0 = atan - angle0
        jointAngle1 = math.pi - angle1



    Joint0 = Joint0.rotated(jointAngle0)
    Joint1 = Joint0 + Joint1.rotated(jointAngle0)
    Hand = Joint1 + Hand.rotated(jointAngle1)
    a = Joint0
    b = Joint1
    c = Hand
    IK_list = [a, b, c]
    return IK_list


def clip(surf, x, y, x_size, y_size):
    handle_surf = surf.copy()
    clipR = arcade.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clipR)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


def text(image):
    """
    :param Image image:
    :return:
    """
    global characters
    spacing = 1
    character_order = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    current_char_width = 0
    characters = []
    character_count = 0
    for x in range(image.width):
        c = image.getpixel((x, 0))
        if c == (127, 127, 127):
            """char_img = clip(image, x-current_char_width, 0, current_char_width, image.height)
            characters[character_order[character_count//2]] = char_img.copy()"""
            character_count += 1
            print(f'What position the character is in: {character_count}')
            print(f'How wide the character is: {current_char_width}')
            print(f'The position of the x is: {x-current_char_width+1}, width={current_char_width}')
            texture = arcade.load_texture('Sprites/Medievil text.png', x=x-current_char_width+1, y=0, width=current_char_width, height=image.height)
            characters.append(texture)
            current_char_width = 0
        else:
            current_char_width += 1
    return tuple(characters)


class IK(arcade.Window):
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

        #global newpoint
        arcade.start_render()
        points = IK_solverR(self.joint2, self.mouse, 160, 160, 'right')
        npoint = Vec2d(self.mouseX+16, self.mouseY-32)
        arcade.draw_line_strip(points, white, 5)
        arcade.draw_point(npoint.x, npoint.y, white, 5)
        arcade.draw_point(self.X, self.Y, white, 5)
        arcade.draw_points((points[1], points[2]), white, 50)
        speed = 100
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
        if key == arcade.key.E:
            e = text(Image.open('Sprites/Medievil text.png'))

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
