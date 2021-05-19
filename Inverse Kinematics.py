import arcade
import math
from pymunk import Vec2d
import time
a = Vec2d(200, -100)
b = Vec2d(200, 100)
c = a - b  # or Vector2(0, -200)
alpha = math.atan2(a.y - b.y, a.x - b.y)
points = [Vec2d(100, 100), Vec2d(200, 100), Vec2d(300, 100), Vec2d(400, 100), Vec2d(500, 100)]
target = Vec2d(450, 300)

rel_points = []
angles = []
for i in range(len(points)):
    rel_points.append(points[i] - points[i-1])
    angles.append(0)

i = len(points) - 2  # second-to-last index
endpoint = a
current_point = b

diff = (endpoint - current_point) - (target - current_point)
angle = math.atan2(diff.y, diff.x)
angles[i] += angle


i = len(points) - 3  # third-to-last index
endpoint = a - rel_points[len(points)-1] + rel_points[len(points)-1].rotated_degrees(angles[i+1])

current_point = b

diff = (endpoint - current_point) - (target - current_point)
angle = math.atan2(diff.y, diff.x)
angles[i] += angle


def solve_ik(i, endpoint, target):
    if i < len(points) - 2:
        endpoint = solve_ik(i+1, endpoint, target)
    current_point = points[i]
    diff = (endpoint-current_point) - (target-current_point)
    angle = math.atan2(diff.y, diff.x)
    angles[i] += angle

    return current_point + (endpoint-current_point).rotated_degrees(angle)


def render():
    black = 0, 0, 0
    white = 255, 255, 255
    arcade.start_render()
    #arcade.set_background_color(white)
    for i in range(1, len(points)):
        prev = points[i-1]
        cur = points[i]
        arcade.draw_lines((prev, cur), black, 5)
        #print(prev, cur)
    for point in points:
        arcade.draw_circle_filled(int(point[0]), int(point[1]), 5, black)
        #print('point')
    arcade.draw_circle_filled(int(target[0]), int(target[1]), 10, black)
    #print('point destination')


arcade.open_window(640, 480, 'IK')
g=1
while 1:
    g+= 1
    print(g)
    start = time.time()
    solve_ik(0, points[-1], target)

    angle = 0
    for i in range(1, len(points)):
        angle += angles[i-1]
        points[i] = points[i-1] + rel_points[i-1].rotated_degrees(angle)
    end = time.time()
    render()
    time.sleep(1/60)
