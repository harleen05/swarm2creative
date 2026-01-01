import pygame
import random
import json

WIDTH = 800
HEIGHT = 600
SHOW_STRUCTURE = False

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

    def update(self):
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

    def edges(self):
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.x < 0: self.pos.x = WIDTH
        if self.pos.y > HEIGHT: self.pos.y = 0
        if self.pos.y < 0: self.pos.y = HEIGHT

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.pos.x), int(self.pos.y)), 4)
    
    def apply_behaviors(self, agents):
        neighbors = get_neighbors(self, agents, 60)
        align_force = alignment(self, neighbors)
        cohesion_force = cohesion(self, neighbors)
        separation_force = separation(self, neighbors)
        self.vel += align_force
        self.vel += cohesion_force
        self.vel += separation_force

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
    
def draw_architecture(screen, agents):
    for agent in agents:
        pts = agent.arch_path
        if len(pts) < 10:
            continue

        # 1️⃣ Reduce clutter drastically
        simplified = pts[::10]

        # 2️⃣ Smooth using midpoint curve
        smooth = []
        for i in range(len(simplified)-1):
            p1 = simplified[i]
            p2 = simplified[i+1]
            mid = (p1 + p2) / 2
            smooth.append(p1)
            smooth.append(mid)

        # 3️⃣ Draw elegant structural beams
        for i in range(len(smooth)-1):
            p1 = smooth[i]
            p2 = smooth[i+1]

            thickness = max(1, int(i / 40))
            color = (200, 200, 220)

            pygame.draw.line(
                screen,
                color,
                (int(p1.x), int(p1.y)),
                (int(p2.x), int(p2.y)),
                thickness
            )