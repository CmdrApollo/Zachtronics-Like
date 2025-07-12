import pygame
import math

pygame.init()

FONT = pygame.font.SysFont("Courier", 16)

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

try:
    joystick = pygame.joystick.Joystick(0)
except pygame.error:
    joystick = None

TILESIZE = 48

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(a, minv, maxv):
    return min(max(minv, a), maxv)

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
    name = "Conveyor"
    def __init__(self, x, y, direction=Direction.EAST):
        self.x = x
        self.y = y
        self.direction = direction

    def convert(self, item):
        return item.name

    def draw(self, win, ox, oy, alpha=255):
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
                                ], 1)
        
        s.set_alpha(alpha)

        win.blit(pygame.transform.rotate(s, -90 * self.direction), (ox + self.x * TILESIZE, oy + self.y * TILESIZE))

class Smelter(Conveyor):
    name = "Smelter"
    def __init__(self, x, y, direction=Direction.EAST):
        super().__init__(x, y, direction)

    def convert(self, item):
        if item.name == "ore":
            return "bar"
        return item.name

    def draw(self, win, ox, oy, alpha=255):
        t = (pygame.time.get_ticks() // 500) % 3
        t = 2 - t

        s = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)

        pygame.draw.rect(s, '#404040', (0, 0, TILESIZE, TILESIZE), 0)
        
        for i in range(3):
            pygame.draw.polygon(s, '#C00000' if t == i else "#800000", 
                                [
                                    (6, 12 + i * (TILESIZE // 4)),
                                    (TILESIZE // 2, 6 + i * (TILESIZE // 4)),
                                    (TILESIZE - 6, 12 + i * (TILESIZE // 4))
                                ], 1)
        
        s.set_alpha(alpha)

        win.blit(pygame.transform.rotate(s, -90 * self.direction), (ox + self.x * TILESIZE, oy + self.y * TILESIZE))

class Item:
    def __init__(self, name, x, y):
        self.name = name
        self.x = self.draw_x = x
        self.y = self.draw_y = y
    
    def draw(self, win, ox, oy, t):
        match self.name:
            case "ore":
                pygame.draw.circle(win, 'white', (ox + lerp(self.draw_x, self.x, 1 - t) * TILESIZE + TILESIZE // 2, oy + lerp(self.draw_y, self.y, 1 - t) * TILESIZE + TILESIZE // 2), TILESIZE // 2 - 5, 1)
            case "bar":
                pygame.draw.rect(win, 'white', (ox + lerp(self.draw_x, self.x, 1 - t) * TILESIZE + 5, oy + lerp(self.draw_y, self.y, 1 - t) * TILESIZE + 5, TILESIZE - 10, TILESIZE - 10), 1)

def main():
    clock = pygame.time.Clock()
    delta = 0.0

    cursor_x = 0
    cursor_y = 0
    rotation = Direction.NORTH

    level = {
        "world_size": (8, 8),
        "inputs": [
            {
                "x": 0,
                "y": 0,
                "every": 2,
                "current": 0,
                "item": "ore"
            }
        ]
    }

    world_size = level["world_size"]
    world = [[None for _ in range(world_size[0])] for _ in range(world_size[1])]
    items = []
    inputs = level["inputs"]

    menu_tiles = [Conveyor, Smelter]
    selected_tile = 0
    held_tile = menu_tiles[selected_tile]

    timer = 1 / 3

    factory_running = False

    placing = True
    removing = False

    run = True
    while run:
        delta = clock.tick_busy_loop(60.0) / 1000.0

        timer -= delta

        if timer < 0:
            timer += 1 / 3

            if factory_running:
                # inputs
                for i in inputs:
                    i["current"] += 1
                    if i["current"] == i["every"]:
                        i["current"] = 0
                        
                        add = True
                        for item in items:
                            if item.x == i["x"] and item.y == i["y"]:
                                add = False
                                break

                        if add:
                            items.append(Item(i["item"], i["x"], i["y"]))

                # update item positions
                for item in items[::-1]:
                    item.draw_x, item.draw_y = item.x, item.y

                    tile = world[item.y][item.x]
                    if isinstance(tile, Conveyor):
                        f = flow[tile.direction]
                        ix = item.x
                        iy = item.y
                        item.x = clamp(item.x + f[0], 0, world_size[0] - 1)
                        item.y = clamp(item.y + f[1], 0, world_size[1] - 1)
                        
                        for other in items:
                            if other == item:
                                continue

                            if item.x == other.x and item.y == other.y:
                                item.x = ix
                                item.y = iy
                                break

                        item.name = tile.convert(item)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 11:
                    if placing or removing:
                        cursor_y = max(0, cursor_y - 1)
                elif event.button == 12:
                    if placing or removing:
                        cursor_y = min(world_size[1] - 1, cursor_y + 1)
                elif event.button == 13:
                    if placing or removing:
                        cursor_x = max(0, cursor_x - 1)
                    else:
                        selected_tile = max(0, selected_tile - 1)
                elif event.button == 14:
                    if placing or removing:
                        cursor_x = min(world_size[0] - 1, cursor_x + 1)
                    else:
                        selected_tile = min(len(menu_tiles) - 1, selected_tile + 1)
                elif event.button == 0:
                    # xbox A / place
                    if placing:
                        if not world[cursor_y][cursor_x]:
                            world[cursor_y][cursor_x] = held_tile(cursor_x, cursor_y, rotation)
                    elif removing:
                        world[cursor_y][cursor_x] = None
                    else:
                        held_tile = menu_tiles[selected_tile]
                        placing = True
                elif event.button == 1:
                    # xbox B / cancel
                    if placing or removing:
                        placing = False
                        removing = False
                    else:
                        # enter menu
                        pass
                elif event.button == 2:
                    # xbox X / remove
                    placing = False
                    removing = True
                elif event.button == 6:
                    # start / start & stop factory
                    items = []
                    factory_running = not factory_running
                elif event.button == 9:
                    # left bumper / rotate
                    if placing:
                        rotation -= 1
                        if rotation < 0: rotation += 4
                elif event.button == 10:
                    # right bumper / rotate
                    if placing:
                        rotation = (rotation + 1) % 4
                else:
                    print(event.button)
        
        screen.fill('#202020')

        ox, oy = WIDTH // 2 - (TILESIZE * world_size[0]) // 2, 5

        for i in range(world_size[0]):
            for j in range(world_size[1]):
                if world[j][i]:
                    world[j][i].draw(screen, ox, oy)

        for item in items:
            item.draw(screen, ox, oy, timer * 3)

        pygame.draw.rect(screen, 'green' if factory_running else 'white', (ox, oy, TILESIZE * world_size[0], TILESIZE * world_size[1]), 1)

        if placing or removing:
            if placing:
                held_tile(cursor_x, cursor_y, rotation).draw(screen, ox, oy, 127)
            
            pygame.draw.rect(screen, 'yellow', (ox + cursor_x * TILESIZE, oy + cursor_y * TILESIZE, TILESIZE, TILESIZE), 2)
        else:
            for i, tile in enumerate(menu_tiles):
                tx = WIDTH // 2 - ((TILESIZE + 10) * len(menu_tiles)) // 2 + i * (TILESIZE + 10) + 5

                obj = tile(0, 0, 0)
                obj.draw(screen, tx, HEIGHT - TILESIZE - 5, 192)
                if i == selected_tile:
                    pygame.draw.rect(screen, 'white', (tx, HEIGHT - TILESIZE - 5, TILESIZE, TILESIZE), 1)
                    screen.blit(t := FONT.render(obj.name, True, 'white'), (tx, HEIGHT - TILESIZE - t.get_height() - 5))

        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()