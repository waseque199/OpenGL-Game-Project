from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 100
GRID_SIZE = 14
game_over = False
game_started = False
level_won = False
current_level = "start"
monkey_pos = [0, 0, 50]
monkey_angle = 0
monkey_jumping = False
monkey_jump_height = 0
monkey_jump_velocity = 0
JUMP_VELOCITY = 15
GRAVITY = 0.8
monkey_on_platform = False
platform_index = -1
monkey_shield = False
shield_start_time = 0
SHIELD_DURATION = 5
monkey_swinging = True
swing_angle = 0
monkey_invincible = False

mouse_x, mouse_y = 0, 0
camera_mode = "third"
lastx, lasty, lastz = 0, 0, 0


score = 0
life = 3
barrels_dodged = 0
platforms = []
NUM_PLATFORMS = 6
PLATFORM_MIN_HEIGHT = 50
PLATFORM_MAX_HEIGHT = 200
palm_trees = []
ladders = []

goal_coin = {
    "position": [0, 0, 0],
    "rotation": 0,
    "collected": False
}

barrels = []
BARREL_SPAWN_INTERVAL = 3
last_barrel_time = 0
rocks = []
ROCK_SPEED = 15
enemies = []
NUM_ENEMIES = {
    "easy": 3,
    "medium": 7,
    "hard": 10
}
ENEMY_SPEED = 0.8
BARREL_SPEED = 5
min_bound = -GRID_SIZE * GRID_LENGTH // 2
max_bound = GRID_SIZE * GRID_LENGTH // 2


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(font, ord(character))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_large(x, y, text):
    draw_text(x, y, text, GLUT_BITMAP_TIMES_ROMAN_24)


def draw_swinging_monkey():
    global swing_angle
    glPushMatrix()
    glTranslatef(500, 300, 0)

    glColor3f(0.0, 0.6, 0.0)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex2f(0, 200)
    glVertex2f(0, 0)
    glEnd()
    glLineWidth(1.0)
    glPushMatrix()
    glRotatef(swing_angle, 0, 0, 1)
    glTranslatef(0, -80, 0)
    glColor3f(0.6, 0.4, 0.1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(25 * math.cos(angle), 25 * math.sin(angle))
    glEnd()
    glTranslatef(0, 30, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(15 * math.cos(angle), 15 * math.sin(angle))
    glEnd()

    glColor3f(0.5, 0.3, 0.1)
    glBegin(GL_LINES)
    glVertex2f(-25, -30)  # Left arm
    glVertex2f(0, 0)
    glVertex2f(25, -30)  # Right arm
    glVertex2f(0, 0)
    glEnd()

    glBegin(GL_LINES)
    glVertex2f(-15, -50)  # Left leg
    glVertex2f(0, -25)
    glVertex2f(15, -50)  # Right leg
    glVertex2f(0, -25)
    glEnd()

    glPopMatrix()
    glPopMatrix()
    swing_angle = 20 * math.sin(time.time() * 2)


def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    draw_text_large(450, 700, "MONKEY JAX")
    draw_text(450, 500, "SELECT DIFFICULTY:")
    draw_text(450, 450, "Press 'E' for EASY")
    draw_text(450, 400, "Press 'M' for MEDIUM")
    draw_text(450, 350, "Press 'H' for HARD")
    draw_swinging_monkey()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_grid(GRID_SIZE):
    glBegin(GL_QUADS)
    center_offset = GRID_SIZE // 2
    for i in range(GRID_SIZE * GRID_SIZE):
        row = i // GRID_SIZE
        col = i % GRID_SIZE

        is_white = (row + col) % 2 == 0
        glColor3f(0.2, 0.8, 0.2) if is_white else glColor3f(0.15, 0.6, 0.15)  # Green grass colors

        x = (row - center_offset) * GRID_LENGTH
        y = (col - center_offset) * GRID_LENGTH

        vertices = [
            (x, y, 0),
            (x + GRID_LENGTH, y, 0),
            (x + GRID_LENGTH, y + GRID_LENGTH, 0),
            (x, y + GRID_LENGTH, 0)
        ]

        for vertex in vertices:
            glVertex3f(*vertex)

    glEnd()


def draw_border_walls():
    wall_height = 100
    grid_extent = (GRID_LENGTH * GRID_SIZE) // 2

    edges = [
        {"color": (0.8, 0.5, 0.2), "coords": [(-grid_extent, -grid_extent), (grid_extent, -grid_extent)]},  # Front
        {"color": (0.8, 0.5, 0.2), "coords": [(-grid_extent, grid_extent), (grid_extent, grid_extent)]},  # Back
        {"color": (0.8, 0.5, 0.2), "coords": [(-grid_extent, -grid_extent), (-grid_extent, grid_extent)]},  # Left
        {"color": (0.8, 0.5, 0.2), "coords": [(grid_extent, -grid_extent), (grid_extent, grid_extent)]}  # Right
    ]

    glBegin(GL_QUADS)
    for edge in edges:
        glColor3f(*edge["color"])
        (x1, y1), (x2, y2) = edge["coords"]

        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(x2, y2, wall_height)
        glVertex3f(x1, y1, wall_height)
    glEnd()


def draw_palm_tree(position, height=150, trunk_radius=10):
    x, y, z = position

    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.6, 0.4, 0.2)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), trunk_radius, trunk_radius * 0.8, height, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(x, y, z + height)
    leaf_colors = [(0.0, 0.5, 0.0), (0.0, 0.6, 0.0), (0.1, 0.7, 0.1)]

    for i in range(7):
        angle = i * (360.0 / 7)
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glRotatef(45, 1, 0, 0)
        glColor3f(*leaf_colors[i % 3])
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for j in range(8):
            leaf_angle = j * (360.0 / 7)
            x_coord = math.cos(math.radians(leaf_angle)) * trunk_radius * 6
            y_coord = math.sin(math.radians(leaf_angle)) * trunk_radius
            z_coord = math.sin(math.radians(leaf_angle)) * trunk_radius * 3

            glVertex3f(x_coord, y_coord, z_coord)
        glEnd()

        glPopMatrix()
    glPopMatrix()


