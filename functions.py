import time
import math
import heapq
from threading import Timer
from PIL import Image

# a* 알고리즘
class Node:
    def __init__(self, PARENT=None, POSITION=None):
        self.PARENT = PARENT
        self.POSITION = POSITION
        self.G = 0
        self.H = 0
        self.F = 0

    def __eq__(self, OTHER):
        return self.POSITION == OTHER.POSITION

    def __lt__(self, OTHER):
        return self.F < OTHER.F

def heuristic(NODE, GOAL, D=1, D2=2 ** 0.5):
    DX = abs(NODE.POSITION[0] - GOAL.POSITION[0])
    DY = abs(NODE.POSITION[1] - GOAL.POSITION[1])
    return D * (DX + DY) + (D2 - 2 * D) * min(DX, DY)

def astar(MAZE, START, END, TIMEOUT = 1):
    ALREADY = False

    START_NODE = Node(None, START)
    END_NODE = Node(None, END)

    OPEN_LIST = []
    CLOSED_SET = set()

    heapq.heappush(OPEN_LIST, START_NODE)

    START_TIME = time.time()
    
    while OPEN_LIST:
        if not ALREADY:
            ALREADY = True
            END_TIME = START_TIME + TIMEOUT
        
        if time.time() > END_TIME:
            print('(CLEAR) A* TIMEOUT')
            return None
        
        CUR_NODE = heapq.heappop(OPEN_LIST)
        CLOSED_SET.add(CUR_NODE.POSITION)
        
        if CUR_NODE == END_NODE:
            PATH = []
            while CUR_NODE is not None:
                PATH.append(CUR_NODE.POSITION)
                CUR_NODE = CUR_NODE.PARENT
            return PATH[::-1]

        for NEW_POSITION in (0, -1), (0, 1), (-1, 0), (1, 0):
            NODE_POSITION = (CUR_NODE.POSITION[0] + NEW_POSITION[0], CUR_NODE.POSITION[1] + NEW_POSITION[1])

            if NODE_POSITION[0] > len(MAZE) - 1 or NODE_POSITION[0] < 0 or NODE_POSITION[1] > len(MAZE[0]) - 1 or NODE_POSITION[1] < 0: continue
            if MAZE[NODE_POSITION[0]][NODE_POSITION[1]] == 1: continue

            NEW_NODE = Node(CUR_NODE, NODE_POSITION)
            if NEW_NODE.POSITION in CLOSED_SET: continue

            NEW_NODE.G = CUR_NODE.G + 1
            NEW_NODE.H = heuristic(NEW_NODE, END_NODE)
            NEW_NODE.F = NEW_NODE.G + NEW_NODE.H

            if any(CHILD for CHILD in OPEN_LIST if NEW_NODE == CHILD and NEW_NODE.G > CHILD.G): continue

            heapq.heappush(OPEN_LIST, NEW_NODE)

# 맵 내부 생성
def generate_map(PATH):
    RED = (255, 0, 0, 255)
    BLACK = (0, 0, 0, 255)

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

# 원형 경계
def distance(RECT1, RECT2):
    return math.sqrt((RECT1.centerx - RECT2.centerx) ** 2 + (RECT1.centery - RECT2.centery) ** 2)

INTERVALS = []
INTERVAL_IDX = 0

# 매 초 마다 실행
def set_interval(CALLBACK, SEC, PARAM=None):
    global INTERVAL_IDX
    
    def func_wrapper(INTERVAL_IDX):
        INTERVALS[INTERVAL_IDX] = set_interval(CALLBACK, SEC, PARAM)
        if PARAM: CALLBACK(PARAM)
        else: CALLBACK()

    timer = Timer(SEC, func_wrapper, (INTERVAL_IDX,))
    timer.start()

    INTERVALS.append(timer)
    INTERVAL_IDX += 1
    
    return timer