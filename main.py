import pygame
import math

pygame.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

try:
    joystick = pygame.joystick.Joystick(0)
except pygame.error:
    joystick = None

TILESIZE = 48

class Direction:
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

flow = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0)
}

class Conveyor:
    def __init__(self, x, y, direction=Direction.EAST):
        self.x = x
        self.y = y
        self.direction = direction

    def draw(self, win, alpha=255):
        t = (pygame.time.get_ticks() // 500) % 3
        t = 2 - t

        s = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)

        pygame.draw.rect(s, '#404040', (0, 0, TILESIZE, TILESIZE), 0)
        
        for i in range(3):
            pygame.draw.polygon(s, '#C0C000' if t == i else "#808000", 
                                [
                                    (6, 12 + i * (TILESIZE // 4)),
                                    (TILESIZE // 2, 6 + i * (TILESIZE // 4)),
                                    (TILESIZE - 6, 12 + i * (TILESIZE // 4))
                                ])
        
        s.set_alpha(alpha)

        win.blit(pygame.transform.rotate(s, -90 * self.direction), (self.x * TILESIZE, self.y * TILESIZE))

def main():
    clock = pygame.time.Clock()
    delta = 0.0

    cursor_x = 0
    cursor_y = 0
    rotation = Direction.NORTH

    world_size = (8, 8)

    world = [[None for _ in range(world_size[0])] for _ in range(world_size[1])]

    held_tile = Conveyor

    run = True
    while run:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 11: cursor_y = max(0, cursor_y - 1)
                elif event.button == 12: cursor_y = min(world_size[1] - 1, cursor_y + 1)
                elif event.button == 13: cursor_x = max(0, cursor_x - 1)
                elif event.button == 14: cursor_x = min(world_size[0] - 1, cursor_x + 1)
                elif event.button == 0:
                    # xbox A / place
                    if not world[cursor_y][cursor_x]:
                        world[cursor_y][cursor_x] = held_tile(cursor_x, cursor_y, rotation)
                elif event.button == 10:
                    # right bumper / rotate
                    rotation = (rotation + 1) % 4
                else:
                    print(event.button)
        
        screen.fill('#202020')

        for i in range(world_size[0]):
            for j in range(world_size[1]):
                if world[j][i]:
                    world[j][i].draw(screen)

        held_tile(cursor_x, cursor_y, rotation).draw(screen, 127)
        pygame.draw.rect(screen, 'yellow', (cursor_x * TILESIZE, cursor_y * TILESIZE, TILESIZE, TILESIZE), 2)

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()