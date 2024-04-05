import pygame
import random

i = 0
score_list = []
steps_list = []
give_up_list = []
give_up = False
collected_treasures = []

while i < 600:

    # Initialize Pygame
    pygame.init()

    # Maze dimensions
    width, height = 800, 800
    maze_size = 20  # Adjust for a more complex maze
    block_size = width // maze_size

    # Define colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    NUM_TREASURES = 10

    # Set up the display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Maze Treasure Hunt')

    # Load treasure image
    treasure_image = pygame.image.load('treasure.png')
    treasure_image = pygame.transform.scale(treasure_image, (block_size, block_size))

    # Player and treasures
    player_pos = [random.randint(0, maze_size - 1), random.randint(0, maze_size - 1)]
    treasures = []
    for _ in range(NUM_TREASURES):  # Number of treasures
        while True:
            treasure = [random.randint(0, maze_size - 1), random.randint(0, maze_size - 1)]
            if treasure not in treasures and treasure != player_pos:
                treasures.append(treasure)
                break

    # Generating walls and obstacles dynamically
    def generate_walls():
        walls = []
        for i in range(1, maze_size - 1):  # Avoid placing walls on the border
            for j in range(1, maze_size - 1):
                if [i, j] != player_pos and [i, j] not in treasures and random.choice([True, False, False]):
                    walls.append([i, j])

        return walls

    def generate_water(slope):
        water = []

        water_size = min(maze_size, maze_size) // 4

        start_x = random.randint(0, maze_size - water_size)
        start_y = random.randint(0, maze_size - water_size)

        # Fill the square with water
        for i in range(start_x, start_x + water_size):
            for j in range(start_y, start_y + water_size):
                water.append([i, j])

        return water

    slope = 0.5  # This is a placeholder; adjust your slope logic as needed
    water = generate_water(slope)

    walls = generate_walls()

    # Maze generation algorithm using BFS
    def solve(start_row, start_col):
        q = []
        q.append((start_row, start_col))
        visited = [[False for i in range(maze_size)] for j in range(maze_size)]
        visited[start_row][start_col] = True

        prev = [[None for i in range(maze_size)] for j in range(maze_size)]
        while len(q) > 0:
            row, col = q.pop(0)
            if [row, col] == treasure_pos:
                return prev

            # Check adjacent cells
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_row = row + dr
                next_col = col + dc
                if (
                    next_row >= 0 and next_row < maze_size and
                    next_col >= 0 and next_col < maze_size and
                    not visited[next_row][next_col] and
                    [next_row, next_col] not in walls
                ):
                    q.append((next_row, next_col))
                    visited[next_row][next_col] = True
                    prev[next_row][next_col] = (row, col)

        return None

    def reconstruct_path(start_row, start_col, end_row, end_col, prev):
        path = []
        row, col = end_row, end_col
        while (row, col) != (start_row, start_col):
            path.append((row, col))
            row, col = prev[row][col]
        path.append((start_row, start_col))
        path.reverse()
        return path

    def bfs(start_row, start_col, end_row, end_col):
        prev = solve(start_row, start_col)
        if prev is None:
            print("Caminho não encontrado.")
            return []
        return reconstruct_path(start_row, start_col, end_row, end_col, prev)

    # Player movement functions
    def move_player():
        path = bfs(player_pos[0], player_pos[1], treasure_pos[0], treasure_pos[1])
        if path:
            next_pos = path[1]  # Move to the next cell in the path
            dx = next_pos[0] - player_pos[0]
            dy = next_pos[1] - player_pos[1]
            if dx == 0 and dy == 1:
                return 'DOWN'
            elif dx == 0 and dy == -1:
                return 'UP'
            elif dx == 1 and dy == 0:
                return 'RIGHT'
            elif dx == -1 and dy == 0:
                return 'LEFT'
        return "NONE"  # If no path found, stay in place

    # Game loop
    running = True
    score = 0
    steps = 0
    while running:

        # Check if there are treasures left
        if treasures:
            treasure_pos = treasures[0]
        # Check if max steps exceeded
        else:
            print("All treasures found")
            running = False
            print(steps)
            print(score)
            break
    
        if steps >= 79:
            running = False
            print(steps)
            print(score)
            print("Max steps exceeded")

        
        direction = move_player()
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

        # Drawing
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
    
        # Check if player steps on water
        if [px, py] in water:
            score -= 5
            print("In water! Paying heavier price:", [px, py])

        pygame.display.flip() 
        pygame.time.wait(1)  # Slow down the game a bit

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