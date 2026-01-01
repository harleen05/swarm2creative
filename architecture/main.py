import pygame
from engine import Agent, WIDTH, HEIGHT
import engine

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Swarm Engine - Basic Movement")
clock = pygame.time.Clock()
SHOW_STRUCTURE = False

agents = [Agent() for _ in range(50)]

running = True
while running:
    if not SHOW_STRUCTURE:
        screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                from engine import export_architecture
                export_architecture(agents)

            if event.key == pygame.K_l:
                SHOW_STRUCTURE = not SHOW_STRUCTURE
                print("Architecture Mode:", SHOW_STRUCTURE)

    for agent in agents:
        agent.apply_behaviors(agents)
        agent.update()
        agent.draw(screen)

    if SHOW_STRUCTURE:
        engine.draw_architecture(screen, agents)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()