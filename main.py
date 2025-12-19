import pygame
import math

pygame.init()

# --- Window Setup ---
display_info = pygame.display.Info()
WIDTH, HEIGHT = display_info.current_w, display_info.current_h

UI_WIDTH = 320  # how much space the sidebar takes
DEMO_WIDTH = WIDTH - UI_WIDTH  # the demo area width

# set up the window
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Linear Transformations Demo")

# fonts for UI and titles
font = pygame.font.SysFont("consolas", 20)
title_font = pygame.font.SysFont("consolas", 22, bold=True)
button_font = pygame.font.SysFont("consolas", 18)

# --- Sprite (Square) ---
# starting square coordinates relative to center
sprite = [
    [-50, -50],
    [50, -50],
    [50, 50],
    [-50, 50]
]

# --- Transformation State ---
scale_factor = 1.0  # scaling multiplier
angle = 0           # rotation angle in radians
shear_k = 0.0       # shear amount (skew)
tx, ty = 0, 0       # translation (movement)
clock = pygame.time.Clock()  # for timing frame updates

# ---------------------------------------
# Matrix & Transform Helpers
# ---------------------------------------

# basic 2x2 matrix multiplication for a single point
def apply_matrix(point, matrix):
    x, y = point
    # x' = a*x + b*y, y' = c*x + d*y
    return [
        matrix[0][0]*x + matrix[0][1]*y,
        matrix[1][0]*x + matrix[1][1]*y
    ]

# rotate points around origin
def rotate(points, theta):
    # rotation matrix: [[cos -sin],[sin cos]]
    R = [
        [math.cos(theta), -math.sin(theta)],
        [math.sin(theta), math.cos(theta)]
    ]
    # apply rotation to all points
    return [apply_matrix(p, R) for p in points], R

# scale points from origin
def scale(points, factor):
    S = [
        [factor, 0],
        [0, factor]
    ]
    return [apply_matrix(p, S) for p in points], S

# shear (skew) in x direction
def shear(points, k):
    Sh = [
        [1, k],
        [0, 1]
    ]
    return [apply_matrix(p, Sh) for p in points], Sh

# move points by tx, ty
def translate(points, tx, ty):
    return [[x + tx, y + ty] for x, y in points]

# multiply two 2x2 matrices (for combined transform)
def multiply_matrices(A, B):
    return [
        [
            A[0][0]*B[0][0] + A[0][1]*B[1][0],
            A[0][0]*B[0][1] + A[0][1]*B[1][1],
        ],
        [
            A[1][0]*B[0][0] + A[1][1]*B[1][0],
            A[1][0]*B[0][1] + A[1][1]*B[1][1],
        ]
    ]

# ---------------------------------------
# Drawing
# ---------------------------------------

# grid in the demo area
def draw_grid():
    grid_color = (60, 60, 60)
    spacing = 50
    # vertical lines
    for x in range(0, DEMO_WIDTH, spacing):
        pygame.draw.line(win, grid_color, (x, 0), (x, HEIGHT))
    # horizontal lines
    for y in range(0, HEIGHT, spacing):
        pygame.draw.line(win, grid_color, (0, y), (DEMO_WIDTH, y))

# snap center of the demo area to nearest grid intersection
def get_snapped_center():
    spacing = 50
    cx = DEMO_WIDTH // 2
    cy = HEIGHT // 2
    cx -= cx % spacing
    cy -= cy % spacing
    return cx, cy

# draw the polygon (sprite)
def draw_polygon(points, color):
    cx, cy = get_snapped_center()
    # offset points so the square is centered on the grid
    pts = [(x + cx, y + cy) for x, y in points]
    pygame.draw.polygon(win, color, pts, 2)

