import arcade
import math
from pymunk import Vec2d


class Segment:
    def __init__(self, x, y, len_, angle_):
        super().__init__()
        self.a = Vec2d(x, y)
        self.angle = angle_
        self.length = len_
        self.b = Vec2d
        self.mouseX = None
        self.mouseY = None
        self.calculateB()

    def follow(self, targetx, targety):
        target = Vec2d(targetx, targety)
        direction = (target-self.a)
        self.angle = direction.angle
        direction = direction.scale_to_length(self.length)
        direction = direction.__mul__(-1)

        self.a = (target + direction)

    def calculateB(self):
        dx = self.length * math.cos(self.angle)
        dy = self.length * math.sin(self.angle)
        self.b = Vec2d(self.a.x+dx, self.a.y+dy)

    def draw(self):
        arcade.draw_line(self.a.x, self.a.y, self.b.x, self.b.y, arcade.color.WHITE)

    def update(self):
        pass
        self.calculateB()

class Segment2:
    def __init__(self, parent_, len_, angle_):
        super().__init__()
        parent = parent_
        self.a = parent.b
        self.angle = angle_
        self.length = len_
        self.b = Vec2d
        self.mouseX = None
        self.mouseY = None
        self.calculateB()

    def follow(self, targetx, targety):
        target = Vec2d(targetx, targety)
        direction = (target-self.a)
        self.angle = direction.angle
        direction = direction.scale_to_length(self.length)
        direction = direction.__mul__(-1)

        self.a = (target + direction)

    def calculateB(self):
        dx = self.length * math.cos(self.angle)
        dy = self.length * math.sin(self.angle)
        self.b = Vec2d(self.a.x+dx, self.a.y+dy)

    def draw(self):
        arcade.draw_line(self.a.x, self.a.y, self.b.x, self.b.y, arcade.color.WHITE, 3)

    def update(self):
        self.calculateB()


class IK(arcade.Window):
    def __init__(self):
        """
        Initializer
        """
        super().__init__(1200, 700, 'inverse Kinimatics')
        arcade.set_background_color((51, 51, 51))
        self.seg1 = None
        self.seg2 = None
        self.mouseX = None
        self.mouseY = None
        self.current = None
        self.next = None
        self.key = None

    def setup(self):
        self.mouseX = 0
        self.mouseY = 0
        self.seg1 = Segment(300, 200, 100, 0)
        self.seg2 = Segment2(self.seg1, 100, 0)
    def on_draw(self):
        arcade.start_render()
        self.current = self.next = self.seg1

        self.seg1.draw()
        self.seg2.draw()

        self.seg2.follow(self.mouseX, self.mouseY)
        self.seg1.follow(self.seg2.a.x, self.seg2.a.y)

        self.seg1.update()
        self.seg2.update()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouseX = x
        self.mouseY = y
    def on_key_press(self, key: int, modifiers: int):
        self.key = key


def main():
    window = IK()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
