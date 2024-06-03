from PIL import Image

RED = (255, 0, 0, 255)
BLACK = (0, 0, 0, 255)
TRANSPARENT = (0, 0, 0, 0)

def generate_map(PATH):
    IMAGE = Image.open(PATH)
    width, height = IMAGE.size

    maze = []

    for Y in range(height):
        YS = []

        for X in range(width):
            PIXEL = IMAGE.getpixel((X, Y))
            
            TILE = 0
            if PIXEL == BLACK: TILE = 1
            elif PIXEL == RED: TILE = 2

            YS.append(TILE)

        maze.append(YS)

    IMAGE.close()

    return [maze, width, height]