# draw a 2x2 matrix nicely
def draw_matrix(matrix, x, y, title):
    title_surf = title_font.render(title, True, (160, 200, 255))
    win.blit(title_surf, (x, y))
    y += 32
    for i in range(2):
        # show values rounded to 2 decimals
        row = f"[ {matrix[i][0]:.2f}   {matrix[i][1]:.2f} ]"
        surf = font.render(row, True, (255,255,255))
        win.blit(surf, (x, y))
        y += 24

# ---------------------------------------
# Reset Button
# ---------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action

    def draw(self):
        # button background
        pygame.draw.rect(win, (70, 70, 70), self.rect)
        pygame.draw.rect(win, (255,255,255), self.rect, 2)
        txt = button_font.render(self.text, True, (255,255,255))
        win.blit(txt, txt.get_rect(center=self.rect.center))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

# resets all transform states to default
def reset():
    global scale_factor, angle, shear_k, tx, ty
    scale_factor = 1.0
    angle = 0
    shear_k = 0
    tx = 0
    ty = 0

reset_button = Button(DEMO_WIDTH + 20, 40, UI_WIDTH - 40, 35, "Reset (R)", reset)

# ---------------------------------------
# Instructions on sidebar
# ---------------------------------------
def draw_instructions():
    x = DEMO_WIDTH + 20
    y = 460

    # title
    title = title_font.render("Controls:", True, (160,200,255))
    win.blit(title, (x, y))
    y += 35

    # actual key controls
    lines = [
        "Arrow Keys: Rotate / Scale",
        "Q / E: Shear",
        "WASD: Move",
        "R: Reset",
        "",
        "Esc: Quit"
    ]
    for line in lines:
        surf = font.render(line, True, (255,255,255))
        win.blit(surf, (x, y))
        y += 22

# ---------------------------------------
# MAIN LOOP
# ---------------------------------------
running = True
while running:
    dt = clock.tick(60)/1000  # delta time so movement is smooth

    win.fill((25,25,25))  # clear screen

    draw_grid()  # grid lines
    pygame.draw.rect(win, (35, 35, 35), (DEMO_WIDTH, 0, UI_WIDTH, HEIGHT))  # sidebar bg

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            reset_button.click(pygame.mouse.get_pos())

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # --- controls ---
    if keys[pygame.K_LEFT]: angle -= 2*dt   # rotate left
    if keys[pygame.K_RIGHT]: angle += 2*dt  # rotate right
    if keys[pygame.K_UP]: scale_factor += 0.5*dt
    if keys[pygame.K_DOWN]: scale_factor = max(0.2, scale_factor - 0.5*dt)
    if keys[pygame.K_q]: shear_k -= dt
    if keys[pygame.K_e]: shear_k += dt

    speed = 200
    if keys[pygame.K_w]: ty -= speed*dt
    if keys[pygame.K_s]: ty += speed*dt
    if keys[pygame.K_a]: tx -= speed*dt
    if keys[pygame.K_d]: tx += speed*dt
    if keys[pygame.K_r]: reset()  # reset all

    # --- transformation pipeline ---
    # scale -> shear -> rotate -> translate
    scaled, S = scale(sprite, scale_factor)
    sheared, Sh = shear(scaled, shear_k)
    rotated, R = rotate(sheared, angle)
    transformed = translate(rotated, tx, ty)

    # combined matrix = R * Sh * S
    RS = multiply_matrices(R, Sh)
    M = multiply_matrices(RS, S)

    # --- draw shapes ---
    draw_polygon(sprite, (180, 80, 80))          # original
    draw_polygon(transformed, (100, 255, 255))  # transformed

    # --- draw UI ---
    reset_button.draw()

    draw_matrix(S, DEMO_WIDTH + 20, 100, "Scale:")
    draw_matrix(Sh, DEMO_WIDTH + 20, 190, "Shear:")
    draw_matrix(R, DEMO_WIDTH + 20, 280, "Rotation:")
    draw_matrix(M, DEMO_WIDTH + 20, 370, "Combined:")

    draw_instructions()

    pygame.display.update()

pygame.quit()