def draw_palm_trees():
    for tree in palm_trees:
        draw_palm_tree(tree["position"], tree["height"], tree["radius"])


def draw_sphere(radius, slices, stacks):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_FILL)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluSphere(quad, radius, slices, stacks)


def draw_monkey():
    glPushMatrix()
    glTranslatef(*monkey_pos)
    glRotatef(monkey_angle, 0, 0, 1)
    if current_level == "start" and monkey_swinging:
        glRotatef(swing_angle, 1, 0, 0)

    if game_over:
        glRotatef(90, 1, 0, 0)

    glColor3f(0.6, 0.4, 0.1)
    draw_sphere(25, 20, 20)

    # Monkey head
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0.6, 0.4, 0.1)
    draw_sphere(15, 20, 20)

    # Monkey face
    glColor3f(0.9, 0.8, 0.6)
    glTranslatef(0, -10, 0)
    draw_sphere(12, 20, 20)

    # Eyes
    glColor3f(0, 0, 0)
    glTranslatef(-5, 0, 5)
    draw_sphere(3, 10, 10)
    glTranslatef(10, 0, 0)
    draw_sphere(3, 10, 10)

    # Mouth
    glColor3f(0.5, 0.2, 0.2)
    glTranslatef(-5, -5, -5)
    glScalef(1, 0.5, 0.5)
    draw_sphere(5, 10, 10)
    glPopMatrix()

    # Arms
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.1)
    glTranslatef(25, 0, 10)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 30, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.6, 0.4, 0.1)
    glTranslatef(-25, 0, 10)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 30, 10, 10)
    glPopMatrix()

    # Legs
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.1)
    glTranslatef(10, 0, -25)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 25, 10, 10)  # Right leg
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.6, 0.4, 0.1)
    glTranslatef(-10, 0, -25)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 25, 10, 10)  # Left leg
    glPopMatrix()

    # Tail
    glPushMatrix()
    glColor3f(0.6, 0.4, 0.1)
    glTranslatef(0, 20, 0)
    glRotatef(30, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 3, 30, 10, 10)
    glPopMatrix()

    if monkey_shield or monkey_invincible:
        glColor4f(0.3, 0.6, 1.0, 0.5)
        draw_sphere(35, 20, 20)

    glPopMatrix()


def draw_cube(size):
    half_size = size / 2

    vertices = [
        (-half_size, -half_size, half_size),
        (half_size, -half_size, half_size),
        (half_size, half_size, half_size),
        (-half_size, half_size, half_size),

        (-half_size, -half_size, -half_size),
        (-half_size, half_size, -half_size),
        (half_size, half_size, -half_size),
        (half_size, -half_size, -half_size),

        (-half_size, half_size, -half_size),
        (-half_size, half_size, half_size),
        (half_size, half_size, half_size),
        (half_size, half_size, -half_size),

        (-half_size, -half_size, -half_size),
        (half_size, -half_size, -half_size),
        (half_size, -half_size, half_size),
        (-half_size, -half_size, half_size),

        (half_size, -half_size, -half_size),
        (half_size, half_size, -half_size),
        (half_size, half_size, half_size),
        (half_size, -half_size, half_size),

        (-half_size, -half_size, -half_size),
        (-half_size, -half_size, half_size),
        (-half_size, half_size, half_size),
        (-half_size, half_size, -half_size)
    ]

    glBegin(GL_QUADS)
    for i in range(0, len(vertices), 4):
        for j in range(4):
            glVertex3f(*vertices[i + j])
    glEnd()


def draw_platforms():
    for platform in platforms:
        glPushMatrix()
        glTranslatef(*platform["position"])
        glColor3f(0.5, 0.3, 0.1)
        glPushMatrix()
        glScalef(platform["width"], platform["length"], platform["height"])
        draw_cube(1)
        glPopMatrix()

        glColor3f(0.6, 0.4, 0.2)
        glBegin(GL_QUADS)
        half_width = platform["width"] / 2
        half_length = platform["length"] / 2
        height = platform["height"] / 2

        glVertex3f(-half_width, -half_length, height)
        glVertex3f(half_width, -half_length, height)
        glVertex3f(half_width, half_length, height)
        glVertex3f(-half_width, half_length, height)
        glEnd()

        glPopMatrix()


