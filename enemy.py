import arcade
import constants


class Enemy(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture('Sprites/Player/Crosshair_Center.png')
        self.path = None
        self.A = False
        self.D = False
        self.pathfind = False
        self.jump = True
        self.level_list = None
        self.barrier_list = None
        self.enemypos = None
        self.playerpos = None

    def on_key_press(self, key: int):
        if key == arcade.key.UP:
            self.change_y = constants.JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.A = True
        elif key == arcade.key.RIGHT:
            self.D = True
        elif key == arcade.key.LSHIFT:
            if self.pathfind:
                self.pathfind = False
            else:
                self.pathfind = True

    def on_key_release(self, key: int):
        if key == arcade.key.LEFT:
            self.A = False
        elif key == arcade.key.RIGHT:
            self.D = False

    def update(self):

        if self.change_x > constants.FRICTION:
            self.change_x -= constants.FRICTION
        elif self.change_x < -constants.FRICTION:
            self.change_x += constants.FRICTION
        else:
            self.change_x = 0

        # Apply acceleration based on the keys pressed

        if self.A and not self.D:
            self.change_x += -constants.ACCELERATION_RATE
        elif self.D and not self.A:
            self.change_x += constants.ACCELERATION_RATE

        if self.path and len(self.path) > 1 and self.pathfind:
            # print(f'Enemy position:{self.position}, First Point:{self.path[1]}')
            xpos = self.path[1][0]
            ypos = self.path[1][1]
            item = [item[1] for item in self.path if item[1] > ypos]
            # print(f'this is item{item}')
            if self.center_x > xpos:
                self.change_x += -constants.ACCELERATION_RATE
            elif self.center_x < xpos:
                self.change_x += constants.ACCELERATION_RATE

            if len(item) and self.physics_engines[0].can_jump() and self.change_y < 0:
                self.change_y = constants.JUMP_SPEED

            elif self.center_y + 32 < ypos and self.physics_engines[0].can_jump():
                self.change_y = constants.JUMP_SPEED

        if self.change_x > constants.MAX_SPEED:
            self.change_x = constants.MAX_SPEED
        elif self.change_x < -constants.MAX_SPEED:
            self.change_x = -constants.MAX_SPEED

    """def shoot(self):
        start_x = enemy.center_x
        start_y = enemy.center_y

        dest_x = self.player.center_x
        dest_y = self.player.center_y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Set the enemy to face the player.
        # enemy.angle = math.degrees(angle) - 90

        # Shoot every 60 frames change of shooting each frame
        if arcade.has_line_of_sight(self.player.position, enemy.position, self.wall_list):
            if self.frame_count % 60 == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = start_x
                bullet.center_y = start_y - 10

                # Angle the bullet sprite
                bullet.angle = math.degrees(angle)

                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the bullet travels.
                bullet.change_x = math.cos(angle) * constants.BULLET_SPEED
                bullet.change_y = math.sin(angle) * constants.BULLET_SPEED

                self.bullet_list.append(bullet)"""
