import pygame
import pyautogui
import math
import random
import sys
import time
import uuid
import heapq
from threading import Timer
from functools import reduce
from PIL import Image

# 이미지, 사운드
from images import *
from sounds import *

# 전체적인 설정
CONFIG = {
    'SCREEN_WIDTH': pyautogui.size()[0], # 너비
    'SCREEN_HEIGHT': pyautogui.size()[1], # 높이
    'TILE_SIZE': 100, # 타일 사이즈
    'DEBUG': False, # 디버그
    'MASTER_SOUND': 1, # 최대 사운드
    'MIXING': False # 사운드 조절중 여부
}

# 초기화
pygame.init()
screen = pygame.display.set_mode((CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT']), pygame.FULLSCREEN)
pygame.display.set_caption('COMPANY')
pygame.display.set_icon(pygame.image.load('images/icon.ico'))

# 폰트
font = pygame.font.Font('fonts/Orbit-Regular.ttf', 18)
font2 = pygame.font.Font('fonts/Orbit-Regular.ttf', 24)
font3 = pygame.font.Font('fonts/Orbit-Regular.ttf', 72)
font4 = pygame.font.Font('fonts/Orbit-Regular.ttf', 48)

# 인게임 변수
INGAME = {
    'RUNNING': True, # 실행 상태
    'SCENES': [], # 씬들
    'CUR_SCENE': '', # 현재 씬
    'SPRITES': [], # 스프라이트들
    'MAPS': [], # 맵들
    'CUR_MAP': '', # 현재 맵
    'NEXT_MAP': 'experimentation', # 다음으로 착륙할 맵
    'CUR_MOD': 'READY', # READY: 착륙 준비 완료, OK: 착륙 후, FARMING: 미로 맵 입장 후
    'TERMINAL': False, # 터미널 on/off 토글
    'COMMAND': '', # 터미널에 입력한 커맨드
    'HELP': '', # 터미널에 출력되는 문자열
    'STORE': [], # 상점에서 구매한 아이템
    'DELIVERY': False, # 배달
    'DELIVERY_LANDING': True, # 배달 준비 여부
    'SCAN': False, # 스캔중 여부
    'TIME': 60 * 8, # 8시부터 시작
    'MONEY': 60, # 현금
    'DAY': 3, # 마감일
    'QUOTA': 0, # 채워진 할당량
    'TARGET_QUOTA': 130, # 할당량
    'CAMERA_MOVE': False, # 카메라 움직임 토글
    'CAMERA_X': 0, # 카메라 포지션 x
    'CAMERA_Y': 0, # 카메라 포지션 y
    'CHARGING': False, # 충전중 여부
    'SAVES': [], # 저장된 아이템들
    'SURVIVAL_RESULT': False, # 생존 결과 표시중 여부
    'QUOTA_RESULT': False, # 할당량 결과 표시중 여부
    'DAY_RESULT': False # 마감일 결과 표시중 여부
}

# 스프라이트 객체
class Sprite(pygame.sprite.Sprite):
    def __init__(self, SPRITE_ID, TYPE, DISPLAY_NAME, FRONT_IMAGE, BACK_IMAGE, LEFT_IMAGE, RIGHT_IMAGE, FRONT_WALK_IMAGE, BACK_WALK_IMAGE, LEFT_WALK_IMAGE, RIGHT_WALK_IMAGE):
        super().__init__()

        self.UUID = uuid.uuid4()

        self.ID = SPRITE_ID # 아이디
        self.DISPLAY_NAME = DISPLAY_NAME # 이름
        self.TYPE = TYPE # 타입

        self.INVINCIBILITY = False # 무적
        self.PRICE = 0 # 가격
        self.INVENTORY = [] # 인벤토리
        self.CUR_ITEM_IDX = 0 # 현재 들고있는 아이템 인덱스
        self.CONTAIN = None # 원형 경계 안으로 들어온 오브젝트
        self.FLASHLIGHT = False # 손전등 on/off 토글
        self.LOCKED = False # 문 잠김
        self.OPENED = False # 문 on/off 토글
        self.HP = 15 # 체력
        self.DECREASING = False # 체력 소모중 여부
        self.DECREASING_SIZE = 3 # 체력 소모 크기
        self.DIED = False # 사망 여부
        self.DAMAGE = 3 # 공격 대미지
        self.DISTANCE = 500 # 넓은 원형 경계 (대부분 추적용)
        self.ATTACK_DISTANCE = 150 # 좁은 원형 경계 (대부분 공격용)
        self.TRACK = False # 추적
        self.GUAGE = 100 # 게이지
        self.ALREADY_PLAY = False # 이미 재생함 여부

        self.FRONT_IMAGE = FRONT_IMAGE
        self.BACK_IMAGE = BACK_IMAGE
        self.LEFT_IMAGE = LEFT_IMAGE
        self.RIGHT_IMAGE = RIGHT_IMAGE
        self.FRONT_WALK_IMAGE = FRONT_WALK_IMAGE
        self.BACK_WALK_IMAGE = BACK_WALK_IMAGE
        self.LEFT_WALK_IMAGE = LEFT_WALK_IMAGE
        self.RIGHT_WALK_IMAGE = RIGHT_WALK_IMAGE
        
        self.CUR_IMAGE = FRONT_IMAGE # 현재 이미지
        self.LAST_ROTATE = 'front' # 마지막으로 본 방향
        self.WALKING = False # 걷는중 여부
        self.SPEED = 1 # 걷는 속도

        self.RECT = self.CUR_IMAGE.get_rect()
        self.RECT.center = (CONFIG['SCREEN_WIDTH'] // 2, CONFIG['SCREEN_HEIGHT'] // 2)

        # 자동 전송
        INGAME['SPRITES'].append(self)
    
    # 해당 값 만큼 좌표 이동
    def move(self, DX, DY, NO_CRASH=False):
        self.WALKING = True
        
        OLD_RECT = self.RECT.copy()

        self.RECT.x += DX
        self.RECT.y += DY

        if not NO_CRASH:
            # 충돌
            for Y, ROW in enumerate(CUR_MAP['ARRAY']):
                for X, TILE in enumerate(ROW):
                    if CUR_MAP['ID'] == 'ship':
                        if TILE in [SHIP_WALL, SHIP_TERMINAL]:
                            self.crash(X, Y, OLD_RECT)
                    
                    elif CUR_MAP['ID'] == 'experimentation':
                        if TILE in [EXPERIMENTATION_WALL]:
                            self.crash(X, Y, OLD_RECT)
                    
                    elif CUR_MAP['ID'] == 'factory':
                        if TILE in [FACTORY_WALL]:
                            self.crash(X, Y, OLD_RECT)
                    
                    elif CUR_MAP['ID'] == 'company':
                        if TILE in [FACTORY_WALL]:
                            self.crash(X, Y, OLD_RECT)
            
            for OBJECT in CUR_MAP['OBJECTS']:
                X = OBJECT.RECT.x / 100
                Y = OBJECT.RECT.y / 100

                if CUR_MAP['ID'] == 'ship':
                    if OBJECT.TYPE == 'terminal':
                        self.crash(X, Y, OLD_RECT)
                
                if CUR_MAP['ID'] == 'experimentation':
                    if OBJECT.TYPE in ['enter', 'terminal']:
                        self.crash(X, Y, OLD_RECT)
                
                if CUR_MAP['ID'] == 'factory':
                    if OBJECT.TYPE in ['door', 'exit'] and not OBJECT.OPENED:
                        self.crash(X, Y, OLD_RECT)
                
                if CUR_MAP['ID'] == 'company':
                    if OBJECT.TYPE in ['salemanager', 'terminal']:
                        self.crash(X, Y, OLD_RECT)

        # 현재 이미지 변경
        if DY > 0:
            self.CUR_IMAGE = self.FRONT_WALK_IMAGE
            self.LAST_ROTATE = 'front'

        if DY < 0:
            self.CUR_IMAGE = self.BACK_WALK_IMAGE
            self.LAST_ROTATE = 'back'

        if DX < 0:
            self.CUR_IMAGE = self.LEFT_WALK_IMAGE
            self.LAST_ROTATE = 'left'

        if DX > 0:
            self.CUR_IMAGE = self.RIGHT_WALK_IMAGE
            self.LAST_ROTATE = 'right'
    
    # 충돌
    def crash(self, X, Y, OLD_RECT, SIZE=CONFIG['TILE_SIZE']):
        WALL_RECT = pygame.Rect(X * CONFIG['TILE_SIZE'], Y * CONFIG['TILE_SIZE'], SIZE, SIZE)

        if self.RECT.colliderect(WALL_RECT):
            self.RECT = OLD_RECT
            return
    
    # 해당 좌표로 이동
    def teleport(self, X, Y):
        self.RECT.x = X
        self.RECT.y = Y
    
    # 맵 이동
    def map_to(self, FIRST, MAP_ID):
        MAP_REDUCED = Map.reduced('ID')
        FROM_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
        TO_MAP_IDX = MAP_REDUCED.index(MAP_ID)

        INGAME['MAPS'][TO_MAP_IDX]['OBJECTS'].append(self)
        
        if not FIRST:
            INGAME['MAPS'][FROM_MAP_IDX]['OBJECTS'].remove(self)
    
    # 아이템 드랍
    def drop_item(self, CUR_ITEM):
        if CUR_ITEM.ID in ['stop', 'shovel']: DROP_SHOVEL.play()
        elif CUR_ITEM.ID == 'key': DROP_KEY.play()
        elif CUR_ITEM.ID == 'bottle': DROP_BOTTLE.play()
        elif CUR_ITEM.ID == 'flashlight': DROP_FLASHLIGHT.play()
        else: GRAB_DEFAULT_ITEM.play()

        CUR_ITEM.RECT.x = self.RECT.x
        CUR_ITEM.RECT.y = self.RECT.y
        CUR_MAP['OBJECTS'].append(CUR_ITEM)
        self.INVENTORY.remove(CUR_ITEM)
    
    # 아이템 수집
    def grab_item(self):
        if self.CONTAIN.ID in ['stop', 'shovel']: GRAB_SHOVEL.play()
        elif self.CONTAIN.ID == 'key': GRAB_KEY.play()
        elif self.CONTAIN.ID == 'bottle': GRAB_BOTTLE.play()
        elif self.CONTAIN.ID == 'flashlight': GRAB_FLASHLIGHT.play()
        else: GRAB_DEFAULT_ITEM.play()

        self.INVENTORY.append(self.CONTAIN)
        CUR_MAP['OBJECTS'].remove(self.CONTAIN)
        self.CONTAIN = None

# 맵 객체
class Map:
    def __init__(self, MAP_ID, MAP_DISPLAY_NAME, MAP_ARRAY):
        self.MAP_ID = MAP_ID
        self.MAP_DISPLAY_NAME = MAP_DISPLAY_NAME
        self.MAP_ARRAY = MAP_ARRAY

        # 자동 전송
        INGAME['MAPS'].append({
            'ID': self.MAP_ID,
            'DISPLAY_NAME': self.MAP_DISPLAY_NAME,
            'ARRAY': self.MAP_ARRAY,
            'OBJECTS': []
        })
    
    # 맵을 리스트로
    @staticmethod
    def reduced(PROPERTY):
        return reduce(lambda acc, cur: acc + [cur[PROPERTY]], INGAME['MAPS'], [])

# 씬 객체
class Scene:
    def __init__(self, SCENE_ID, SCENE_DISPLAY_NAME):
        self.SCENE_ID = SCENE_ID
        self.SCENE_DISPLAY_NAME = SCENE_DISPLAY_NAME

        # 자동 전송
        INGAME['SCENES'].append({
            'ID': self.SCENE_ID,
            'DISPLAY_NAME': self.SCENE_DISPLAY_NAME,
            'INTERFACES': []
        })
    
    # 씬을 리스트로
    @staticmethod
    def reduced(PROPERTY):
        return reduce(lambda acc, cur: acc + [cur[PROPERTY]], INGAME['SCENES'], [])

# 인터페이스 객체
class Interface:
    def __init__(self, INTERFACE_ID, INTERFACE_DISPLAY_NAME, INTERFACE_BEFORE_TEXT, INTERFACE_AFTER_TEXT, INTERFACE_RECT, INTERFACE_HOVER = False):
        self.INTERFACE_ID = INTERFACE_ID
        self.INTERFACE_DISPLAY_NAME = INTERFACE_DISPLAY_NAME
        self.INTERFACE_AFTER_TEXT = INTERFACE_AFTER_TEXT
        self.INTERFACE_BEFORE_TEXT = INTERFACE_BEFORE_TEXT
        self.INTERFACE_RECT = INTERFACE_RECT
        self.INTERFACE_HOVER = INTERFACE_HOVER
    
    def to(self, SCENE_ID):
        SCENE_REDUCED = Scene.reduced('ID')
        TO_SCENE_IDX = SCENE_REDUCED.index(SCENE_ID)

        INGAME['SCENES'][TO_SCENE_IDX]['INTERFACES'].append(self)

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

def astar(MAZE, START, END):
    START_NODE = Node(None, START)
    END_NODE = Node(None, END)

    OPEN_LIST = []
    CLOSED_SET = set()

    heapq.heappush(OPEN_LIST, START_NODE)

    while OPEN_LIST:
        CUR_NODE = heapq.heappop(OPEN_LIST)
        CLOSED_SET.add(CUR_NODE.POSITION)
        
        if CUR_NODE == END_NODE:
            PATH = []
            while CUR_NODE is not None:
                PATH.append(CUR_NODE.POSITION)
                CUR_NODE = CUR_NODE.parent
            return PATH[::-1]

        for NEW_POSITION in (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1):
            NODE_POSITION = (CUR_NODE.POSITION[0] + NEW_POSITION[0], CUR_NODE.POSITION[1] + NEW_POSITION[1])

            if NODE_POSITION[0] > len(MAZE) - 1 or NODE_POSITION[0] < 0 or NODE_POSITION[1] > len(MAZE[0]) - 1 or NODE_POSITION[1] < 0: continue
            if MAZE[NODE_POSITION[0]][NODE_POSITION[1]] != 0: continue

            NEW_NODE = Node(CUR_NODE, NODE_POSITION)
            if NEW_NODE.POSITION in CLOSED_SET: continue

            NEW_NODE.G = CUR_NODE.G + 1
            NEW_NODE.H = heuristic(NEW_NODE, END_NODE)
            NEW_NODE.F = NEW_NODE.G + NEW_NODE.H

            if any(CHILD for CHILD in OPEN_LIST if NEW_NODE == CHILD and NEW_NODE.G > CHILD.G): continue

            heapq.heappush(OPEN_LIST, NEW_NODE)

# 맵 내부 생성
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

# 원형 경계
def distance(RECT1, RECT2):
    return math.sqrt((RECT1.centerx - RECT2.centerx) ** 2 + (RECT1.centery - RECT2.centery) ** 2)

# 매 초 마다 실행
def set_interval(CALLBACK, SEC):
    def func_wrapper():
        set_interval(CALLBACK, SEC)
        CALLBACK()

    timer = Timer(SEC, func_wrapper)
    timer.start()
    return timer

# 볼륨 믹서
def mixing():
    MAIN_MUSIC_1.set_volume(CONFIG['MASTER_SOUND'])
    MAIN_MUSIC_2.set_volume(CONFIG['MASTER_SOUND'])
    LOBBY_MUSIC_3.set_volume(CONFIG['MASTER_SOUND'])
    INTRO_MUSIC.set_volume(CONFIG['MASTER_SOUND'])
    MENU_MUSIC.set_volume(CONFIG['MASTER_SOUND'])
    DELIVERY_MUSIC.set_volume(CONFIG['MASTER_SOUND'])
    DOOR_OPENING.set_volume(CONFIG['MASTER_SOUND'])
    METAL_DOOR_SHUT.set_volume(CONFIG['MASTER_SOUND'])
    METAL_DOOR_CLOSE.set_volume(CONFIG['MASTER_SOUND'])
    NOISE.set_volume(CONFIG['MASTER_SOUND'])
    NOISE_2.set_volume(CONFIG['MASTER_SOUND'])
    METAL_WALK_1.set_volume(CONFIG['MASTER_SOUND'])
    METAL_WALK_2.set_volume(CONFIG['MASTER_SOUND'])
    METAL_WALK_3.set_volume(CONFIG['MASTER_SOUND'])
    METAL_WALK_4.set_volume(CONFIG['MASTER_SOUND'])
    GRAB_SHOVEL.set_volume(CONFIG['MASTER_SOUND'])
    GRAB_KEY.set_volume(CONFIG['MASTER_SOUND'])
    GRAB_BOTTLE.set_volume(CONFIG['MASTER_SOUND'])
    GRAB_FLASHLIGHT.set_volume(CONFIG['MASTER_SOUND'])
    GRAB_DEFAULT_ITEM.set_volume(CONFIG['MASTER_SOUND'])
    DROP_SHOVEL.set_volume(CONFIG['MASTER_SOUND'])
    DROP_KEY.set_volume(CONFIG['MASTER_SOUND'])
    DROP_BOTTLE.set_volume(CONFIG['MASTER_SOUND'])
    DROP_FLASHLIGHT.set_volume(CONFIG['MASTER_SOUND'])
    FLASHLIGHT_CLICK.set_volume(CONFIG['MASTER_SOUND'])
    BRACKEN_ATTACK.set_volume(CONFIG['MASTER_SOUND'])
    JESTER_DOING.set_volume(CONFIG['MASTER_SOUND'])
    COILHEAD_ATTACK_1.set_volume(CONFIG['MASTER_SOUND'])
    COILHEAD_ATTACK_2.set_volume(CONFIG['MASTER_SOUND'])

# 메인 씬
Main = Scene('main', '메인')
INGAME['CUR_SCENE'] = Main.SCENE_ID

Title = Interface('title', '제목', 'COMPANY™', 'COMPANY™', (200, 200))
Title.to(Main.SCENE_ID)

Menu1 = Interface('menu', '메뉴1', '시작하기', '> 시작하기', (200, 300))
Menu1.to(Main.SCENE_ID)

Menu1 = Interface('menu', '메뉴2', '설정', '> 설정', (200, 350))
Menu1.to(Main.SCENE_ID)

Menu2 = Interface('menu', '메뉴3', '종료', '> 종료', (200, 400))
Menu2.to(Main.SCENE_ID)

MENU_MUSIC.play(loops=-1)

# 설정 씬
Setting = Scene('setting', '설정')

Title = Interface('menu', '메뉴1', '> 돌아가기', '< 돌아가기', (200, 200))
Title.to(Setting.SCENE_ID)

# 인게임 씬
Ingame = Scene('ingame', '인게임')

# 타일
SHIP_WALL = 1
SHIP_TERMINAL = 2

EXPERIMENTATION_WALL = 1
EXPERIMENTATION_TILE = 2

FACTORY_WALL = 1
FACTORY_DOOR = 2
FACTORY_PIPE1 = 3
FACTORY_PIPE2 = 4
FACTORY_PIPE3 = 5
FACTORY_WEB1 = 6
FACTORY_WEB2 = 7

COMPANY_TILE = 2
COMPANY_WALL = 1

# 함선 맵
OUTPUT = generate_map('images/map/ship.png')
ShipArray = OUTPUT[0]
Ship = Map('ship', 'ship', ShipArray)
INGAME['CUR_MAP'] = Ship.MAP_ID

# 터미널
Terminal = Sprite('terminal', 'terminal', '터미널', TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE)
Terminal.map_to(True, Ship.MAP_ID)
Terminal.teleport(200, 100)

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Ship.MAP_ID)
Charger.teleport(325, 75)

# 익스페리멘테이션 맵
OUTPUT = generate_map('images/map/experimentation.png')
ExperimentationArray = OUTPUT[0]
Experimentation = Map('experimentation', 'experimentation', ExperimentationArray)

# 터미널
Terminal = Sprite('terminal', 'terminal', '터미널', TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE)
Terminal.map_to(True, Experimentation.MAP_ID)
Terminal.teleport(400, 1900)

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Experimentation.MAP_ID)
Charger.teleport(525, 1875)

# 배달
Delivery = Sprite('delivery', 'delivery', '배달', DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE)
Delivery.map_to(True, Experimentation.MAP_ID)
Delivery.teleport(1700, -1000)

# 정문
Enter1 = Sprite('enter', 'enter', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Enter1.map_to(True, Experimentation.MAP_ID)
Enter1.teleport(3900, 2000)

Enter2 = Sprite('enter', 'enter', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Enter2.map_to(True, Experimentation.MAP_ID)
Enter2.teleport(3900, 2100)

# 열리는 문
Open1 = Sprite('open', 'open_up', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open1.map_to(True, Experimentation.MAP_ID)
Open1.teleport(1200, 2100)

Open2 = Sprite('open', 'open_down', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open2.map_to(True, Experimentation.MAP_ID)
Open2.teleport(1200, 2100)

# 공장 맵
OUTPUT = generate_map('images/map/factory.png')
FactoryArray = OUTPUT[0]
Factory = Map('factory', 'factory', FactoryArray)

# 문 생성
for Y, ROW in enumerate(Factory.MAP_ARRAY):
    for X, TILE in enumerate(ROW):
        if TILE == 0:
            rand = random.randrange(0, 50)
            if rand == 1: Factory.MAP_ARRAY[Y][X] = FACTORY_WEB1
            if rand == 2: Factory.MAP_ARRAY[Y][X] = FACTORY_WEB2

        if TILE == FACTORY_DOOR:
            Factory.MAP_ARRAY[Y][X] = 0

            # 문
            if Factory.MAP_ARRAY[Y][X - 1] == FACTORY_WALL and Factory.MAP_ARRAY[Y][X + 1] == FACTORY_WALL: IMAGE = DOOR_IMAGE
            else: IMAGE = DOOR_2_IMAGE
            
            Door = Sprite('door', 'door', '문', IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE)
            Door.map_to(True, Factory.MAP_ID)
            Door.teleport(X * 100, Y * 100)
            Door.LOCKED = True if random.randrange(0, 20) == 0 else False

# 나가는 문
Exit = Sprite('exit', 'exit', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Exit.map_to(True, Factory.MAP_ID)
Exit.teleport(0, 300)

# 회사 맵
_ = generate_map('images/map/company.png')
CompanyArray = _[0]
Company = Map('company', 'company', CompanyArray)

# 터미널
Terminal = Sprite('terminal', 'terminal', '터미널', TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE)
Terminal.map_to(True, Company.MAP_ID)
Terminal.teleport(2700, 5400)

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Company.MAP_ID)
Charger.teleport(2825, 5375)

# 배달
Delivery2 = Sprite('delivery', 'delivery', '배달', DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE)
Delivery2.map_to(True, Company.MAP_ID)
Delivery2.teleport(4000, -1000)

# 열리는 문
Open3 = Sprite('open', 'open_up', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open3.map_to(True, Company.MAP_ID)
Open3.teleport(3500, 5500)

Open4 = Sprite('open', 'open_down', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open4.map_to(True, Company.MAP_ID)
Open4.teleport(3500, 5700)

SaleManager = Sprite('salemanager', 'salemanager', '판매소', COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE)
SaleManager.map_to(True, Company.MAP_ID)
SaleManager.teleport(4900, 5100)

SaleManager = Sprite('salemanager', 'salemanager', '판매소', COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE)
SaleManager.map_to(True, Company.MAP_ID)
SaleManager.teleport(4900, 5200)

CompanyMonster = Sprite('monster', 'monster', '회사 괴물', TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE)
CompanyMonster.map_to(True, Company.MAP_ID)
CompanyMonster.teleport(4900, 5150)
CompanyMonster.DAMAGE = 100

# 플레이어
Player = Sprite('player', 'player', '플레이어', PLAYER_FRONT_IMAGE, PLAYER_BACK_IMAGE, PLAYER_LEFT_IMAGE, PLAYER_RIGHT_IMAGE, PLAYER_FRONT_WALK_IMAGE, PLAYER_BACK_WALK_IMAGE, PLAYER_LEFT_WALK_IMAGE, PLAYER_RIGHT_WALK_IMAGE)
Player.map_to(True, Ship.MAP_ID)
Player.teleport(300, 300)
Player.DISTANCE = (CONFIG['SCREEN_WIDTH'] / 2) + 300
if CONFIG['DEBUG']: Player.INVINCIBILITY = True

# 플레이어 걷는 소리 재생
def player_walk_sound():
    if Player.WALKING:
        RANDOM = random.randrange(1, 5)
        if RANDOM == 1: METAL_WALK_1.play()
        elif RANDOM == 2: METAL_WALK_2.play()
        elif RANDOM == 3: METAL_WALK_3.play()
        elif RANDOM == 4: METAL_WALK_4.play()

set_interval(player_walk_sound, .4)

# 체력 소모
def decrease_player_hp():
    if Player.DECREASING and not Player.INVINCIBILITY:
        Player.HP -= Player.DECREASING_SIZE

set_interval(decrease_player_hp, .5)

# 게이지
def gauge():
    INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])

    if Player.FLASHLIGHT and 'flashlight' in INVENTORY:
        if not Player.DIED and not CONFIG['DEBUG']:
            if not Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE == 0:
                Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE -= 2
    else: Player.FLASHLIGHT = False

set_interval(gauge, 20)

# 시간
def increase_time():
    if not INGAME['CUR_MOD'] == 'READY' and not INGAME['CUR_MAP'] == 'company':
        INGAME['TIME'] += 4

        if INGAME['TIME'] == 60 * 8 + 24 and len(INGAME['STORE']) > 0:
            for ITEM in INGAME['STORE']:
                Item = Sprite(ITEM['ID'], 'item', ITEM['DISPLAY_NAME'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'])
                if INGAME['CUR_MAP'] == 'experimentation': Delivery.INVENTORY.append(Item)
                elif INGAME['CUR_MAP'] == 'company': Delivery2.INVENTORY.append(Item)
            INGAME['STORE'] = []

            INGAME['DELIVERY'] = True
            INGAME['DELIVERY_LANDING'] = True

            def delivery_music_play():
                DELIVERY_MUSIC.play()
            
            Timer(6, delivery_music_play).start()

set_interval(increase_time, 3)

while INGAME['RUNNING']:
    # try:
        if INGAME['CUR_SCENE'] == 'main':
            # 현재 씬
            SCENE_REDUCED = Scene.reduced('ID')
            CUR_SCENE_IDX = SCENE_REDUCED.index(INGAME['CUR_SCENE'])
            CUR_SCENE = INGAME['SCENES'][CUR_SCENE_IDX]

            screen.fill((0, 0, 0))

            for INTERFACE in CUR_SCENE['INTERFACES']:
                text_ = font2.render(INTERFACE.INTERFACE_BEFORE_TEXT, True, (255, 255, 255))
                if INTERFACE.INTERFACE_HOVER: text_ = font2.render(INTERFACE.INTERFACE_AFTER_TEXT, True, (255, 255, 255))
                screen.blit(text_, INTERFACE.INTERFACE_RECT)
            
            # 이벤트
            for event in pygame.event.get():
                # 종료
                if event.type == pygame.QUIT: INGAME['RUNNING'] = False
                
                if event.type == pygame.MOUSEMOTION:
                    for INTERFACE in CUR_SCENE['INTERFACES']:
                        if INTERFACE.INTERFACE_ID == 'menu':
                            RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                            INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                            INTERFACE.INTERFACE_HOVER = False
                            if INTERFACE_RECT.collidepoint(event.pos): INTERFACE.INTERFACE_HOVER = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    for INTERFACE in CUR_SCENE['INTERFACES']:
                        if INTERFACE.INTERFACE_ID == 'menu':
                            RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                            INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                            if INTERFACE_RECT.collidepoint(event.pos):
                                if INTERFACE.INTERFACE_DISPLAY_NAME == '메뉴1':
                                    time.sleep(.5)

                                    INGAME['CUR_SCENE'] = Ingame.SCENE_ID
                                    pygame.mouse.set_visible(False)

                                    MENU_MUSIC.stop()

                                    # 인트로 스피치 재생
                                    def intro_music_play():
                                        INTRO_MUSIC.play()

                                    Timer(1, intro_music_play).start()
                                
                                elif INTERFACE.INTERFACE_DISPLAY_NAME == '메뉴2':
                                    INGAME['CUR_SCENE'] = Setting.SCENE_ID
                                
                                elif INTERFACE.INTERFACE_DISPLAY_NAME == '메뉴3':
                                    INGAME['RUNNING'] = False
        
        if INGAME['CUR_SCENE'] == 'setting':
            # 현재 씬
            SCENE_REDUCED = Scene.reduced('ID')
            CUR_SCENE_IDX = SCENE_REDUCED.index(INGAME['CUR_SCENE'])
            CUR_SCENE = INGAME['SCENES'][CUR_SCENE_IDX]

            screen.fill((0, 0, 0))

            for INTERFACE in CUR_SCENE['INTERFACES']:
                text_ = font2.render(INTERFACE.INTERFACE_BEFORE_TEXT, True, (255, 255, 255))
                if INTERFACE.INTERFACE_HOVER: text_ = font2.render(INTERFACE.INTERFACE_AFTER_TEXT, True, (255, 255, 255))
                screen.blit(text_, INTERFACE.INTERFACE_RECT)

            text_ = font2.render('스껄!', True, (255, 255, 255))
            screen.blit(text_, (220, 320))
            pygame.draw.rect(screen, (255, 255, 255), (200, 300, 250, 80), 1)
            pygame.draw.rect(screen, (255, 255, 255), (210, 310, 230, 60), 1)
            
            text_ = font2.render('주 음량', True, (255, 255, 255))
            screen.blit(text_, (200, 430))
            pygame.draw.rect(screen, (255, 255, 255), (200, 490, 200, 3), 3)
            pygame.draw.circle(screen, (0, 0, 0), (200 + CONFIG['MASTER_SOUND'] * 100, 490), 10)
            pygame.draw.circle(screen, (255, 255, 255), (200 + CONFIG['MASTER_SOUND'] * 100, 490), 5)
            
            # 이벤트
            for event in pygame.event.get():
                # 종료
                if event.type == pygame.QUIT: INGAME['RUNNING'] = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    RECT = pygame.Rect(200, 465, 200, 30)

                    if RECT.collidepoint(event.pos):
                        CONFIG['MIXING'] = True
                        CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * 0.01
                        mixing()
                
                if event.type == pygame.MOUSEMOTION:
                    RECT = pygame.Rect(200, 465, 200, 30)

                    if CONFIG['MIXING']:
                        if RECT.collidepoint(event.pos):
                            CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * 0.01
                            mixing()
                    
                    else:
                        for INTERFACE in CUR_SCENE['INTERFACES']:
                            if INTERFACE.INTERFACE_ID == 'menu':
                                RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                                INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                                INTERFACE.INTERFACE_HOVER = False
                                if INTERFACE_RECT.collidepoint(event.pos): INTERFACE.INTERFACE_HOVER = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    RECT = pygame.Rect(200, 465, 200, 30)

                    if CONFIG['MIXING']:
                        if RECT.collidepoint(event.pos):
                            CONFIG['MIXING'] = False
                            CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * 0.01
                            mixing()
                    
                    else:
                        for INTERFACE in CUR_SCENE['INTERFACES']:
                            if INTERFACE.INTERFACE_ID == 'menu':
                                RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                                INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                                if INTERFACE_RECT.collidepoint(event.pos):
                                    if INTERFACE.INTERFACE_DISPLAY_NAME == '메뉴1':
                                        INGAME['CUR_SCENE'] = Main.SCENE_ID
        
        elif INGAME['CUR_SCENE'] == 'ingame':
            # 현재 맵
            MAP_REDUCED = Map.reduced('ID')
            CUR_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
            CUR_MAP = INGAME['MAPS'][CUR_MAP_IDX]

            CUR_ITEM_EXISTS = len(Player.INVENTORY) >= Player.CUR_ITEM_IDX + 1

            if CONFIG['DEBUG']: screen.fill((0, 0, 255))
            else: screen.fill((0, 0, 0))
            
            keys = pygame.key.get_pressed()

            # 이벤트
            for event in pygame.event.get():
                # 종료
                if event.type == pygame.QUIT: INGAME['RUNNING'] = False

                # 플레이어가 살아있을 때
                if not Player.DIED:
                    # 키를 눌렀을 떄
                    if event.type == pygame.KEYDOWN:
                        # 터미널에 입력
                        if INGAME['TERMINAL']:
                            # 나가기
                            if event.key == pygame.K_ESCAPE:
                                INGAME['TERMINAL'] = False
                                INGAME['COMMAND'] = ''

                            # 지우기
                            elif event.key == pygame.K_BACKSPACE:
                                INGAME['COMMAND'] = INGAME['COMMAND'][:-1]
                            
                            # 띄어쓰기
                            elif event.key == pygame.K_SPACE:
                                INGAME['COMMAND'] += ' '
                            
                            # 커맨드
                            elif event.key == pygame.K_RETURN:
                                if INGAME['COMMAND'] == 'moons':
                                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}

                                    > experimentation
                                    기본적인 행성 입니다.
                                    
                                    > company
                                    회사 건물 입니다. 날이 차감되지 않으며
                                    아이템을 팔 수 있습니다.
                                    
                                    예시) > company'''

                                elif INGAME['COMMAND'] == 'store':
                                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                    
                                    > flashlight
                                    프로 손전등 입니다. f키로 킬 수 있습니다.

                                    > shovel
                                    철제 삽 입니다. r키로 공격할 수 있습니다.
                                    
                                    예시) > flashlight'''

                                elif INGAME['COMMAND'] in ['flashlight', 'shovel']:
                                    if INGAME['MONEY'] - 25 <= 0:
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        현금이 모자랍니다.'''

                                    else:
                                        DISPLAY_NAME = '철제 삽' if INGAME['COMMAND'] == 'shovel' else '손전등'
                                        INGAME['MONEY'] -= 25 if INGAME['COMMAND'] == 'flashlight' else 30
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}

                                        {DISPLAY_NAME} 1개를 주문했습니다.'''
                                        INGAME['STORE'].append({ 'ID': INGAME['COMMAND'], 'DISPLAY_NAME': DISPLAY_NAME, 'IMAGE': SHOVEL_IMAGE if INGAME['COMMAND'] == 'shovel' else FLASHLIGHT_IMAGE })

                                elif INGAME['COMMAND'] in ['experimentation', 'company']:
                                    if INGAME['CUR_MOD'] == 'READY':
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        {INGAME['COMMAND']} 으로 함선이 이동했습니다.
                                        이동 비용은 $0원 입니다.'''
                                        INGAME['NEXT_MAP'] = INGAME['COMMAND']
                                    
                                    else:
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        이륙한 다음에만 이동할 수 있습니다.'''
                                
                                elif INGAME['COMMAND'] == 'land':
                                    if INGAME['CUR_MOD'] == 'READY':
                                        CUR_MAP = INGAME['MAPS'][Map.reduced('ID').index(INGAME['NEXT_MAP'])]

                                        try:
                                            for ITEM in INGAME['SAVES']:
                                                CUR_MAP['OBJECTS'].remove(ITEM)
                                        except: ...

                                        if INGAME['NEXT_MAP'] == 'company':
                                            for ITEM in INGAME['SAVES']:
                                                ITEM.RECT.x += 2600
                                                ITEM.RECT.y += 5300
                                                CUR_MAP['OBJECTS'].append(ITEM)
                                        
                                        if INGAME['NEXT_MAP'] == 'experimentation':
                                            for ITEM in INGAME['SAVES']:
                                                ITEM.RECT.x += 200
                                                ITEM.RECT.y += 1800
                                                CUR_MAP['OBJECTS'].append(ITEM)
                                        
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        {INGAME['NEXT_MAP']}으로 함선이 착륙합니다.'''

                                        NEXT_MAP = None
                                        if INGAME['NEXT_MAP'] == 'experimentation': NEXT_MAP = Experimentation
                                        if INGAME['NEXT_MAP'] == 'company': NEXT_MAP = Company

                                        INGAME['TERMINAL'] = False

                                        Player.map_to(False, NEXT_MAP.MAP_ID)
                                        if INGAME['NEXT_MAP'] == 'experimentation': Player.teleport(200 + Player.RECT.x, 1800 + Player.RECT.y)
                                        if INGAME['NEXT_MAP'] == 'company': Player.teleport(2500 + Player.RECT.x, 5300 + Player.RECT.y)
                                        
                                        INGAME['CUR_MAP'] = NEXT_MAP.MAP_ID
                                        INGAME['CUR_MOD'] = 'OK'

                                        INGAME['CAMERA_MOVE'] = True

                                        INTRO_MUSIC.stop()

                                        # 착륙 사운드 재생
                                        DOOR_OPENING.play()
                                        NOISE.play()

                                        if INGAME['NEXT_MAP'] == 'experimentation':
                                            # 메인 음악 재생
                                            def main_music():
                                                if random.randrange(1, 3) == 1: MAIN_MUSIC_1.play()
                                                else: MAIN_MUSIC_2.play()

                                            Timer(10, main_music).start()

                                            FACTORY = INGAME['MAPS'][Map.reduced('ID').index('factory')]
                                            WILL_REMOVES = []
                                            for OBJECT in FACTORY['OBJECTS']:
                                                if OBJECT.TYPE in ['item', 'monster', 'door']: WILL_REMOVES.append(OBJECT)
                                            
                                            for OBJECT in WILL_REMOVES:
                                                Door = Sprite('door', 'door', '문', OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE)
                                                Door.map_to(True, Factory.MAP_ID)
                                                Door.teleport(OBJECT.RECT.x, OBJECT.RECT.y)
                                                Door.LOCKED = True if random.randrange(0, 20) == 0 else False

                                                FACTORY['OBJECTS'].remove(OBJECT)
                                            
                                            # 아이템 생성
                                            for IDX in range(0, 50):
                                                RECT_X = random.randrange(1, OUTPUT[1]) * 100
                                                RECT_Y = random.randrange(1, OUTPUT[2]) * 100

                                                if not Factory.MAP_ARRAY[int(RECT_Y / 100)][int(RECT_X / 100)] == FACTORY_WALL:
                                                    Array = [
                                                        { 'ID': 'key', 'DISPLAY_NAME': '열쇠', 'IMAGE': KEY_IMAGE },
                                                        { 'ID': 'stop', 'DISPLAY_NAME': '정지 표지판', 'IMAGE': STOP_IMAGE },
                                                        { 'ID': 'airhorn', 'DISPLAY_NAME': '에어혼', 'IMAGE': AIRHORN_IMAGE },
                                                        { 'ID': 'bigbolt', 'DISPLAY_NAME': '큰 나사', 'IMAGE': BIGBOLT_IMAGE },
                                                        { 'ID': 'clownhorn', 'DISPLAY_NAME': '광대 나팔', 'IMAGE': CLOWNHORN_IMAGE },
                                                        { 'ID': 'coffee mug', 'DISPLAY_NAME': '머그컵', 'IMAGE': COFFEE_MUG_IMAGE },
                                                        { 'ID': 'comedy', 'DISPLAY_NAME': '희극', 'IMAGE': COMEDY_IMAGE },
                                                        { 'ID': 'flask', 'DISPLAY_NAME': '플라스크', 'IMAGE': FLASK_IMAGE },
                                                        { 'ID': 'giftbox', 'DISPLAY_NAME': '선물 상자', 'IMAGE': GIFTBOX_IMAGE },
                                                        { 'ID': 'whoopie cushion', 'DISPLAY_NAME': '방귀 쿠션', 'IMAGE': WHOOPIE_CUSHION_IMAGE },
                                                        { 'ID': 'cube', 'DISPLAY_NAME': '장난감 큐브', 'IMAGE': CUBE_IMAGE },
                                                        { 'ID': 'toothpaste', 'DISPLAY_NAME': '치약', 'IMAGE': TOOTHPASTE_IMAGE },
                                                        { 'ID': 'kettle', 'DISPLAY_NAME': '찻주전자', 'IMAGE': KETTLE_IMAGE },
                                                        { 'ID': 'duck', 'DISPLAY_NAME': '장난감 오리', 'IMAGE': DUCK_IMAGE },
                                                        { 'ID': 'ring', 'DISPLAY_NAME': '약혼 반지', 'IMAGE': RING_IMAGE },
                                                        { 'ID': 'soda', 'DISPLAY_NAME': '소다', 'IMAGE': SODA_IMAGE },
                                                        { 'ID': 'plastic fish', 'DISPLAY_NAME': '플라스틱 물고기', 'IMAGE': PLASTIC_FISH_IMAGE },
                                                        { 'ID': 'medicine', 'DISPLAY_NAME': '약통', 'IMAGE': MEDICINE_IMAGE },
                                                        { 'ID': 'homesick', 'DISPLAY_NAME': '향수병', 'IMAGE': HOMESICK_IMAGE },
                                                        { 'ID': 'reading glasses', 'DISPLAY_NAME': '돋보기', 'IMAGE': READING_GLASSES_IMAGE },
                                                        { 'ID': 'ball seven', 'DISPLAY_NAME': '마법의 7번공', 'IMAGE': BALL_SEVEN_IMAGE },
                                                        { 'ID': 'hair dryer', 'DISPLAY_NAME': '헤어드라이기', 'IMAGE': HAIR_DRYER_IMAGE },
                                                        { 'ID': 'hair comb', 'DISPLAY_NAME': '빗', 'IMAGE': HAIR_COMB_IMAGE },
                                                        { 'ID': 'golden cup', 'DISPLAY_NAME': '황금 컵', 'IMAGE': GOLDEN_CUP_IMAGE },
                                                        { 'ID': 'egg beater', 'DISPLAY_NAME': '달걀 거품기', 'IMAGE': EGG_BEATER_IMAGE },
                                                        { 'ID': 'brass bell', 'DISPLAY_NAME': '황동 종', 'IMAGE': BRASS_BELL_IMAGE }
                                                    ]
                                                    ITEM = Array[random.randrange(len(Array))]

                                                    Item = Sprite(ITEM['ID'], 'item', ITEM['DISPLAY_NAME'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'])
                                                    Item.map_to(True, Factory.MAP_ID)
                                                    Item.teleport(RECT_X, RECT_Y)
                                                    Item.PRICE = random.randrange(3, 70)

                                            # 몬스터 생성
                                            for IDX in range(0, 15):
                                                RECT_X = random.randrange(1, OUTPUT[1]) * 100
                                                RECT_Y = random.randrange(1, OUTPUT[2]) * 100

                                                if not Factory.MAP_ARRAY[int(RECT_Y / 100)][int(RECT_X / 100)] == FACTORY_WALL:
                                                    rand = random.randrange(0, 4)

                                                    if rand == 0:
                                                        HoardingBug = Sprite('hoarding bug', 'monster', '비축벌레', HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE)
                                                        HoardingBug.map_to(True, Factory.MAP_ID)
                                                        HoardingBug.teleport(RECT_X, RECT_Y)
                                                        HoardingBug.SPEED = 1

                                                    elif rand == 1:
                                                        CoilHead = Sprite('coil head', 'monster', '코일헤드', COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE)
                                                        CoilHead.map_to(True, Factory.MAP_ID)
                                                        CoilHead.teleport(RECT_X, RECT_Y)
                                                        CoilHead.INVINCIBILITY = True
                                                        CoilHead.DAMAGE = 100
                                                        CoilHead.SPEED = 3

                                                    elif rand == 2:
                                                        Bracken = Sprite('bracken', 'monster', '브레켄', BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE)
                                                        Bracken.map_to(True, Factory.MAP_ID)
                                                        Bracken.teleport(RECT_X, RECT_Y)
                                                        Bracken.DAMAGE = 100
                                                        Bracken.SPEED = 2
                                                    
                                                    elif rand == 3:
                                                        Jester = Sprite('jester', 'monster', '제스터', JESTER_IMAGE, JESTER_IMAGE, JESTER_IMAGE, JESTER_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE)
                                                        Jester.map_to(True, Factory.MAP_ID)
                                                        Jester.teleport(RECT_X, RECT_Y)
                                                        Jester.INVINCIBILITY = True
                                                        Jester.DAMAGE = 0
                                                        Jester.SPEED = 1
                                    
                                    else:
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        함선이 이동한 다음에만 착륙할 수 있습니다.'''
                                
                                elif INGAME['COMMAND'] == 'take-off':
                                    if INGAME['CUR_MOD'] == 'OK':
                                        SHIP = INGAME['MAPS'][Map.reduced('ID').index('ship')]
                                        for ITEM in INGAME['SAVES']:
                                            if INGAME['CUR_MAP'] == 'experimentation':
                                                ITEM.RECT.x -= 200
                                                ITEM.RECT.y -= 1800
                                                SHIP['OBJECTS'].append(ITEM)
                                            
                                            elif INGAME['CUR_MAP'] == 'company':
                                                ITEM.RECT.x -= 2500
                                                ITEM.RECT.y -= 5300
                                                SHIP['OBJECTS'].append(ITEM)
                                        
                                        if INGAME['CUR_MAP'] == 'experimentation':
                                            INGAME['SURVIVAL_RESULT'] = True
                                            def survival_result_false():
                                                INGAME['SURVIVAL_RESULT'] = False

                                                INGAME['DAY'] -= 1
                                                INGAME['DAY_RESULT'] = True
                                                def day_result_false():
                                                    INGAME['DAY_RESULT'] = False
                                                Timer(4, day_result_false).start()
                                            Timer(5, survival_result_false).start()
                                        
                                        elif INGAME['CUR_MAP'] == 'company':
                                            INGAME['SURVIVAL_RESULT'] = True
                                            def survival_result_false():
                                                INGAME['SURVIVAL_RESULT'] = False

                                                INGAME['DAY'] = 3
                                                INGAME['MONEY'] += INGAME['QUOTA']
                                                INGAME['QUOTA'] = 0
                                                INGAME['TARGET_QUOTA'] *= 2.5
                                                INGAME['TARGET_QUOTA'] = int(INGAME['TARGET_QUOTA'])
                                                INGAME['QUOTA_RESULT'] = True
                                                def day_result_false():
                                                    INGAME['QUOTA_RESULT'] = False
                                                Timer(4, day_result_false).start()
                                            Timer(5, survival_result_false).start()
                                        
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        함선이 이륙합니다.'''

                                        NOISE_2.play()

                                        INGAME['TERMINAL'] = False

                                        Player.map_to(False, Ship.MAP_ID)
                                        if INGAME['CUR_MAP'] == 'experimentation': Player.teleport(Player.RECT.x - 200, Player.RECT.y - 1800)
                                        elif INGAME['CUR_MAP'] == 'company': Player.teleport(Player.RECT.x - 2500, Player.RECT.y - 5300)
                                        
                                        INGAME['CUR_MAP'] = Ship.MAP_ID
                                        INGAME['CUR_MOD'] = 'READY'

                                        INGAME['TIME'] = 60 * 8
                                    
                                    else:
                                        INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                        
                                        착륙한 후에만 이륙할 수 있습니다.'''

                                else:
                                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                    알 수 없는 명령어 \'{INGAME['COMMAND']}\'.'''

                                INGAME['COMMAND'] = ''
                            
                            # 입력 제한
                            elif len(INGAME['COMMAND']) <= 30:
                                INGAME['COMMAND'] += str(pygame.key.name(event.key))
                        
                        # 인게임에 입력
                        else:
                            # 공격
                            if event.key == pygame.K_r:
                                if CUR_ITEM_EXISTS:
                                    CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                    if CUR_ITEM.ID in ['shovel', 'stop']:
                                        for MONSTER in CUR_MAP['OBJECTS']:
                                            dist = distance(Player.RECT, MONSTER.RECT)

                                            if dist < Player.ATTACK_DISTANCE:
                                                if MONSTER.TYPE == 'monster':
                                                    if not MONSTER.INVINCIBILITY:
                                                        MONSTER.HP -= Player.DAMAGE

                                                        if MONSTER.HP < 0:
                                                            CUR_MAP['OBJECTS'].remove(MONSTER)
                            
                            # e키 상호작용
                            if event.key == pygame.K_e and Player.CONTAIN:
                                # 터미널 초기화
                                if Player.CONTAIN.TYPE == 'terminal':
                                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                    
                                    > MOONS
                                    행성 목록을 보여줍니다.
                                    현재는 익스페리멘테이션만 가능합니다.

                                    > STORE
                                    구매할 아이템 목록을 보여줍니다.
                                    주문을 완료하면 하늘에서 배달이 옵니다.
                                    
                                    > LAND
                                    함선이 지정된 행성으로 착륙합니다.
                                    
                                    > TAKE-OFF
                                    함선이 이륙합니다.'''
                                    INGAME['TERMINAL'] = True

                                # 문
                                elif Player.CONTAIN.TYPE == 'door':
                                    DOOR_IDX = CUR_MAP['OBJECTS'].index(Player.CONTAIN)
                                    DOOR = CUR_MAP['OBJECTS'][DOOR_IDX]

                                    # 열려있다면
                                    if DOOR.OPENED:
                                        DOOR.OPENED = False

                                        IMAGE = DOOR_IMAGE
                                        if DOOR.FRONT_IMAGE == DOOR_2_IMAGE: IMAGE = DOOR_2_IMAGE
                                        DOOR.CUR_IMAGE = IMAGE
                                    
                                    # 닫혀있다면
                                    else:
                                        # 잠겨있다면
                                        if DOOR.LOCKED:
                                            if CUR_ITEM_EXISTS:
                                                CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                                # 키를 들고 있다면
                                                if CUR_ITEM.ID == 'key':
                                                    Player.INVENTORY.remove(CUR_ITEM)
                                                    DOOR.LOCKED = False

                                                    if len(Player.INVENTORY) < Player.CUR_ITEM_IDX + 1:
                                                        CUR_ITEM_EXISTS = False

                                        # 잠겨있지 않다면
                                        else:
                                            DOOR.OPENED = True

                                            IMAGE = OPENED_DOOR_IMAGE
                                            if DOOR.FRONT_IMAGE == DOOR_2_IMAGE: IMAGE = OPENED_DOOR_2_IMAGE
                                            DOOR.CUR_IMAGE = IMAGE
                                
                                # 입장
                                elif Player.CONTAIN.TYPE == 'enter':
                                    DELIVERY_MUSIC.stop()
                                    NOISE.stop()
                                    MAIN_MUSIC_1.stop()
                                    MAIN_MUSIC_2.stop()

                                    # 공장 로비 사운드 재생
                                    LOBBY_MUSIC_3.play(loops=-1)
                                    METAL_DOOR_SHUT.play()

                                    Player.map_to(False, Factory.MAP_ID)
                                    Player.teleport(100, 300)
                                    Player.SPEED = 2
                                    
                                    INGAME['CUR_MAP'] = Factory.MAP_ID
                                    INGAME['CUR_MOD'] = 'FARMING'
                                
                                # 나가기
                                elif Player.CONTAIN.TYPE == 'exit':
                                    LOBBY_MUSIC_3.stop()
                                    METAL_DOOR_CLOSE.play()

                                    Player.map_to(False, INGAME['NEXT_MAP'])
                                    Player.teleport(3800, 2100)
                                    Player.SPEED = 1
                                    
                                    INGAME['CUR_MAP'] = INGAME['NEXT_MAP']
                                    INGAME['CUR_MOD'] = 'OK'
                                
                                # 배달
                                elif Player.CONTAIN.TYPE == 'delivery':
                                    def delivery_landing_false():
                                        INGAME['DELIVERY_LANDING'] = False
                                        
                                    Timer(20, delivery_landing_false).start()
                                    
                                    if INGAME['CUR_MAP'] == 'experimentation':
                                        for ITEM in Delivery.INVENTORY:
                                            if ITEM.ID in ['stop', 'shovel']: DROP_SHOVEL.play()
                                            if ITEM.ID == 'key': DROP_KEY.play()
                                            if ITEM.ID == 'bottle': DROP_BOTTLE.play()
                                            if ITEM.ID == 'flashlight': DROP_FLASHLIGHT.play()

                                            ITEM.RECT.x = Delivery.RECT.x
                                            ITEM.RECT.y = Delivery.RECT.y
                                            CUR_MAP['OBJECTS'].append(ITEM)
                                        Delivery.INVENTORY = []
                                    
                                    elif INGAME['CUR_MAP'] == 'company':
                                        for ITEM in Delivery2.INVENTORY:
                                            if ITEM.ID in ['stop', 'shovel']: DROP_SHOVEL.play()
                                            if ITEM.ID == 'key': DROP_KEY.play()
                                            if ITEM.ID == 'bottle': DROP_BOTTLE.play()
                                            if ITEM.ID == 'flashlight': DROP_FLASHLIGHT.play()

                                            ITEM.RECT.x = Delivery2.RECT.x
                                            ITEM.RECT.y = Delivery2.RECT.y
                                            CUR_MAP['OBJECTS'].append(ITEM)
                                        Delivery2.INVENTORY = []
                                
                                # 충전
                                elif Player.CONTAIN.TYPE == 'charger':
                                    if CUR_ITEM_EXISTS:
                                        CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                        if CUR_ITEM.ID == 'flashlight':
                                            INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])

                                            INGAME['CHARGING'] = True

                                            def charging_false():
                                                INGAME['CHARGING'] = False

                                            def charge_item():
                                                Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE = 100
                                            
                                            Player.CUR_IMAGE = Player.BACK_WALK_IMAGE
                                            Player.LAST_ROTATE = 'back'
                                            
                                            Timer(2, charging_false).start()
                                            Timer(1, charge_item).start()
                                
                                # 올려두기
                                elif Player.CONTAIN.TYPE == 'salemanager':
                                    if CUR_ITEM_EXISTS:
                                        CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]
                                        Player.drop_item(CUR_ITEM)
                                        CUR_ITEM_EXISTS = False
                                        CUR_ITEM.RECT.x = 4900 + random.randrange(0, 75)
                                        CUR_ITEM.RECT.y = 5100 + random.randrange(0, 100)
                                        CUR_ITEM.TYPE = 'sold'

                                        def sale_items():
                                            SUM = 0

                                            for ITEM in CUR_MAP['OBJECTS']:
                                                if ITEM.TYPE == 'sold': SUM += ITEM.PRICE
                                            
                                            for ITEM in CUR_MAP['OBJECTS']:
                                                if ITEM.TYPE == 'sold': CUR_MAP['OBJECTS'].remove(ITEM)
                                            
                                            INGAME['QUOTA'] += SUM
                                        
                                        Timer(10, sale_items).start()
                                
                                # 아이템 수집
                                elif len(Player.INVENTORY) < 8:
                                    # 플레이어가 함선 안에 있는지
                                    RECT = pygame.Rect(0, 0, 1100, 700)
                                    if INGAME['CUR_MAP'] == 'experimentation': RECT = pygame.Rect(200, 1800, 1100, 700)
                                    elif INGAME['CUR_MAP'] == 'company': RECT = pygame.Rect(2500, 5300, 1100, 700)  
                                    print(INGAME['SAVES'], Player.CONTAIN)
                                    if not INGAME['CUR_MAP'] == 'factory' and RECT.collidepoint(Player.CONTAIN.RECT.x, Player.CONTAIN.RECT.y): INGAME['SAVES'].remove(Player.CONTAIN)

                                    Player.grab_item()

                            # g키 버리기
                            if event.key == pygame.K_g and len(Player.INVENTORY) > 0:
                                if CUR_ITEM_EXISTS:
                                    CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                    if CUR_ITEM:
                                        Player.drop_item(CUR_ITEM)

                                        if len(Player.INVENTORY) < Player.CUR_ITEM_IDX + 1:
                                            CUR_ITEM_EXISTS = False
                                        
                                        # 플레이어가 함선 안에 있는지
                                        RECT = pygame.Rect(0, 0, 1100, 700)
                                        if INGAME['CUR_MAP'] == 'experimentation': RECT = pygame.Rect(200, 1800, 1100, 700)
                                        elif INGAME['CUR_MAP'] == 'company': RECT = pygame.Rect(2500, 5300, 1100, 700)
                                        if not INGAME['CUR_MAP'] == 'factory' and RECT.collidepoint(CUR_ITEM.RECT.x, CUR_ITEM.RECT.y): INGAME['SAVES'].append(CUR_ITEM)
                            
                            # f키 손전등
                            if event.key == pygame.K_f:
                                if CUR_ITEM_EXISTS:
                                    CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                    if CUR_ITEM:
                                        if CUR_ITEM.ID == 'flashlight':
                                            Player.FLASHLIGHT = not Player.FLASHLIGHT

                                            FLASHLIGHT_CLICK.play()
                            
                            # q키 스캔
                            if event.key == pygame.K_q and not INGAME['SCAN']:
                                INGAME['SCAN'] = True
                                def scan_false():
                                    INGAME['SCAN'] = False
                                Timer(2, scan_false).start()

                            # 아이템 선택
                            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                                Player.CUR_ITEM_IDX = int(pygame.key.name(event.key)) - 1

            # 터미널이 안열려있으면
            sum_text = font.render('', True, (255, 255, 255))
            if not INGAME['TERMINAL']:
                if INGAME['CAMERA_MOVE']:
                    if INGAME['CUR_MAP'] == 'experimentation':
                        if INGAME['CAMERA_X'] <= -700:
                            INGAME['CAMERA_MOVE'] = False

                            def camera_move_false():
                                INGAME['CAMERA_X'] = 0
                                INGAME['CAMERA_Y'] = 0
                            
                            Timer(2, camera_move_false).start()
                        
                        else: INGAME['CAMERA_X'] -= 2

                        if Open1.RECT.y >= 1900:
                            Open1.RECT.y -= 1

                        if Open2.RECT.y <= 2300:
                            Open2.RECT.y += 1
                    
                    elif INGAME['CUR_MAP'] == 'company':
                        if INGAME['CAMERA_X'] <= -700:
                            INGAME['CAMERA_MOVE'] = False

                            def camera_move_false():
                                INGAME['CAMERA_X'] = 0
                                INGAME['CAMERA_Y'] = 0
                            
                            Timer(2, camera_move_false).start()
                        
                        else: INGAME['CAMERA_X'] -= 2

                        if Open3.RECT.y >= 5400:
                            Open3.RECT.y -= 1

                        if Open4.RECT.y <= 5800:
                            Open4.RECT.y += 1
                
                # 카메라 시점 계산
                OFFSET_X = CONFIG['SCREEN_WIDTH'] // 2 - Player.RECT.centerx + INGAME['CAMERA_X']
                OFFSET_Y = CONFIG['SCREEN_HEIGHT'] // 2 - Player.RECT.centery + INGAME['CAMERA_Y']

                # 타일 그리기
                for Y, ROW in enumerate(CUR_MAP['ARRAY']):
                    for X, TILE in enumerate(ROW):
                        RECT = (X * CONFIG['TILE_SIZE'] + OFFSET_X, Y * CONFIG['TILE_SIZE'] + OFFSET_Y)
                        dist = distance(Player.RECT, pygame.Rect(X * CONFIG['TILE_SIZE'], Y * CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE']))

                        if dist < Player.DISTANCE or not INGAME['CAMERA_X'] == 0:
                            if CUR_MAP['ID'] == 'ship':
                                TILE_IMAGE.render(screen, RECT)
                                if TILE == SHIP_WALL: WALL_IMAGE.render(screen, RECT)
                                elif TILE == SHIP_TERMINAL: TERMINAL_IMAGE.render(screen, RECT)

                            if CUR_MAP['ID'] == 'experimentation':
                                SAND_IMAGE.render(screen, RECT)
                                if TILE == EXPERIMENTATION_WALL: WALL_IMAGE.render(screen, RECT)
                                if TILE == EXPERIMENTATION_TILE: TILE_IMAGE.render(screen, RECT)
                            
                            if CUR_MAP['ID'] == 'factory':
                                TILE_IMAGE.render(screen, RECT)
                                if TILE == FACTORY_WALL: WALL_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_DOOR: DOOR_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_PIPE1: PIPE1_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_PIPE2: PIPE2_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_PIPE3: PIPE3_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_WEB1: WEB1_IMAGE.render(screen, RECT)
                                elif TILE == FACTORY_WEB2: WEB2_IMAGE.render(screen, RECT)
                            
                            if CUR_MAP['ID'] == 'company':
                                TILE_2_IMAGE.render(screen, RECT)
                                if TILE == COMPANY_TILE: TILE_IMAGE.render(screen, RECT)
                                if TILE == COMPANY_WALL: WALL_IMAGE.render(screen, RECT)

                # 현재 맵에 존재하는 오브젝트들
                for OBJECT in CUR_MAP['OBJECTS']:
                    text = None

                    # 카메라 시점에 대한 오브젝트 위치
                    OBJECT_RECT = OBJECT.RECT.move(OFFSET_X, OFFSET_Y)

                    # 배달이라면
                    if OBJECT.TYPE == 'delivery':
                        if INGAME['DELIVERY']:
                            if INGAME['CUR_MAP'] == 'experimentation':
                                if INGAME['DELIVERY_LANDING']:
                                    # 착륙
                                    if Delivery.RECT.y >= 2000: Delivery.CUR_IMAGE = Delivery.FRONT_IMAGE
                                    # 하늘에서 날라오기
                                    else: Delivery.move(0, Delivery.SPEED, True)
                                
                                else:
                                    DELIVERY_MUSIC.stop()
                                    # 이륙
                                    if Delivery.RECT.y <= -1000: Delivery.CUR_IMAGE = Delivery.FRONT_IMAGE
                                    # 하늘로 날라가기
                                    else: Delivery.move(0, -Delivery.SPEED, True)
                            
                            elif INGAME['CUR_MAP'] == 'company':
                                if INGAME['DELIVERY_LANDING']:
                                    # 착륙
                                    if Delivery2.RECT.y >= 5400: Delivery2.CUR_IMAGE = Delivery2.FRONT_IMAGE
                                    # 하늘에서 날라오기
                                    else: Delivery2.move(0, Delivery2.SPEED, True)
                                
                                else:
                                    DELIVERY_MUSIC.stop()
                                    # 이륙
                                    if Delivery2.RECT.y <= -1000: Delivery2.CUR_IMAGE = Delivery2.FRONT_IMAGE
                                    # 하늘로 날라가기
                                    else: Delivery2.move(0, -Delivery2.SPEED, True)

                    # 플레이어라면
                    if OBJECT.TYPE == 'player':
                        # 플레이어 이동
                        if not Player.DIED and INGAME['CAMERA_X'] == 0 and not INGAME['CHARGING']:
                            if keys[pygame.K_w]: Player.move(0, -Player.SPEED)
                            if keys[pygame.K_s]: Player.move(0, Player.SPEED)
                            if keys[pygame.K_a]: Player.move(-Player.SPEED, 0)
                            if keys[pygame.K_d]: Player.move(Player.SPEED, 0)

                            if keys[pygame.K_UP]:
                                Player.CUR_IMAGE = Player.BACK_WALK_IMAGE
                                Player.LAST_ROTATE = 'back'
                            if keys[pygame.K_DOWN]:
                                Player.CUR_IMAGE = Player.FRONT_WALK_IMAGE
                                Player.LAST_ROTATE = 'front'
                            if keys[pygame.K_LEFT]:
                                Player.CUR_IMAGE = Player.LEFT_WALK_IMAGE
                                Player.LAST_ROTATE = 'left'
                            if keys[pygame.K_RIGHT]:
                                Player.CUR_IMAGE = Player.RIGHT_WALK_IMAGE
                                Player.LAST_ROTATE = 'right'

                        if CONFIG['DEBUG']: pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], Player.ATTACK_DISTANCE, 1)
                        
                        for ITEM in CUR_MAP['OBJECTS']:
                            # 플레이어 원형 경계
                            dist = distance(Player.RECT, ITEM.RECT)

                            if dist < Player.ATTACK_DISTANCE:
                                # 단축키 + 메시지 표시
                                if ITEM.TYPE == 'item':
                                    shortcut = '(E)'

                                    if len(OBJECT.INVENTORY) == 8: shortcut = '(가득참)'
                                    OBJECT.CONTAIN = ITEM

                                    text = font.render(f'{shortcut} {ITEM.DISPLAY_NAME} 들기', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'terminal':
                                    OBJECT.CONTAIN = ITEM

                                    text = font.render('(E) 터미널 사용하기', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'door':
                                    OBJECT.CONTAIN = ITEM

                                    shortcut = '(E)'
                                    if ITEM.LOCKED: shortcut = '(잠김)'

                                    message = '문 열기'
                                    if ITEM.OPENED: message = '문 닫기'
                                    
                                    text = font.render(f'{shortcut} {message}', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'enter':
                                    OBJECT.CONTAIN = ITEM

                                    text = font.render('(E) 입장하기', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'exit':
                                    OBJECT.CONTAIN = ITEM

                                    text = font.render('(E) 나가기', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'delivery':
                                    OBJECT.CONTAIN = ITEM

                                    text = font.render('(E) 열기', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'charger':
                                    OBJECT.CONTAIN = ITEM

                                    shortcut = '(E)'
                                    message = '충전할 수 있는 아이템이 아닙니다.'

                                    if CUR_ITEM_EXISTS:
                                        CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                        if CUR_ITEM.ID == 'flashlight':
                                            message = '충전하기'

                                    text = font.render(f'{shortcut} {message}', True, (255, 255, 255))
                                    break

                                elif ITEM.TYPE == 'salemanager':
                                    OBJECT.CONTAIN = ITEM
                                    
                                    text = font.render('(E) 올려두기', True, (255, 255, 255))
                                    break

                            else: OBJECT.CONTAIN = None
                        
                        # 키를 누르고 있지 않다면
                        if not (keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]):
                            OBJECT.WALKING = False

                        # 걷고있지 않다면
                        if not OBJECT.WALKING:
                            if OBJECT.LAST_ROTATE == 'front': OBJECT.CUR_IMAGE = OBJECT.FRONT_IMAGE
                            if OBJECT.LAST_ROTATE == 'back': OBJECT.CUR_IMAGE = OBJECT.BACK_IMAGE
                            if OBJECT.LAST_ROTATE == 'left': OBJECT.CUR_IMAGE = OBJECT.LEFT_IMAGE
                            if OBJECT.LAST_ROTATE == 'right': OBJECT.CUR_IMAGE = OBJECT.RIGHT_IMAGE

                    # 몬스터라면 (제작중)
                    elif OBJECT.TYPE == 'monster':
                        if CONFIG['DEBUG']:
                            pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], OBJECT.DISTANCE, 1)
                            pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], OBJECT.ATTACK_DISTANCE, 1)
                        
                        dist = distance(OBJECT.RECT, Player.RECT)

                        # 비축벌레
                        if OBJECT.ID == 'hoarding bug':
                            # print(int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE']))
                            # print(astar([Factory.MAP_ARRAY], (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])), (5, 5)))
                            ...

                        # 코일헤드
                        if OBJECT.ID == 'coil head':
                            # 공격
                            if dist < OBJECT.ATTACK_DISTANCE and OBJECT.TRACK:
                                Player.DECREASING = True
                                Player.DECREASING_SIZE = OBJECT.DAMAGE
                                
                                if Player.HP < 0:
                                    Player.DIED = True
                                    
                                    for CUR_ITEM_IDX, CUR_ITEM in enumerate(Player.INVENTORY):
                                        Player.drop_item(CUR_ITEM)
                                    
                                    CUR_ITEM_EXISTS = False

                                    def resurrection():
                                        Player.DIED = False

                                        WILL_REMOVES = []
                                        for ITEM in INGAME['SAVES']:
                                            if ITEM.ID in ['key', 'flashlight', 'shovel']:
                                                WILL_REMOVES.append(ITEM)
                                        
                                        for ITEM in WILL_REMOVES:
                                            INGAME['SAVES'].remove(ITEM)
                                        
                                        Player.map_to(False, Ship.MAP_ID)
                                        Player.teleport(1100 // 2, 700 // 2)
                                    
                                    Timer(2, resurrection)
                            else: Player.DECREASING = False

                            # 추적
                            if dist < OBJECT.DISTANCE:
                                if Player.RECT.x > OBJECT.RECT.x: OBJECT.move(OBJECT.SPEED, 0)
                                if Player.RECT.x < OBJECT.RECT.x: OBJECT.move(-OBJECT.SPEED, 0)
                                if Player.RECT.y > OBJECT.RECT.y: OBJECT.move(0, OBJECT.SPEED)
                                if Player.RECT.y < OBJECT.RECT.y: OBJECT.move(0, -OBJECT.SPEED)
                            else: OBJECT.WALKING = False
                            
                            if dist < OBJECT.DISTANCE: OBJECT.TRACK = True
                            else: OBJECT.TRACK = False

                            if dist < OBJECT.DISTANCE:
                                if OBJECT.TRACK and Player.LAST_ROTATE == 'front':
                                    if Player.RECT.y < OBJECT.RECT.y:
                                        OBJECT.SPEED = 0
                                        if not OBJECT.ALREADY_PLAY: COILHEAD_ATTACK_1.play()
                                        OBJECT.ALREADY_PLAY = True
                                    else:
                                        OBJECT.SPEED = 3
                                        OBJECT.ALREADY_PLAY = False

                                elif OBJECT.TRACK and Player.LAST_ROTATE == 'back':
                                    if Player.RECT.y > OBJECT.RECT.y:
                                        OBJECT.SPEED = 0
                                        if not OBJECT.ALREADY_PLAY: COILHEAD_ATTACK_2.play()
                                        OBJECT.ALREADY_PLAY = True
                                    else:
                                        OBJECT.SPEED = 3
                                        OBJECT.ALREADY_PLAY = False

                                elif OBJECT.TRACK and Player.LAST_ROTATE == 'left':
                                    if Player.RECT.x > OBJECT.RECT.x:
                                        OBJECT.SPEED = 0
                                        if not OBJECT.ALREADY_PLAY: COILHEAD_ATTACK_1.play()
                                        OBJECT.ALREADY_PLAY = True
                                    else:
                                        OBJECT.SPEED = 3
                                        OBJECT.ALREADY_PLAY = False

                                elif OBJECT.TRACK and Player.LAST_ROTATE == 'right':
                                    if Player.RECT.x < OBJECT.RECT.x:
                                        OBJECT.SPEED = 0
                                        if not OBJECT.ALREADY_PLAY: COILHEAD_ATTACK_2.play()
                                        OBJECT.ALREADY_PLAY = True
                                    else:
                                        OBJECT.SPEED = 3
                                        OBJECT.ALREADY_PLAY = False
                    
                    # 오브젝트 이미지 그리기
                    dist = distance(Player.RECT, OBJECT.RECT)

                    if dist < Player.DISTANCE or not INGAME['CAMERA_X'] == 0:
                        if OBJECT.TYPE == 'door' and OBJECT.OPENED:
                            RECT_X = OBJECT_RECT.x + 50
                            RECT_Y = OBJECT_RECT.y

                            if OBJECT.CUR_IMAGE == OPENED_DOOR_2_IMAGE:
                                RECT_X -= 50
                                RECT_Y -= 50
                                
                            OBJECT.CUR_IMAGE.render(screen, (RECT_X, RECT_Y))
                        elif not OBJECT.DIED: OBJECT.CUR_IMAGE.render(screen, OBJECT_RECT)

                    if CONFIG['DEBUG']: pygame.draw.rect(screen, (255, 255, 0), OBJECT_RECT, 1)

                    # 스캔 정보 표시
                    if INGAME['SCAN'] and dist < Player.DISTANCE and OBJECT.TYPE == 'item':
                        pygame.draw.circle(screen, (0, 255, 0), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 75, 1)
                        pygame.draw.circle(screen, (0, 255, 0), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 85, 1)
                        pygame.draw.circle(screen, (0, 255, 0), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 130, 1)
                        pygame.draw.rect(screen, (0, 255, 0), (OBJECT_RECT.x + 125, OBJECT_RECT.y - 50, 200, 100))

                        # 정보
                        text_ = font.render(OBJECT.DISPLAY_NAME, True, (0, 0, 0))
                        screen.blit(text_, (OBJECT_RECT.x + 150, OBJECT_RECT.y - 25))
                        text_ = font.render(f'${str(OBJECT.PRICE)}', True, (0, 0, 0))
                        screen.blit(text_, (OBJECT_RECT.x + 150, OBJECT_RECT.y))

                        # 합계
                        SUM = 0
                        for ITEM in CUR_MAP['OBJECTS']:
                            dist = distance(Player.RECT, ITEM.RECT)
                            if ITEM.TYPE == 'item' and dist < Player.DISTANCE: SUM += ITEM.PRICE
                        
                        sum_text = font.render(f'합계: ${str(SUM)}', True, (255, 255, 255))

                    # 아이템 상호작용 표시
                    if text and Player.CONTAIN: screen.blit(text, (Player.CONTAIN.RECT.centerx + OFFSET_X - (text.get_size()[0] / 2), Player.CONTAIN.RECT.y + OFFSET_Y - 50))
            
            # 레터박스
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, (CONFIG['SCREEN_WIDTH'] / 2) - 450, CONFIG['SCREEN_HEIGHT']))
            pygame.draw.rect(screen, (0, 0, 0), (CONFIG['SCREEN_WIDTH'] - ((CONFIG['SCREEN_WIDTH'] / 2) - 450), 0, (CONFIG['SCREEN_WIDTH'] / 2) - 450, CONFIG['SCREEN_HEIGHT']))

            # 총합계 표시
            if INGAME['SCAN']: screen.blit(sum_text, (50, 80))
            
            # 플레이어가 함선 안에 있는지
            RECT = pygame.Rect(0, 0, 1100, 700)
            if INGAME['CUR_MAP'] == 'experimentation': RECT = pygame.Rect(200, 1800, 1100, 700)
            elif INGAME['CUR_MAP'] == 'company': RECT = pygame.Rect(2500, 5300, 1100, 700)
            IS_SHIP = RECT.collidepoint(Player.RECT.x, Player.RECT.y)
            if INGAME['CUR_MAP'] == 'factory': IS_SHIP = False

            if IS_SHIP:
                # 마감일 표시
                pygame.draw.rect(screen, (255, 255, 255), (CONFIG['SCREEN_WIDTH'] - 400, 50, 100, 100), 1)
                text_ = font.render('마감일', True, (255, 255, 255))
                text2_ = font.render(f'{INGAME["DAY"]}일', True, (255, 255, 255))
                screen.blit(text_, (CONFIG['SCREEN_WIDTH'] - 375, 70))
                screen.blit(text2_, (CONFIG['SCREEN_WIDTH'] - 375, 100))
            
                # 할당량 표시
                pygame.draw.rect(screen, (255, 255, 255), (CONFIG['SCREEN_WIDTH'] - 250, 50, 200, 100), 1)
                text_ = font.render('수익 할당량', True, (255, 255, 255))
                text2_ = font.render(f'${INGAME["QUOTA"]} / ${INGAME["TARGET_QUOTA"]}', True, (255, 255, 255))
                screen.blit(text_, (CONFIG['SCREEN_WIDTH'] - 220, 70))
                screen.blit(text2_, (CONFIG['SCREEN_WIDTH'] - 220, 100))

            # 플레이어가 들고 있는 아이템 표시
            if CUR_ITEM_EXISTS:
                CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]
                if Player.LAST_ROTATE == 'front': OFFSET = (-25, 25)
                if Player.LAST_ROTATE == 'back': OFFSET = (25, -25)
                if Player.LAST_ROTATE == 'left': OFFSET = (-25, 25)
                if Player.LAST_ROTATE == 'right': OFFSET = (25, 25)
                CUR_ITEM.CUR_IMAGE.render(screen, (Player.RECT.x + OFFSET_X + OFFSET[0], Player.RECT.y + OFFSET_Y + OFFSET[1]))

            # 손전등 비네트 효과
            INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])
            if not Player.DIED and not CONFIG['DEBUG'] and INGAME['CUR_MOD'] == 'FARMING':
                if Player.FLASHLIGHT and 'flashlight' in INVENTORY and not Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE == 0: VIGNETTE1_IMAGE.render(screen, ((CONFIG['SCREEN_WIDTH'] // 2) - (CONFIG['SCREEN_HEIGHT'] / 2), (CONFIG['SCREEN_HEIGHT'] // 2) - (CONFIG['SCREEN_HEIGHT'] / 2)))
                else: VIGNETTE2_IMAGE.render(screen, ((CONFIG['SCREEN_WIDTH'] // 2) - (CONFIG['SCREEN_HEIGHT'] / 2), (CONFIG['SCREEN_HEIGHT'] // 2) - (CONFIG['SCREEN_HEIGHT'] / 2)))

            # 인벤토리 아이템 표시
            for IDX, ITEM in enumerate(Player.INVENTORY):
                if ITEM:
                    if Player.CUR_ITEM_IDX == IDX: RGB = (255, 255, 255)
                    else: RGB = (0, 0, 0)

                    ITEM.CUR_IMAGE.render(screen, (50 + IDX * 150, CONFIG['SCREEN_HEIGHT'] - 150))

                pygame.draw.rect(screen, RGB, (50 + IDX * 150, CONFIG['SCREEN_HEIGHT'] - 150, 100, 100), 2)

            # 시간
            if not INGAME['CUR_MAP'] == 'factory' and not INGAME['CUR_MOD'] == 'READY' and not INGAME['CUR_MAP'] == 'company' and not IS_SHIP:
                HOURS = int(INGAME['TIME'] / 60)
                MINUTES = int(INGAME['TIME'] % 60)
                APM = '오전' if HOURS < 12 else '오후'
                DISPLAY_HOURS = f'0{str(HOURS)}' if HOURS < 10 else str(HOURS)
                DISPLAY_MINUTES = f'0{str(MINUTES)}' if MINUTES < 10 else str(MINUTES)
                text = font.render(f'{APM} {str(DISPLAY_HOURS)}:{str(DISPLAY_MINUTES)}', True, (255, 255, 255))
                screen.blit(text, (50, 50))

            # 플레이어 상세
            PLAYER_OUTLINE_IMAGE.render(screen, (50, 130))
            PLAYER_DETAIL_IMAGE.render(screen, (90, 160))

            # 게이지 표시
            INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])
            if 'flashlight' in INVENTORY:
                pygame.draw.rect(screen, (255, 255, 0), (50, 300, 120, 30), 3)
                pygame.draw.rect(screen, (255, 255, 0), (60, 310, Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE, 10))
            
            if INGAME['SURVIVAL_RESULT']:
                pygame.draw.rect(screen, (150, 31, 27), ((CONFIG['SCREEN_WIDTH'] // 2) - 400, CONFIG['SCREEN_HEIGHT'] // 2 - 100, 800, 200))
                text = font4.render('생존', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - 350, CONFIG['SCREEN_HEIGHT'] // 2 - 50))
                text = font2.render('"나".', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - 200, CONFIG['SCREEN_HEIGHT'] // 2 - 50))
                text = font2.render('수익성 높음. 그 외 생략', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - 200, CONFIG['SCREEN_HEIGHT'] // 2))
            
            if INGAME['DAY_RESULT']:
                pygame.draw.rect(screen, (150, 31, 27), ((CONFIG['SCREEN_WIDTH'] // 2) - 450, CONFIG['SCREEN_HEIGHT'] // 2 - 150, 900, 300))
                
                text = font3.render(f'{INGAME['DAY']}일 남음', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - (text.get_size()[0] / 2), CONFIG['SCREEN_HEIGHT'] // 2 - (text.get_size()[1] / 2) - 20))
                
                text = font2.render(f'{INGAME['DAY']} days left', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - (text.get_size()[0] / 2), CONFIG['SCREEN_HEIGHT'] // 2 - (text.get_size()[1] / 2) + 60))
            
            if INGAME['QUOTA_RESULT']:
                pygame.draw.rect(screen, (150, 31, 27), ((CONFIG['SCREEN_WIDTH'] // 2) - 450, CONFIG['SCREEN_HEIGHT'] // 2 - 150, 900, 300))
                
                text = font3.render(f'다음 할당량: ${INGAME['TARGET_QUOTA']}', True, (255, 255, 255))
                screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - (text.get_size()[0] / 2), CONFIG['SCREEN_HEIGHT'] // 2 - (text.get_size()[1] / 2)))

            # 터미널이 열려있다면
            if INGAME['TERMINAL']:
                TERMINAL_SCREEN_IMAGE.render(screen, ((CONFIG['SCREEN_WIDTH'] // 2) - 450, CONFIG['SCREEN_HEIGHT'] // 2 - 450))

                # 한 줄 마다 나눠서 그리기
                for IDX, LINE in enumerate(INGAME['HELP'].split('\n')):
                    text = font.render(LINE.strip(), True, (0, 255, 0))
                    screen.blit(text, (((CONFIG['SCREEN_WIDTH'] // 2) - 450) + 200, ((CONFIG['SCREEN_HEIGHT'] // 2) - 450) + 200 + IDX * 30))
                
                text = font.render(f'> {INGAME["COMMAND"]}', True, (0, 255, 0))
                screen.blit(text, (((CONFIG['SCREEN_WIDTH'] // 2) - 450) + 200, ((CONFIG['SCREEN_HEIGHT'] // 2) - 450) + 700))

        # 중요한 거
        pygame.display.flip()
    # except: ...

pygame.quit()
sys.exit()