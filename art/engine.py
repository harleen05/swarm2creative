import pygame
import random
from noise import pnoise2
import math

ART_STATE = {
    "emotion": "neutral",
    "flow_noise": 0.02,
    "symmetry": 4,
    "motion_intensity": "moderate"
}

FLOW_SCALE = 0.004
FLOW_STRENGTH = 0.25
LAST_FRAME = None
WIDTH = 800
HEIGHT = 600
ART_MODE = "chaos"
EMOTION = "anxiety"
ROTATION_SYMMETRY = 6
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2
current_shape = "spiral"
star_target = None
star_timer = 0
ART_STATE["paused"] = False

FOCAL_POINTS = [
    (WIDTH * 0.25, HEIGHT * 0.35),
    (WIDTH * 0.75, HEIGHT * 0.30),
    (WIDTH * 0.35, HEIGHT * 0.75),
    (WIDTH * 0.70, HEIGHT * 0.70),
]

def update_focal_points(t):
    new_points = []
    speed = 0.3
    radius = 50
    for (x, y) in FOCAL_POINTS:
        nx = x + math.sin(t * speed + x) * radius
        ny = y + math.cos(t * speed + y) * radius
        new_points.append((nx, ny))
    return new_points

NEGATIVE_ZONES = [
    (WIDTH * 0.5, HEIGHT * 0.5, 250),
]

EMOTION_SETTINGS = {
    "calm": {
        "align": 0.05,
        "cohesion": 0.01,
        "separation": 0.06,
        "noise": 0.01
    },
    "anxiety": {
        "align": 0.08,
        "cohesion": 0.0005,
        "separation": 0.3,
        "focal": 0.03,
        "neg": 0.12
    },
    "joy": {
        "align": 0.06,
        "cohesion": 0.01,
        "separation": 0.15,
        "focal": 0.02,
        "neg": 0.02
    }
}

def get_flow_vector(x, y, t):
    angle = pnoise2(x * FLOW_SCALE, y * FLOW_SCALE, repeatx=999999, repeaty=999999, base=int(t)) * 8 * 3.14159
    vec = pygame.Vector2(1, 0).rotate_rad(angle)
    return vec

def get_neighbors(agent, agents, radius):
    neighbors = []
    for other in agents:
        if other is agent:
            continue
        if agent.pos.distance_to(other.pos) < radius:
            neighbors.append(other)
    return neighbors

def alignment(agent, neighbors, strength=0.05):
    if not neighbors:
        return pygame.Vector2(0, 0)

    avg_vel = pygame.Vector2(0, 0)
    for other in neighbors:
        avg_vel += other.vel

    avg_vel /= len(neighbors)

    steer = avg_vel - agent.vel
    steer *= strength
    return steer

def cohesion(agent, neighbors, strength=0.01):
    if not neighbors:
        return pygame.Vector2(0, 0)

    center = pygame.Vector2(0, 0)
    for other in neighbors:
        center += other.pos

    center /= len(neighbors)

    steer = center - agent.pos
    steer *= strength
    return steer

def separation(agent, neighbors, desired_distance=25, strength=0.15):
    if not neighbors:
        return pygame.Vector2(0, 0)

    steer = pygame.Vector2(0, 0)
    total = 0

    for other in neighbors:
        dist = agent.pos.distance_to(other.pos)
        if dist < desired_distance and dist > 0:
            diff = agent.pos - other.pos
            diff /= dist
            steer += diff
            total += 1

    if total > 0:
        steer /= total
        steer *= strength

    return steer

def random_color_palette():
    """Return a palette tuned to the current art mode (chaos/flow/composition)."""
    base_palettes = {
        # chaos / freeform – rich but softer
        "chaos": [
            [(255, 99, 71), (255, 178, 102), (255, 255, 153)],          # warm sunset
            [(102, 178, 255), (0, 102, 204), (0, 51, 102)],             # blue ocean
            [(255, 102, 178), (255, 153, 204), (204, 0, 102)],          # pink neon
            [(102, 255, 178), (0, 153, 102), (0, 204, 153)],            # mint lush
        ],
        # flow / geometric – high-contrast neon
        "flow": [
            [(120, 240, 255), (60, 180, 255), (190, 120, 255)],         # cyan / violet neon
            [(255, 80, 180), (255, 210, 80), (80, 255, 200)],           # magenta / gold / aqua
        ],
        # composition / mandala – deep, saturated
        "composition": [
            [(255, 140, 0), (255, 215, 0), (255, 69, 0)],               # festival
            [(186, 85, 211), (148, 0, 211), (72, 61, 139)],             # deep mandala
        ],
    }

    mode = ART_STATE.get("art_mode", "chaos")
    palettes = base_palettes.get(mode, base_palettes["chaos"])
    import random
    return random.choice(palettes)

