import pygame
import random
import json

WIDTH = 800
HEIGHT = 600
SHOW_STRUCTURE = False
STRUCTURAL_EDGES = set()
ARCHITECTURE_MODE = False

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

def export_architecture(agents):
    data = {
        "points": [],
        "width": WIDTH,
        "height": HEIGHT
    }
    for agent in agents:
        data["points"].extend(agent.path)
    with open("architecture_paths.json", "w") as f:
        json.dump(data, f, indent=4)
    print("🏛 Exported → architecture_paths.json")
    
def draw_architecture(screen):
    xs = [c.x for c in ARCHITECTURE["columns"]]
    if len(xs) >= 2:
        left = min(xs)
        right = max(xs)

        for y in ARCHITECTURE["floors"]:
            pygame.draw.line(
                screen,
                (180,180,200),
                (int(left), int(y)),
                (int(right), int(y)),
                4
            )

    for c in ARCHITECTURE["primary_columns"]:
        pygame.draw.rect(
            screen,
            (210,210,225),
            pygame.Rect(int(c.x-8), int(c.y-180), 16, 360)
        )

    for c in ARCHITECTURE["secondary_columns"]:
        pygame.draw.rect(
            screen,
            (170,170,190),
            pygame.Rect(int(c.x-4), int(c.y-140), 8, 280)
        )
    cols = ARCHITECTURE["primary_columns"]
    for i in range(len(cols)-1):
        c1 = cols[i]
        c2 = cols[i+1]
        for y in ARCHITECTURE["floors"]:
            pygame.draw.line(
                screen,
                (190,190,210),
                (int(c1.x), int(y)),
                (int(c2.x), int(y)),
                3
            )
    core = ARCHITECTURE.get("core")
    if core:
        pygame.draw.rect(
            screen,
            (160,160,180),
            pygame.Rect(
                int(core.x - 18),
                int(HEIGHT * 0.2),
                36,
                int(HEIGHT * 0.6)
            )
        )

    for p1, p2 in ARCHITECTURE["beams"]:
        pygame.draw.line(
            screen,
            (200,200,220),
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)),
            3
        )

def detect_columns(agents, speed_threshold=0.6, min_count=4):
    columns = []
    for a in agents:
        if a.vel.length() < speed_threshold:
            nearby = [
                b for b in agents
                if a.pos.distance_to(b.pos) < 25 and b.vel.length() < speed_threshold
            ]
            if len(nearby) >= min_count:
                columns.append(a.pos)
    return columns

def anchor_repulsion(agent, agents, radius=80, strength=0.6):
    force = pygame.Vector2(0,0)
    for other in agents:
        if other is agent:
            continue
        if other.is_anchor:
            d = agent.pos.distance_to(other.pos)
            if d < radius and d > 0:
                diff = agent.pos - other.pos
                diff.normalize_ip()
                force += diff * (strength / d)
    return force

def too_close_to_anchor(agent, agents, min_dist=120):
    for other in agents:
        if other.is_anchor and agent.pos.distance_to(other.pos) < min_dist:
            return True
    return False

ARCHITECTURE = {
    "columns": [],
    "primary_columns": [],
    "secondary_columns": [],
    "floors": [],
    "beams": [],
    "core": None
}

def cluster_columns(columns, radius=60):
    clusters = []
    for c in columns:
        placed = False
        for cl in clusters:
            if c.distance_to(cl[0]) < radius:
                cl.append(c)
                placed = True
                break
        if not placed:
            clusters.append([c])
    return clusters

def commit_architecture(agents):
    for a in agents:
        if a.is_anchor:
            raw_columns = [pygame.Vector2(a.pos.x, a.pos.y) for a in agents if a.is_anchor]
            column_clusters = cluster_columns(raw_columns)

            ARCHITECTURE["columns"] = [
                sum(cluster, pygame.Vector2(0,0)) / len(cluster)
                for cluster in column_clusters
            ]

    for c in ARCHITECTURE["columns"]:
        if c.y > HEIGHT * 0.4:
            ARCHITECTURE["primary_columns"].append(c)
        else:
            ARCHITECTURE["secondary_columns"].append(c)
    
    ys = [a.pos.y for a in agents]
    ys.sort()
    
    if ARCHITECTURE["primary_columns"]:
        cx = WIDTH / 2
        core = min(
            ARCHITECTURE["primary_columns"],
            key=lambda c: abs(c.x - cx)
        )
        ARCHITECTURE["core"] = core

    levels = []
    for y in ys:
        if not any(abs(y - l) < 25 for l in levels):
            levels.append(y)
    for y in levels[:4]:
        ARCHITECTURE["floors"].append(y)
    cols = ARCHITECTURE["columns"]
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            if abs(cols[i].y - cols[j].y) < 40:
                ARCHITECTURE["beams"].append((cols[i], cols[j]))

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
        self.path = []
        self.arch_path = []
        self.is_anchor = False

    def update(self, agents):
        self.pos += self.vel
        if self.vel.length() > 4:
            self.vel.scale_to_length(4)
        self.edges()
        self.path.append((self.pos.x, self.pos.y))
        if len(self.path) > 500:
            self.path.pop(0)
        self.arch_path.append(self.pos.copy())
        if len(self.arch_path) > 400:
            self.arch_path.pop(0)
        if (
            not self.is_anchor and
            self.vel.length() < 0.25 and
            len(self.path) > 200
        ):
            self.is_anchor = True
            self.vel *= 0
        if (
            not self.is_anchor and
            self.vel.length() < 0.25 and
            len(self.path) > 200 and
            not too_close_to_anchor(self, agents)
        ):
            self.is_anchor = True
            self.vel *= 0

    def edges(self):
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = WIDTH
        if self.pos.y > HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = HEIGHT

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.pos.x), int(self.pos.y)), 4)
    
    def apply_behaviors(self, agents):
        if ARCHITECTURE_MODE:
            self.vel *= 0.92
            return

        if self.is_anchor:
            self.vel *= 0
            return

        neighbors = get_neighbors(self, agents, 60)
        self.vel += alignment(self, neighbors)
        self.vel += cohesion(self, neighbors)
        self.vel += separation(self, neighbors)
        for other in agents:
            if other.is_anchor:
                d = self.pos.distance_to(other.pos)
                if 0 < d < 120:
                    diff = self.pos - other.pos
                    diff.normalize_ip()
                    self.vel += diff * (0.3 / d)