def draw_ladder(start_pos, end_pos):
    start_x, start_y, start_z = start_pos
    end_x, end_y, end_z = end_pos
    dx = end_x - start_x
    dy = end_y - start_y
    dz = end_z - start_z
    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    if length == 0:
        return

    dx /= length
    dy /= length
    dz /= length
    side_x = -dy
    side_y = dx
    side_z = 0
    side_length = math.sqrt(side_x * side_x + side_y * side_y + side_z * side_z)
    if side_length > 0:
        side_x /= side_length
        side_y /= side_length
        side_z /= side_length
    else:
        side_x = 1
        side_y = 0
        side_z = 0

    ladder_width = 40
    rung_spacing = 20
    rung_thickness = 5
    glColor3f(0.6, 0.3, 0.1)
    glPushMatrix()
    rail_thickness = 8
    glBegin(GL_QUADS)
    for i in range(4):
        angle = i * math.pi / 2
        rail_x = math.cos(angle) * rail_thickness / 2
        rail_z = math.sin(angle) * rail_thickness / 2
        glVertex3f(
            start_x + side_x * ladder_width / 2 + rail_x,
            start_y + side_y * ladder_width / 2 + rail_z,
            start_z + side_z * ladder_width / 2
        )

        glVertex3f(
            end_x + side_x * ladder_width / 2 + rail_x,
            end_y + side_y * ladder_width / 2 + rail_z,
            end_z + side_z * ladder_width / 2
        )

        angle_next = (i + 1) * math.pi / 2
        next_rail_x = math.cos(angle_next) * rail_thickness / 2
        next_rail_z = math.sin(angle_next) * rail_thickness / 2

        glVertex3f(
            end_x + side_x * ladder_width / 2 + next_rail_x,
            end_y + side_y * ladder_width / 2 + next_rail_z,
            end_z + side_z * ladder_width / 2
        )

        glVertex3f(
            start_x + side_x * ladder_width / 2 + next_rail_x,
            start_y + side_y * ladder_width / 2 + next_rail_z,
            start_z + side_z * ladder_width / 2
        )
    glEnd()
    glPopMatrix()
    glPushMatrix()
    glBegin(GL_QUADS)
    for i in range(4):
        angle = i * math.pi / 2
        rail_x = math.cos(angle) * rail_thickness / 2
        rail_z = math.sin(angle) * rail_thickness / 2

        glVertex3f(
            start_x - side_x * ladder_width / 2 + rail_x,
            start_y - side_y * ladder_width / 2 + rail_z,
            start_z - side_z * ladder_width / 2
        )

        glVertex3f(
            end_x - side_x * ladder_width / 2 + rail_x,
            end_y - side_y * ladder_width / 2 + rail_z,
            end_z - side_z * ladder_width / 2
        )

        angle_next = (i + 1) * math.pi / 2
        next_rail_x = math.cos(angle_next) * rail_thickness / 2
        next_rail_z = math.sin(angle_next) * rail_thickness / 2

        glVertex3f(
            end_x - side_x * ladder_width / 2 + next_rail_x,
            end_y - side_y * ladder_width / 2 + next_rail_z,
            end_z - side_z * ladder_width / 2
        )

        glVertex3f(
            start_x - side_x * ladder_width / 2 + next_rail_x,
            start_y - side_y * ladder_width / 2 + next_rail_z,
            start_z - side_z * ladder_width / 2
        )
    glEnd()
    glPopMatrix()

    num_rungs = int(length / rung_spacing)
    if num_rungs < 2:
        num_rungs = 2

    glColor3f(0.7, 0.4, 0.1)

    for i in range(num_rungs):
        t = i / (num_rungs - 1)
        rung_x = start_x + t * (end_x - start_x)
        rung_y = start_y + t * (end_y - start_y)
        rung_z = start_z + t * (end_z - start_z)

        glPushMatrix()
        glTranslatef(rung_x, rung_y, rung_z)
        up_z = 1.0
        vert_x = dx
        vert_y = dy
        vert_z = dz
        matrix = [
            side_x, side_y, side_z, 0,
            vert_x, vert_y, vert_z, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]
        glMultMatrixf(matrix)
        glScalef(ladder_width, rung_thickness, rung_thickness)
        draw_cube(1)

        glPopMatrix()


def draw_ladders():
    for ladder in ladders:
        draw_ladder(ladder["start"], ladder["end"])


def draw_disk(radius, slices):
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)
    for i in range(slices + 1):
        angle = 2 * math.pi * i / slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0)
    glEnd()


def draw_goal_coin():
    if goal_coin["collected"]:
        return

    glPushMatrix()
    glTranslatef(*goal_coin["position"])
    glRotatef(goal_coin["rotation"], 0, 0, 1)
    glColor3f(1.0, 0.8, 0.0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    coin_radius = 25
    coin_thickness = 5
    gluCylinder(gluNewQuadric(), coin_radius, coin_radius, coin_thickness, 30, 1)
    glColor3f(1.0, 0.9, 0.0)
    draw_disk(coin_radius, 30)
    glTranslatef(0, 0, coin_thickness)
    draw_disk(coin_radius, 30)
    glPopMatrix()

    glPopMatrix()


def draw_barrel(barrel):
    glPushMatrix()
    glTranslatef(*barrel["position"])
    glRotatef(barrel.get("rotation", 0), 1, 0, 0)

    glColor3f(0.6, 0.3, 0.1)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 15, 15, 25, 20, 5)

    glColor3f(0.7, 0.4, 0.1)
    draw_disk(15, 20)
    glTranslatef(0, 0, 25)
    draw_disk(15, 20)
    glPopMatrix()

    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 15.5, 15.5, 2, 20, 2)
    glTranslatef(0, 0, 11.5)
    gluCylinder(gluNewQuadric(), 15.5, 15.5, 2, 20, 2)
    glTranslatef(0, 0, 11.5)
    gluCylinder(gluNewQuadric(), 15.5, 15.5, 2, 20, 2)
    glPopMatrix()
    glPopMatrix()


def draw_barrels():
    for barrel in barrels:
        draw_barrel(barrel)


def draw_rocks():
    for rock in rocks:
        glPushMatrix()
        glTranslatef(*rock["position"])
        glColor3f(0.5, 0.5, 0.5)
        draw_sphere(8, 10, 10)
        glPopMatrix()


def draw_cone(base, height, slices, stacks):
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_FILL)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluCylinder(quad, base, 0, height, slices, stacks)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    draw_disk(base, slices)
    glPopMatrix()


def draw_enemy(enemy):
    glPushMatrix()
    glTranslatef(*enemy["position"])
    glScalef(enemy["scale"], enemy["scale"], enemy["scale"])
    glColor3f(0.7, 0.0, 0.0)
    draw_sphere(20, 20, 20)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0.9, 0.7, 0.5)
    draw_sphere(15, 20, 20)

    # Eyes
    glColor3f(0, 0, 0)
    glTranslatef(-5, -10, 5)
    draw_sphere(3, 10, 10)
    glTranslatef(10, 0, 0)
    draw_sphere(3, 10, 10)

    # Guard hat
    glColor3f(0.2, 0.2, 0.7)
    glTranslatef(-5, 10, 5)
    glRotatef(-90, 1, 0, 0)
    draw_cone(18, 20, 20, 10)
    glPopMatrix()

    # Guard uniform
    glColor3f(0.2, 0.2, 0.7)
    glPushMatrix()
    glScalef(1, 1, 1.5)
    draw_sphere(20, 20, 20)
    glPopMatrix()

    # Arms
    glColor3f(0.2, 0.2, 0.7)
    glPushMatrix()
    glTranslatef(20, 0, 10)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 7, 5, 25, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-20, 0, 10)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 7, 5, 25, 10, 10)
    glPopMatrix()

    # Legs
    glColor3f(0.2, 0.2, 0.7)
    glPushMatrix()
    glTranslatef(10, 0, -20)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 7, 5, 30, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-10, 0, -20)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 7, 5, 30, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_exit_button():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.8, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(950, 780)
    glVertex2f(990, 780)
    glVertex2f(990, 750)
    glVertex2f(950, 750)
    glEnd()

    glColor3f(0.9, 0.9, 0.9)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(950, 780)
    glVertex2f(990, 780)
    glVertex2f(990, 750)
    glVertex2f(950, 750)
    glEnd()
    glLineWidth(1.0)
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(960, 760)
    for character in "X":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_enemies():
    for enemy in enemies:
        draw_enemy(enemy)