def focal_force(agent, strength=0.01, t=0):
    points = update_focal_points(t)
    force = pygame.Vector2(0, 0)
    for (fx, fy) in points:
        point = pygame.Vector2(fx, fy)
        diff = point - agent.pos
        force += diff
    force /= len(points)
    force *= strength
    return force

def negative_space_force(agent, strength=0.08):
    force = pygame.Vector2(0, 0)

    for (nx, ny, r) in NEGATIVE_ZONES:
        center = pygame.Vector2(nx, ny)
        dist = agent.pos.distance_to(center)

        if dist < r:
            diff = agent.pos - center
            if dist != 0:
                diff /= dist
            force += diff

    force *= strength
    return force

def rotate_point(x, y, cx, cy, angle):
    rad = math.radians(angle)
    dx = x - cx
    dy = y - cy

    rx = dx * math.cos(rad) - dy * math.sin(rad)
    ry = dx * math.sin(rad) + dy * math.cos(rad)

    return cx + rx, cy + ry

def shift_color(color, t, emotion):
    r, g, b = color
    # speed per emotion
    if emotion == "calm":
        speed = 0.2
    elif emotion == "joy":
        speed = 0.6
    elif emotion == "anxiety":
        speed = 1.2
    else:
        speed = 0.4
    r = max(0, min(255, r + int(20 * math.sin(t * speed + 0))))
    g = max(0, min(255, g + int(20 * math.sin(t * speed + 2))))
    b = max(0, min(255, b + int(20 * math.sin(t * speed + 4))))
    return (r, g, b)

def shape_force(agent, t, shape):
    cx, cy = CENTER_X, CENTER_Y
    pos = agent.pos
    vec = pygame.Vector2(0, 0)

    if not hasattr(agent, "_shape_mem"):
        agent._shape_mem = {
            "star_target": None,
            "star_timer": 0
        }

    mem = agent._shape_mem

    if shape == "ring":
        # clean orbital ring – tight radius band
        radius = 220 + math.sin(t * 0.4) * 20
        angle = t * 0.8 + pos.x * 0.001
        target = pygame.Vector2(
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius
        )
        vec = target - pos

    elif shape == "spiral":
        # strong outward spiral from center
        r = 40 + t * 30
        angle = t * 0.7 + pos.y * 0.002
        target = pygame.Vector2(
            cx + math.cos(angle) * r,
            cy + math.sin(angle) * r
        )
        vec = target - pos

    elif shape == "petal":
        r_base = 200
        petal_count = 6
        breathing = 20 * math.sin(t * 0.6)

        dx = pos.x - cx
        dy = pos.y - cy
        angle = math.atan2(dy, dx)

        r = r_base + breathing + 60 * math.sin(petal_count * angle)
        target = pygame.Vector2(
            cx + math.cos(angle) * r,
            cy + math.sin(angle) * r
        )
        vec = target - pos

    elif shape == "constellation":
        if mem["star_target"] is None:
            mem["star_target"] = random.choice(FOCAL_POINTS)

        mem["star_timer"] += 1
        if mem["star_timer"] > 180:
            mem["star_target"] = random.choice(FOCAL_POINTS)
            mem["star_timer"] = 0

        target = pygame.Vector2(*mem["star_target"])
        # snap harder toward discrete stars
        vec = (target - pos) * 1.5

    elif shape == "vortex":
        dir_vec = pygame.Vector2(cx, cy) - pos
        if dir_vec.length() > 0:
            dir_vec.rotate_ip(90)
            vec = dir_vec

    elif shape == "orbit":
        radius = 220 + 40 * math.sin(t * 0.4)
        angle = t * 0.6 + (pos.y * 0.002)
        target = pygame.Vector2(
            cx + math.cos(angle) * radius,
            cy + math.sin(angle) * radius
        )
        vec = target - pos

    elif shape == "rays":
        # sharp radial spokes in and out
        angle = math.atan2(pos.y - cy, pos.x - cx)
        step = (2 * math.pi) / ART_STATE.get("symmetry", 8)
        snapped = round(angle / step) * step
        radius = 260 + 40 * math.sin(t * 0.9)
        target = pygame.Vector2(
            cx + math.cos(snapped) * radius,
            cy + math.sin(snapped) * radius
        )
        vec = target - pos

    else:
        vec = pygame.Vector2(0, 0)
        
    # scale differently for stronger shapes
    strength = 0.005
    if shape in ("spiral", "rays"):
        strength = 0.007
    if shape == "orbit":
        strength = 0.004

    return vec * strength

