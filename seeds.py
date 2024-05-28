from PIL import Image

def generate_maze():
    image = Image.open('images/testmap.png')
    width, height = image.size
    maze = []
    for y in range(height):
        ys = []
        for x in range(width):
            pixel = image.getpixel((x, y))
            ys.append(2 if pixel[0] == 255 else 1 if pixel[3] == 255 else 0)
            print(pixel)
        maze.append(ys)
    image.close()
    return [maze, width, height]