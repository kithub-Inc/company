import random

def generate_maze(width, height):
    if width % 2 == 0 or height % 2 == 0:
        raise ValueError("Width and height must be odd numbers")

    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_passages(cx, cy):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        is_dead_end = True

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[cy + dy//2][cx + dx//2] = 0
                maze[ny][nx] = 0
                carve_passages(nx, ny)
                is_dead_end = False

        if is_dead_end:
            for dx, dy in directions:
                if 0 <= cx + dx < width and 0 <= cy + dy < height and maze[cy + dy][cx + dx] == 0:
                    maze[cy + dy//2][cx + dx//2] = 2
                    break

    start_x, start_y = (random.randrange(1, width, 2), random.randrange(1, height, 2))
    maze[start_y][start_x] = 0
    carve_passages(start_x, start_y)

    return maze