class Agent:
    def __init__(self):
        self.pos = pygame.Vector2(
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT)
        )
        self.vel = pygame.Vector2(
            random.uniform(-2, 2),
            random.uniform(-2, 2)
        )
        self.color_palette = random_color_palette()
        self.color = random.choice(self.color_palette)
        self.color_index = 0
        self.history = []

    def update(self):
        self.pos += self.vel
        if self.vel.length() > 0:
            self.vel = self.vel.lerp(self.vel.normalize(), 0.1)
        if self.vel.length() > 1.2:
            self.vel.scale_to_length(1.2)
        self.edges()
        self.history.append(self.pos.copy())

        # longer, denser trails for mandala / geometric
        mode = ART_STATE.get("art_mode", "chaos")
        if mode == "composition":
            max_len = 260
        elif mode == "flow":
            max_len = 180
        else:
            max_len = 120
        if len(self.history) > max_len:
            self.history.pop(0)
        self.color_index = (self.color_index + 0.02) % len(self.color_palette)
        self.color = self.color_palette[int(self.color_index)]

    def edges(self):
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = WIDTH
        if self.pos.y > HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = HEIGHT

    def draw(self, screen, time):
        for p in self.history:
            pygame.draw.circle(
                screen,
                self.color,
                (int(p.x), int(p.y)),
                2
            )
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.pos.x), int(self.pos.y)),
            3
        )
        angle_step = 360 / ROTATION_SYMMETRY
        for i in range(1, ROTATION_SYMMETRY):
            angle = angle_step * i
            rx, ry = rotate_point(self.pos.x, self.pos.y, CENTER_X, CENTER_Y, angle)
            pygame.draw.circle(screen, self.color, (int(rx), int(ry)), 3)
        hx = WIDTH - self.pos.x
        hy = self.pos.y
        pygame.draw.circle(screen, self.color, (int(hx), int(hy)), 2)
        vx = self.pos.x
        vy = HEIGHT - self.pos.y
        pygame.draw.circle(screen, self.color, (int(vx), int(vy)), 2)
        dx = WIDTH - self.pos.x
        dy = HEIGHT - self.pos.y
        pygame.draw.circle(screen, self.color, (int(dx), int(dy)), 2)
    
    def apply_behaviors(self, agents, time, state, pattern_stable=False):
        ART_MODE = state.get("art_mode", "calm")

        EMOTION = state.get("emotion", "calm")
        FLOW_STRENGTH = state.get("flow_noise", 0.02)
        SHAPE = state.get("shape", "freeform")

        neighbors = get_neighbors(self, agents, 60)
        if ART_MODE == "calm":
            align_force = alignment(self, neighbors, 0.04)
            cohesion_force = cohesion(self, neighbors, 0.003)
            separation_force = separation(self, neighbors, 25, 0.12)

        elif  ART_MODE == "chaos":
            perp = pygame.Vector2(-self.vel.y, self.vel.x)
            if perp.length() > 0:
                perp = perp.normalize()
            self.vel += perp * 0.08

            # entropy burst
            self.vel += pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ) * 0.05

        elif ART_MODE == "galaxy":
            align_force = alignment(self, neighbors, 0.03)
            cohesion_force = cohesion(self, neighbors, 0.005)
            separation_force = separation(self, neighbors, 30, 0.1)

        else:
            align_force = cohesion_force = separation_force = pygame.Vector2(0,0)

        if ART_MODE == "flow":  
            to_center = pygame.Vector2(CENTER_X, CENTER_Y) - self.pos
            if to_center.length() > 0:
                tangent = pygame.Vector2(-to_center.y, to_center.x).normalize()
                self.vel += tangent * 0.08
            self.vel += to_center * 0.0006
            jitter = pygame.Vector2(
                random.uniform(-0.3, 0.3),
                random.uniform(-0.3, 0.3)
            )
            self.vel += jitter * 0.03

        if ART_MODE == "composition":
            dx = self.pos.x - CENTER_X
            dy = self.pos.y - CENTER_Y
            angle = math.atan2(dy, dx)
            step = (2 * math.pi) / state.get("symmetry", 6)
            snapped = round(angle / step) * step
            target = pygame.Vector2(
                CENTER_X + math.cos(snapped) * 220,
                CENTER_Y + math.sin(snapped) * 220
            )
            self.vel += (target - self.pos) * 0.002
            to_center = pygame.Vector2(CENTER_X, CENTER_Y) - self.pos
            self.vel += to_center * 0.0008
            
        if pattern_stable:
            self.pos += pygame.Vector2(
                math.sin(time * 0.2) * 0.2,
                math.cos(time * 0.2) * 0.2
            )
        else:
            self.vel += shape_force(self, time, SHAPE)

def get_frame_state(agents):
    return {
        "agents": [
            {
                "x": a.pos.x,
                "y": a.pos.y,
                "color": a.color,
                "trail": [(p.x, p.y) for p in a.history]
            }
            for a in agents
        ],
        "meta": {
            "emotion": ART_STATE.get("emotion"),
            "symmetry": ART_STATE.get("symmetry"),
            "flow_noise": ART_STATE.get("flow_noise"),
            "art_mode": ART_STATE.get("art_mode")
        }
    }