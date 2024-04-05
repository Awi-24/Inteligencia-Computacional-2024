import pygame
import random
import heapq

# Função heurística para o algoritmo A*
def heuristic(a, b):
    return abs(b[0] - a[0]) + abs(b[1] - a[1])

# Algoritmo A*
def astar(graph, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        current_cost, current = heapq.heappop(frontier)

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + 1  # Assuming all edges have the same cost
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(frontier, (priority, next))
                came_from[next] = current

    path = []
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

class MazeGraph:
    def __init__(self, maze_size, walls):
        self.maze_size = maze_size
        self.walls = set(map(tuple, walls))  # Convertendo as listas em tuplas

    def neighbors(self, pos):
        row, col = pos
        candidates = [(row+1, col), (row-1, col), (row, col+1), (row, col-1)]
        valid_neighbors = []
        for neighbor in candidates:
            if 0 <= neighbor[0] < self.maze_size and 0 <= neighbor[1] < self.maze_size and neighbor not in self.walls:
                valid_neighbors.append(neighbor)
        return valid_neighbors

i = 0
score_list = []
steps_list = []
give_up_list = []
give_up = False
collected_treasures = []

while i < 100:
    pygame.init()

    width, height = 800, 800
    maze_size = 20
    block_size = width // maze_size
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    NUM_TREASURES = 10

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Maze Treasure Hunt')

    treasure_image = pygame.image.load('treasure.png')
    treasure_image = pygame.transform.scale(treasure_image, (block_size, block_size))

    player_pos = [random.randint(0, maze_size - 1), random.randint(0, maze_size - 1)]
    treasures = []
    for _ in range(NUM_TREASURES):
        while True:
            treasure = [random.randint(0, maze_size - 1), random.randint(0, maze_size - 1)]
            if treasure not in treasures and treasure != player_pos:
                treasures.append(treasure)
                break

    def generate_walls():
        walls = []
        for i in range(1, maze_size - 1):
            for j in range(1, maze_size - 1):
                if [i, j] != player_pos and [i, j] not in treasures and random.choice([True, False, False]):
                    walls.append([i, j])
        return walls

    def generate_water(slope):
        water = []
        water_size = min(maze_size, maze_size) // 4
        start_x = random.randint(0, maze_size - water_size)
        start_y = random.randint(0, maze_size - water_size)
        for i in range(start_x, start_x + water_size):
            for j in range(start_y, start_y + water_size):
                water.append([i, j])
        return water

    slope = 0.5
    water = generate_water(slope)
    walls = generate_walls()

    maze_graph = MazeGraph(maze_size, walls)

    running = True
    score = 0
    steps = 0
    while running:
        if treasures:
            treasure_pos = treasures[0]
        else:
            print("All treasures found")
            running = False
            print(steps)
            print(score)
            break

        if steps >= 80:
            running = False
            print(steps)
            print(score)
            print("Max steps exceeded")

        path = astar(maze_graph, tuple(player_pos), tuple(treasure_pos))
        if path and len(path) >= 2:
            next_pos = path[1]
            dx = next_pos[0] - player_pos[0]
            dy = next_pos[1] - player_pos[1]
            if dx == 0 and dy == 1:
                direction = 'DOWN'
            elif dx == 0 and dy == -1:
                direction = 'UP'
            elif dx == 1 and dy == 0:
                direction = 'RIGHT'
            elif dx == -1 and dy == 0:
                direction = 'LEFT'
        else:
            direction = "NONE"

        score -= 1

        next_pos = player_pos
        if direction == 'UP':
            next_pos = (player_pos[0], player_pos[1] - 1)
        elif direction == 'DOWN':
            next_pos = (player_pos[0], player_pos[1] + 1)
        elif direction == 'LEFT':
            next_pos = (player_pos[0] - 1, player_pos[1])
        elif direction == 'RIGHT':
            next_pos = (player_pos[0] + 1, player_pos[1])

        if direction == "NONE":
            print("Giving Up!")
            running = False
            give_up = True
            break

        steps += 1

        px, py = next_pos
        if [px, py] not in walls and 0 <= next_pos[0] < maze_size and 0 <= next_pos[1] < maze_size:
            player_pos = next_pos
        else:
            print("Invalid move!", next_pos)
            continue

        screen.fill(BLACK)
        for row in range(maze_size):
            for col in range(maze_size):
                rect = pygame.Rect(col * block_size, row * block_size, block_size, block_size)
                if [col, row] in walls:
                    pygame.draw.rect(screen, BLACK, rect)
                elif [col, row] in water:
                    pygame.draw.rect(screen, BLUE, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                if [col, row] == [px, py]:
                    pygame.draw.rect(screen, RED, rect)
                elif [col, row] in treasures:
                    pygame.draw.rect(screen, WHITE, rect)
                    screen.blit(treasure_image, (col * block_size, row * block_size))

        if [px, py] in treasures:
            treasures.remove([px, py])
            print("Treasure found! Treasures left:", len(treasures))
            score += 500
            # Atualiza o caminho para o próximo tesouro mais próximo
            if treasures:
                treasure_pos = min(treasures, key=lambda x: abs(x[0] - player_pos[0]) + abs(x[1] - player_pos[1]))
                path = astar(maze_graph, tuple(player_pos), tuple(treasure_pos))

        if [px, py] in water:
            score -= 5
            print("In water! Paying heavier price:", [px, py])

        pygame.display.flip()
        pygame.time.wait(1)


    i += 1
    give_up_list.append(give_up)
    steps_list.append(steps)
    score_list.append(score)
    collected_treasures.append(10 - len(treasures))
    give_up = False

print(steps_list)
print(score_list)
print(give_up_list)
print(collected_treasures)
