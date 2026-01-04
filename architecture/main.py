import pygame
from engine import Agent, WIDTH, HEIGHT
import engine

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swarm Engine - Architecture Emergence")
clock = pygame.time.Clock()

ANCHOR_THRESHOLD = 6
ARCHITECTURE_MODE = False

agents = [Agent() for _ in range(50)]

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                engine.export_architecture(agents)

    if not ARCHITECTURE_MODE:
        for agent in agents:
            agent.apply_behaviors(agents)
            agent.update()
        anchor_count = sum(1 for a in agents if a.is_anchor)
        if anchor_count >= ANCHOR_THRESHOLD and not ARCHITECTURE_MODE:
            ARCHITECTURE_MODE = True
            engine.commit_architecture(agents)
            print("🏛 Architecture committed")

    else:
        for agent in agents:
            agent.update()
        if ARCHITECTURE_MODE:
            engine.draw_architecture(screen)
    for agent in agents:
        agent.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