def initialize_platforms():
    platforms.clear()
    platform_positions = [
        (-300, -300, 80),
        (300, -300, 150),
        (-300, 300, 120),
        (300, 300, 180),
        (0, 200, 100),
        (0, -200, 200)
    ]

    for pos in platform_positions:
        platforms.append({
            "position": list(pos),
            "width": 100,
            "length": 100,
            "height": 20
        })

    palm_trees.clear()
    corner_positions = [
        (-GRID_LENGTH * GRID_SIZE // 2 + 50, -GRID_LENGTH * GRID_SIZE // 2 + 50, 0),
        (GRID_LENGTH * GRID_SIZE // 2 - 50, -GRID_LENGTH * GRID_SIZE // 2 + 50, 0),
        (-GRID_LENGTH * GRID_SIZE // 2 + 50, GRID_LENGTH * GRID_SIZE // 2 - 50, 0),
        (GRID_LENGTH * GRID_SIZE // 2 - 50, GRID_LENGTH * GRID_SIZE // 2 - 50, 0)
    ]

    for pos in corner_positions:
        palm_trees.append({
            "position": pos,
            "height": random.randint(120, 180),
            "radius": random.randint(8, 12)
        })

    # Initialize ladders to connect platforms
    ladders.clear()
    # Ground to first platform
    ladders.append({
        "start": [0, 0, 0],
        "end": platforms[5]["position"]  # Platform at [0, -200, 200]
    })

    # Connect platforms with ladders in sequence
    for i in range(len(platforms) - 1):
        start = platforms[i]["position"]
        end = platforms[i + 1]["position"]
        ladders.append({
            "start": start,
            "end": end
        })

    # Set the goal coin on the highest platform
    highest_platform = max(platforms, key=lambda p: p["position"][2])
    goal_coin["position"] = [
        highest_platform["position"][0],
        highest_platform["position"][1],
        highest_platform["position"][2] + highest_platform["height"] // 2 + 30
    ]
    goal_coin["rotation"] = 0
    goal_coin["collected"] = False


def spawn_enemy():
    safe_distance = 300

    while True:
        x = random.uniform(min_bound + 100, max_bound - 100)
        y = random.uniform(min_bound + 100, max_bound - 100)
        z = 50
        dx = x - monkey_pos[0]
        dy = y - monkey_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > safe_distance:
            break

    return {
        "position": [x, y, z],
        "scale": 1.0,
        "scale_dir": 0.005,
        "last_barrel_time": time.time(),
        "speed_multiplier": 1.0
    }


def update_barrels():
    global barrels, monkey_pos, monkey_shield, life, game_over, barrels_dodged, score

    i = 0
    while i < len(barrels):
        barrel = barrels[i]
        barrel["position"][0] += barrel["direction"][0] * barrel["speed"]
        barrel["position"][1] += barrel["direction"][1] * barrel["speed"]
        barrel["position"][2] += barrel["direction"][2] * barrel["speed"] - barrel["gravity"]
        barrel["rotation"] += barrel["rotation_speed"]
        dx = barrel["position"][0] - monkey_pos[0]
        dy = barrel["position"][1] - monkey_pos[1]
        dz = barrel["position"][2] - monkey_pos[2]
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance < 40 and not monkey_shield and not monkey_invincible:
            life -= 1
            barrels.pop(i)

            if life <= 0:
                game_over = True

            continue
        elif distance < 40 and (monkey_shield or monkey_invincible):
            barrels.pop(i)
            barrels_dodged += 1
            score += 5
            continue
        if (barrel["position"][2] <= 0 or
                abs(barrel["position"][0]) > max_bound or
                abs(barrel["position"][1]) > max_bound):
            barrels.pop(i)
            barrels_dodged += 1
            continue

        i += 1


def initialize_enemies():
    global enemies, current_level
    enemies.clear()
    enemy_count = NUM_ENEMIES.get(current_level, 3)
    spawn_interval_multiplier = 1.0
    speed_multiplier = 1.0

    if current_level == "easy":
        spawn_interval_multiplier = 1.5
        speed_multiplier = 0.7
    elif current_level == "medium":
        spawn_interval_multiplier = 1.0
        speed_multiplier = 1.0
    elif current_level == "hard":
        spawn_interval_multiplier = 0.5
        speed_multiplier = 1.3

    for _ in range(enemy_count):
        enemy = spawn_enemy()
        enemy["scale"] = 1.0
        enemy["scale_dir"] = 0.005
        enemy["last_barrel_time"] = time.time() - random.uniform(0, BARREL_SPAWN_INTERVAL * spawn_interval_multiplier)
        enemy["speed_multiplier"] = speed_multiplier
        enemies.append(enemy)


def is_on_platform(pos_x, pos_y, pos_z):
    for i, platform in enumerate(platforms):
        px, py, pz = platform["position"]
        half_width = platform["width"] / 2
        half_length = platform["length"] / 2
        height = platform["height"] / 2
        if (abs(pos_x - px) < half_width and
                abs(pos_y - py) < half_length and
                abs(pos_z - (pz + height)) < 5):
            return True, i

    return False, -1


def throw_rock():
    global mouse_x, mouse_y, monkey_on_platform, monkey_angle
    angle_rad = math.radians(monkey_angle)
    forward_x = -math.sin(angle_rad)
    forward_y = -math.cos(angle_rad)

    start_x = monkey_pos[0] + forward_x * 30
    start_y = monkey_pos[1] + forward_y * 30
    start_z = monkey_pos[2] + 20

    if monkey_on_platform:
        rocks.append({
            "position": [start_x, start_y, start_z],
            "direction": (0, 0, -0.5),
            "speed": ROCK_SPEED
        })
    else:
        if camera_mode == "third":
            viewport = glGetIntegerv(GL_VIEWPORT)
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            winY = viewport[3] - mouse_y

            try:
                near_x, near_y, near_z = gluUnProject(
                    mouse_x, winY, 0.0,
                    modelview, projection, viewport
                )

                far_x, far_y, far_z = gluUnProject(
                    mouse_x, winY, 1.0,
                    modelview, projection, viewport
                )

                dir_x = far_x - near_x
                dir_y = far_y - near_y
                dir_z = far_z - near_z
                length = math.sqrt(dir_x ** 2 + dir_y ** 2 + dir_z ** 2)
                if length > 0:
                    dir_x /= length
                    dir_y /= length
                    dir_z /= length

                    rocks.append({
                        "position": [start_x, start_y, start_z],
                        "direction": (dir_x, dir_y, dir_z),
                        "speed": ROCK_SPEED
                    })
                else:
                    rocks.append({
                        "position": [start_x, start_y, start_z],
                        "direction": (forward_x, forward_y, 0.05),
                        "speed": ROCK_SPEED
                    })
            except:
                rocks.append({
                    "position": [start_x, start_y, start_z],
                    "direction": (forward_x, forward_y, 0.05),
                    "speed": ROCK_SPEED
                })
        else:
            rocks.append({
                "position": [start_x, start_y, start_z],
                "direction": (forward_x, forward_y, 0.05),
                "speed": ROCK_SPEED
            })


def traditional_rock_throw():
    angle_rad = math.radians(monkey_angle)
    direction = (-math.cos(angle_rad), -math.sin(angle_rad), 0.1)

    rocks.append({
        "position": [
            monkey_pos[0] + direction[0] * 30,
            monkey_pos[1] + direction[1] * 30,
            monkey_pos[2] + 20
        ],
        "direction": direction,
        "speed": ROCK_SPEED
    })


def throw_barrel(enemy):
    dx = monkey_pos[0] - enemy["position"][0]
    dy = monkey_pos[1] - enemy["position"][1]
    dz = monkey_pos[2] - enemy["position"][2]
    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    if distance > 0:
        dx /= distance
        dy /= distance
        dz /= distance
    dx += random.uniform(-0.2, 0.2)
    dy += random.uniform(-0.2, 0.2)
    barrels.append({
        "position": [
            enemy["position"][0] + dx * 30,
            enemy["position"][1] + dy * 30,
            enemy["position"][2] + 30
        ],
        "direction": (dx, dy, 0.5),
        "speed": BARREL_SPEED,
        "gravity": 0.02,
        "rotation": 0,
        "rotation_speed": random.uniform(3, 8)
    })


def is_on_platform(pos_x, pos_y, pos_z):
    for i, platform in enumerate(platforms):
        px, py, pz = platform["position"]
        half_width = platform["width"] / 2
        half_length = platform["length"] / 2
        height = platform["height"] / 2
        if (abs(pos_x - px) <= half_width and
                abs(pos_y - py) <= half_length and
                abs(pos_z - (pz + height)) <= 5):
            return True, i

    return False, -1


def is_on_ladder(pos_x, pos_y, pos_z):
    for ladder in ladders:
        start_x, start_y, start_z = ladder["start"]
        end_x, end_y, end_z = ladder["end"]

        dx = end_x - start_x
        dy = end_y - start_y
        dz = end_z - start_z

        ladder_length = math.sqrt(dx * dx + dy * dy + dz * dz)

        if ladder_length > 0:
            dx /= ladder_length
            dy /= ladder_length
            dz /= ladder_length

        mx = pos_x - start_x
        my = pos_y - start_y
        mz = pos_z - start_z

        projection = mx * dx + my * dy + mz * dz
        if 0 <= projection <= ladder_length:
            closest_x = start_x + projection * dx
            closest_y = start_y + projection * dy
            closest_z = start_z + projection * dz

            distance = math.sqrt((pos_x - closest_x) ** 2 +
                                 (pos_y - closest_y) ** 2 +
                                 (pos_z - closest_z) ** 2)
            if distance < 30:
                return True, ladder, projection / ladder_length

    return False, None, 0


def update_monkey_jump():
    global monkey_jumping, monkey_jump_height, monkey_jump_velocity, monkey_on_platform, platform_index
    global monkey_pos
    on_ladder, ladder, ladder_ratio = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])

    if on_ladder and monkey_jumping and monkey_jump_velocity < 0:
        monkey_jumping = False
        monkey_jump_velocity = 0
        if ladder:
            start_x, start_y, start_z = ladder["start"]
            end_x, end_y, end_z = ladder["end"]
            monkey_pos[0] = start_x + (end_x - start_x) * ladder_ratio
            monkey_pos[1] = start_y + (end_y - start_y) * ladder_ratio
            monkey_pos[2] = start_z + (end_z - start_z) * ladder_ratio
        return

    if monkey_jumping:
        monkey_pos[2] += monkey_jump_velocity
        monkey_jump_velocity -= GRAVITY

        if monkey_pos[2] <= 50 and monkey_jump_velocity < 0:
            monkey_pos[2] = 50
            monkey_jumping = False
            monkey_jump_velocity = 0
            monkey_on_platform = False
            platform_index = -1
        is_platform, idx = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])
        if is_platform and monkey_jump_velocity < 0:
            platform = platforms[idx]
            monkey_pos[2] = platform["position"][2] + platform[
                "height"] / 2 + 25
            monkey_jumping = False
            monkey_jump_velocity = 0
            monkey_on_platform = True
            platform_index = idx


