import pygame
from engine import Agent, WIDTH, HEIGHT, ARCHITECTURE_MODE, prune_dead_rooms
import engine

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swarm Engine - Architecture Emergence")
clock = pygame.time.Clock()
architecture_surface = None
ANCHOR_THRESHOLD = 12
agents = [Agent() for _ in range(50)]
ARCHITECTURE_COMMITTED = False
ARCH_TIME = pygame.time.get_ticks()
running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                engine.export_architecture(agents)

    if not ARCHITECTURE_COMMITTED:
        for agent in agents:
            agent.apply_behaviors(agents)
            agent.update(agents)

        anchor_count = sum(1 for a in agents if a.is_anchor)

        if anchor_count >= ANCHOR_THRESHOLD and not ARCHITECTURE_COMMITTED:
            ARCHITECTURE_COMMITTED = True

            engine.commit_architecture(agents)
            architecture_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            engine.draw_architecture(architecture_surface)

            engine.ARCHITECTURE_MODE = True
            ARCH_TIME = pygame.time.get_ticks()
            print("🏛 Architecture committed → circulation started")

    else:
        for agent in agents:
            agent.apply_behaviors(agents)
            agent.update(agents)

        if architecture_surface:
            screen.blit(architecture_surface, (0, 0))
    
    if (
        engine.ARCHITECTURE_MODE
        and pygame.time.get_ticks() - ARCH_TIME > 10000
        and pygame.time.get_ticks() % 3000 < 16
    ):
        engine.prune_dead_rooms(min_hits=120)
        architecture_surface.fill((0,0,0,0))
        engine.draw_architecture(architecture_surface)

    for agent in agents:
        agent.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()