def update_rocks():
    global rocks, enemies, score, barrels_dodged
    i = 0
    while i < len(rocks):
        rock = rocks[i]
        rock["position"][0] += rock["direction"][0] * rock["speed"]
        rock["position"][1] += rock["direction"][1] * rock["speed"]
        rock["position"][2] += rock["direction"][2] * rock["speed"]
        if (abs(rock["position"][0]) > max_bound or
                abs(rock["position"][1]) > max_bound or
                rock["position"][2] <= 0 or
                rock["position"][2] > 500):
            rocks.pop(i)
            continue
        hit = False
        j = 0
        while j < len(enemies):
            enemy = enemies[j]
            dx = rock["position"][0] - enemy["position"][0]
            dy = rock["position"][1] - enemy["position"][1]
            dz = rock["position"][2] - enemy["position"][2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < 40:
                hit = True
                rocks.pop(i)
                enemies.pop(j)
                score += 20
                enemies.append(spawn_enemy())
                print(f"Enemy hit! Score: {score}")
                break

            j += 1

        if hit:
            continue
        j = 0
        while j < len(barrels):
            barrel = barrels[j]
            dx = rock["position"][0] - barrel["position"][0]
            dy = rock["position"][1] - barrel["position"][1]
            dz = rock["position"][2] - barrel["position"][2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            if distance < 25:
                rocks.pop(i)
                barrels.pop(j)
                score += 10
                barrels_dodged += 1

                hit = True
                break

            j += 1

        if hit:
            continue

        i += 1


def update_enemies():
    global enemies

    current_time = time.time()

    for enemy in enemies:
        enemy["scale"] += enemy["scale_dir"]
        if enemy["scale"] < 0.8 or enemy["scale"] > 1.2:
            enemy["scale_dir"] *= -1
        dx = monkey_pos[0] - enemy["position"][0]
        dy = monkey_pos[1] - enemy["position"][1]

        distance = math.hypot(dx, dy)

        if distance > 200:
            speed_mult = enemy.get("speed_multiplier", 1.0)
            enemy["position"][0] += (dx / distance) * ENEMY_SPEED * speed_mult
            enemy["position"][1] += (dy / distance) * ENEMY_SPEED * speed_mult

        # Throw barrels occasionally
        barrel_interval = BARREL_SPAWN_INTERVAL * (1.0 / enemy.get("speed_multiplier", 1.0))
        if current_time - enemy["last_barrel_time"] > barrel_interval:
            throw_barrel(enemy)
            enemy["last_barrel_time"] = current_time


def update_shield():
    global monkey_shield

    current_time = time.time()
    if monkey_shield and current_time - shield_start_time > SHIELD_DURATION:
        monkey_shield = False


def place_monkey_random():
    global monkey_pos, monkey_on_platform, platform_index
    margin = 100
    random_x = random.uniform(min_bound + margin, max_bound - margin)
    random_y = random.uniform(min_bound + margin, max_bound - margin)
    monkey_pos[0] = random_x
    monkey_pos[1] = random_y
    monkey_pos[2] = 50
    monkey_on_platform = False
    platform_index = -1


def update_monkey_position():
    global monkey_on_platform, platform_index, monkey_jumping, monkey_jump_velocity
    is_platform, idx = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])

    if is_platform:
        platform = platforms[idx]
        monkey_pos[2] = platform["position"][2] + platform["height"] / 2 + 25  # Platform height + monkey radius
        monkey_on_platform = True
        platform_index = idx
        monkey_jumping = False
        monkey_jump_velocity = 0
    else:
        on_ladder, ladder, ladder_ratio = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])

        if on_ladder:
            monkey_jumping = False
            monkey_jump_velocity = 0
        elif monkey_pos[2] <= 50:
            monkey_pos[2] = 50
            monkey_jumping = False
            monkey_jump_velocity = 0
            monkey_on_platform = False
            platform_index = -1
        else:
            if not monkey_jumping:
                monkey_jumping = True
                monkey_jump_velocity = 0
            if monkey_on_platform:
                monkey_on_platform = False
                platform_index = -1


def check_goal_coin():
    global goal_coin, level_won, current_level

    if goal_coin["collected"]:
        return
    dx = monkey_pos[0] - goal_coin["position"][0]
    dy = monkey_pos[1] - goal_coin["position"][1]
    dz = monkey_pos[2] - goal_coin["position"][2]
    distance = math.sqrt(dx * dx + dy * dy + dz * dz)
    if distance < 40:
        goal_coin["collected"] = True
        level_won = True
        print(f"Level {current_level} completed!")


def keyboardListener(key, x, y):
    global monkey_pos, monkey_angle, monkey_jumping, monkey_jump_velocity
    global game_over, life, score, barrels_dodged, current_level, game_started
    global monkey_invincible, level_won, monkey_on_platform, platform_index
    if key == b'\x1b':
        print("Game exited")
        glutLeaveMainLoop()
        return
    if not game_started:
        if key == b'e':
            current_level = "easy"
            game_started = True
            initialize_game()
        elif key == b'm':
            current_level = "medium"
            game_started = True
            initialize_game()
        elif key == b'h':
            current_level = "hard"
            game_started = True
            initialize_game()
        return

    if level_won:
        if key == b' ':
            if current_level == "easy":
                current_level = "medium"
            elif current_level == "medium":
                current_level = "hard"
            elif current_level == "hard":
                current_level = "win"

            if current_level == "win":
                game_started = False
                current_level = "start"
            else:
                level_won = False
                initialize_game()
        return
    if game_over:
        if key == b'r':
            game_over = False
            initialize_game()
        return

    move_speed = 10
    climb_speed = 8
    margin = 50
    min_boundary = min_bound + margin
    max_boundary = max_bound - margin
    if key == b'x':
        monkey_angle = (monkey_angle + 90) % 360
        return

    on_ladder, current_ladder, ladder_ratio = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])
    if on_ladder:
        if key == b'w':
            if current_ladder:
                start_x, start_y, start_z = current_ladder["start"]
                end_x, end_y, end_z = current_ladder["end"]
                dx = end_x - start_x
                dy = end_y - start_y
                dz = end_z - start_z
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                if length > 0:
                    dx /= length
                    dy /= length
                    dz /= length
                new_ladder_ratio = ladder_ratio + climb_speed / length
                if new_ladder_ratio > 1:
                    new_ladder_ratio = 1
                monkey_pos[0] = start_x + dx * length * new_ladder_ratio
                monkey_pos[1] = start_y + dy * length * new_ladder_ratio
                monkey_pos[2] = start_z + dz * length * new_ladder_ratio
                if new_ladder_ratio >= 0.95:
                    is_platform, idx = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2] + 10)
                    if is_platform:
                        platform = platforms[idx]
                        monkey_pos[2] = platform["position"][2] + platform["height"] / 2 + 25
                        monkey_on_platform = True
                        platform_index = idx

        elif key == b's':
            if current_ladder:
                start_x, start_y, start_z = current_ladder["start"]
                end_x, end_y, end_z = current_ladder["end"]
                dx = end_x - start_x
                dy = end_y - start_y
                dz = end_z - start_z
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                if length > 0:
                    dx /= length
                    dy /= length
                    dz /= length
                new_ladder_ratio = ladder_ratio - climb_speed / length
                if new_ladder_ratio < 0:
                    new_ladder_ratio = 0

                monkey_pos[0] = start_x + dx * length * new_ladder_ratio
                monkey_pos[1] = start_y + dy * length * new_ladder_ratio
                monkey_pos[2] = start_z + dz * length * new_ladder_ratio

                if new_ladder_ratio <= 0.05:
                    if start_z <= 10:
                        monkey_pos[2] = 50
                        monkey_on_platform = False
                        platform_index = -1
                    else:
                        is_platform, idx = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2] - 10)
                        if is_platform:
                            platform = platforms[idx]
                            monkey_pos[2] = platform["position"][2] + platform["height"] / 2 + 25
                            monkey_on_platform = True
                            platform_index = idx

        elif key == b' ':
            monkey_jumping = True
            monkey_jump_velocity = JUMP_VELOCITY * 0.7

        elif key == b'f':
            throw_rock()
        elif key == b'c':
            monkey_invincible = not monkey_invincible
            print(f"Cheat mode: {'ON' if monkey_invincible else 'OFF'}")

        return

    if key == b'w':
        new_x = monkey_pos[0]
        new_y = monkey_pos[1] + move_speed

        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            monkey_pos[0] = new_x
            monkey_pos[1] = new_y
            if monkey_on_platform:
                still_on, _ = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                if not still_on:
                    on_new_ladder, ladder_info, _ = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                    if not on_new_ladder:
                        monkey_jumping = True
                        monkey_jump_velocity = 0

    elif key == b's':
        new_x = monkey_pos[0]
        new_y = monkey_pos[1] - move_speed
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            monkey_pos[0] = new_x
            monkey_pos[1] = new_y
            if monkey_on_platform:
                still_on, _ = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                if not still_on:
                    on_new_ladder, ladder_info, _ = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                    if not on_new_ladder:
                        monkey_jumping = True
                        monkey_jump_velocity = 0

    elif key == b'a':
        new_x = monkey_pos[0] - move_speed
        new_y = monkey_pos[1]
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            monkey_pos[0] = new_x
            monkey_pos[1] = new_y
            if monkey_on_platform:
                still_on, _ = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                if not still_on:
                    on_new_ladder, ladder_info, _ = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                    if not on_new_ladder:
                        monkey_jumping = True
                        monkey_jump_velocity = 0

    elif key == b'd':
        new_x = monkey_pos[0] + move_speed
        new_y = monkey_pos[1]
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            monkey_pos[0] = new_x
            monkey_pos[1] = new_y
            if monkey_on_platform:
                still_on, _ = is_on_platform(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                if not still_on:
                    on_new_ladder, ladder_info, _ = is_on_ladder(monkey_pos[0], monkey_pos[1], monkey_pos[2])
                    if not on_new_ladder:
                        monkey_jumping = True
                        monkey_jump_velocity = 0

    elif key == b' ':
        if not monkey_jumping:
            monkey_jumping = True
            monkey_jump_velocity = JUMP_VELOCITY

    elif key == b'f':
        throw_rock()

    elif key == b'c':
        monkey_invincible = not monkey_invincible
        print(f"Cheat mode: {'ON' if monkey_invincible else 'OFF'}")


def specialKeyListener(key, x, y):
    global camera_pos, monkey_angle

    if game_over or not game_started or level_won:
        return

    cam_x, cam_y, cam_z = camera_pos
    movement = {
        GLUT_KEY_UP: (0, 0, 10),
        GLUT_KEY_DOWN: (0, 0, -10),
        GLUT_KEY_LEFT: (-10, 0, 0),
        GLUT_KEY_RIGHT: (10, 0, 0)
    }
    if key == GLUT_KEY_UP:
        monkey_angle = 0
    elif key == GLUT_KEY_DOWN:
        monkey_angle = 180
    elif key == GLUT_KEY_LEFT:
        monkey_angle = 90
    elif key == GLUT_KEY_RIGHT:
        monkey_angle = 270
    if key in movement:
        dx, dy, dz = movement[key]
        new_z = cam_z + dz
        if new_z >= 50:
            cam_x += dx
            cam_y += dy
            cam_z = new_z

    camera_pos = (cam_x, cam_y, cam_z)


def mouseListener(button, state, x, y):
    global camera_mode, mouse_x, mouse_y
    mouse_x = x
    mouse_y = y

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 950 <= x <= 990 and 20 <= y <= 50:
            print("Exit button clicked")
            glutLeaveMainLoop()
            return

    if game_over or not game_started or level_won:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        throw_rock()

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "first" if camera_mode == "third" else "third"
    glutMotionFunc(mouseMotion)
    glutPassiveMotionFunc(mouseMotion)


def mouseMotion(x, y):
    global mouse_x, mouse_y, monkey_angle, monkey_on_platform
    mouse_x = x
    mouse_y = y
    if not monkey_on_platform and camera_mode == "third":
        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x = viewport[2] / 2
        center_y = viewport[3] / 2
        dx = mouse_x - center_x
        dy = center_y - mouse_y
        if dx != 0 or dy != 0:
            angle_rad = math.atan2(-dx, dy)
            monkey_angle = math.degrees(angle_rad)


def draw_win_screen():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    draw_text_large(350, 700, "CONGRATULATIONS!")
    draw_text_large(400, 650, "YOU WIN!")
    draw_text(400, 550, f"Final Score: {score}")
    draw_text(380, 500, f"Barrels Dodged: {barrels_dodged}")
    draw_text(350, 400, "Press SPACE to return to main menu")
    glPushMatrix()
    glTranslatef(500, 250, 0)
    glScalef(3, 3, 3)
    glColor3f(0.6, 0.4, 0.1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(20 * math.cos(angle), 20 * math.sin(angle))
    glEnd()
    glTranslatef(0, 25, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(15 * math.cos(angle), 15 * math.sin(angle))
    glEnd()
    glColor3f(0.9, 0.7, 0.5)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, -5)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(10 * math.cos(angle), 10 * math.sin(angle) - 5)
    glEnd()
    glColor3f(0, 0, 0)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glVertex2f(-5, 0)
    glVertex2f(5, 0)
    glEnd()

    glBegin(GL_LINE_STRIP)
    for i in range(11):
        angle = i * math.pi / 10
        glVertex2f(8 * math.cos(angle) - 8, 5 * math.sin(angle) - 10)
    glEnd()

    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_level_complete_screen():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    draw_text_large(350, 700, f"LEVEL {current_level.upper()} COMPLETED!")
    draw_text(400, 600, f"Score: {score}")
    draw_text(380, 550, f"Life: {life}")
    draw_text(380, 500, f"Barrels Dodged: {barrels_dodged}")
    draw_text(350, 400, "Press SPACE to continue to next level")
    glPushMatrix()
    glTranslatef(500, 250, 0)
    glRotatef(goal_coin["rotation"], 0, 0, 1)
    glColor3f(1.0, 0.8, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(50 * math.cos(angle), 50 * math.sin(angle))
    glEnd()

    glColor3f(0.8, 0.6, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(50 * math.cos(angle), 50 * math.sin(angle))
    glEnd()

    glBegin(GL_LINE_LOOP)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(35 * math.cos(angle), 35 * math.sin(angle))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(11):
        angle = i * (2 * math.pi / 10)
        r = 20 if i % 2 == 0 else 10
        glVertex2f(r * math.cos(angle), r * math.sin(angle))
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def setupCamera():
    global monkey_pos, camera_pos, lastx, lasty, lastz
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 10 / 8, 0.1, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "third":
        cam_x, cam_y, cam_z = camera_pos
        gluLookAt(
            cam_x, cam_y, cam_z,
            monkey_pos[0], monkey_pos[1], monkey_pos[2],
            0, 0, 1
        )
    else:

        angle_rad = math.radians(monkey_angle)
        look_x = monkey_pos[0] - 100 * math.sin(angle_rad)
        look_y = monkey_pos[1] - 100 * math.cos(angle_rad)
        look_z = monkey_pos[2] + 20

        cam_x = monkey_pos[0]
        cam_y = monkey_pos[1]
        cam_z = monkey_pos[2] + 20

        gluLookAt(
            cam_x, cam_y, cam_z,
            look_x, look_y, look_z,
            0, 0, 1
        )
    lastx, lasty, lastz = monkey_pos


def idle():
    global goal_coin, current_level

    if not game_started or game_over or level_won:
        if current_level == "start":
            goal_coin["rotation"] += 2
        glutPostRedisplay()
        return
    goal_coin["rotation"] += 2
    update_monkey_jump()
    update_barrels()
    update_rocks()
    update_enemies()
    update_shield()
    check_goal_coin()
    if not monkey_jumping:
        update_monkey_position()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    glEnable(GL_DEPTH_TEST)
    if not game_started:
        draw_start_screen()
    elif level_won:
        if current_level == "win":
            draw_win_screen()
        else:
            draw_level_complete_screen()
    else:
        setupCamera()
        draw_grid(GRID_SIZE)
        draw_border_walls()
        draw_platforms()
        draw_ladders()
        draw_goal_coin()
        draw_palm_trees()
        draw_monkey()
        draw_enemies()
        draw_barrels()
        draw_rocks()

        if game_over:
            draw_text(10, 750, f"Game Over! Your score: {score}")
            draw_text(10, 720, "Press 'R' to restart")
        else:
            draw_text(10, 750, f"Life: {life}")
            draw_text(10, 720, f"Score: {score}")
            draw_text(10, 690, f"Barrels Dodged: {barrels_dodged}")
            draw_text(10, 660, f"Level: {current_level.upper()}")

            if monkey_shield:
                remaining = SHIELD_DURATION - (time.time() - shield_start_time)
                draw_text(10, 630, f"Shield Active: {remaining:.1f}s")

            if monkey_invincible:
                draw_text(10, 600, "CHEAT MODE: Invincible")
            draw_text(800, 750, "Controls:")
            draw_text(800, 720, "WASD: Move")
            draw_text(800, 690, "Space: Jump")
            draw_text(800, 660, "Left Mouse: Throw Rock")
            draw_text(800, 630, "Right Mouse: Toggle Camera")
            draw_text(800, 600, "X: Rotate Monkey")
            draw_text(800, 570, "Esc: Exit Game")
    draw_exit_button()

    glutSwapBuffers()


def initialize_game():
    global monkey_pos, monkey_angle, monkey_jumping, monkey_jump_velocity
    global score, life, barrels_dodged, monkey_invincible, monkey_shield
    global monkey_on_platform, platform_index
    monkey_angle = 0
    monkey_jumping = False
    monkey_jump_velocity = 0
    score = 0
    life = 3
    barrels_dodged = 0
    monkey_invincible = False
    monkey_shield = False
    barrels.clear()
    rocks.clear()
    initialize_platforms()
    initialize_enemies()
    place_monkey_random()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Monkey Jax")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()