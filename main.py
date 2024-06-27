import pygame
import pygame.gfxdraw
import pyautogui
import math
import random
import sys
import time
import uuid
import asyncio
import json
from threading import Timer
from functools import reduce

# 이미지, 사운드
from images import *
from sounds import *
from functions import *

# 전체적인 설정
CONFIG = {
    'SCREEN_WIDTH': pyautogui.size()[0], # 너비
    'SCREEN_HEIGHT': pyautogui.size()[1], # 높이
    'TILE_SIZE': 100, # 타일 사이즈
    'DEBUG': False, # 디버그
    'MASTER_SOUND': 1, # 최대 사운드
    'MIXING': False # 사운드 조절중 여부
}

# 볼륨 믹서
def mixing():
    for SOUND in SOUNDS:
        SOUND.set_volume(CONFIG['MASTER_SOUND'])

with open('data/config.json') as config:
    CONFIG = json.load(config)
    CONFIG['SCREEN_WIDTH'] = pyautogui.size()[0]
    CONFIG['SCREEN_HEIGHT'] = pyautogui.size()[1]
    config.close()
    
    mixing()

def save_config():
    with open('data/config.json', 'w') as config:
        json.dump(CONFIG, config)
        config.close()

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
    'DIFFICULTY': '평화로움', # 난이도
    'SCENES': [], # 씬들
    'CUR_SCENE': '', # 현재 씬
    'PREV_SCENE': '', # 이전 씬
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
    'SAVE_ANIMATION': False, # 저장된 아이템 애니메이션 여부
    'SAVE_ANIMATION_Y': 0, # 저장된 아이템 애니메이션 y
    'SAVE_ITEM': None, # 저장된 아이템
    'SURVIVAL_RESULT': False, # 생존 결과 표시중 여부
    'QUOTA_RESULT': False, # 할당량 결과 표시중 여부
    'DAY_RESULT': False, # 마감일 결과 표시중 여부
    'PREV_HOVER': None, # 인터페이스 마우스 오버 이전 상태
    'LOADING': False, # 로딩중 여부
    'VISIBLE_TILES': [], # 보여지는 타일
    'WARNING': False, # 위험 여부
    'WARNING_ALPHA': 128, # 위험 불투명도
    'WARNING_ALPHA_TOGGLE': False, # 위험 불투명도 토글
    'FIRE': False, # 해고 여부
    'FIRE_MESSAGE': False, # 해고 메시지 표시중 여부
    'FIRE_BUTTON': False, # 해고 버튼 표시중 여부
    'FIRE_BUTTON_RECT': (0, 0, 0, 0), # 해고 버튼 위치
    'FIRE_MESSAGE_IDX': 0, # 해고 메시지 인덱스
    'MIDNIGHT_MESSAGE': False, # 자정 메시지 표시중 여부
    'MIDNIGHT_RUN_MESSAGE': False, # 자정 출발 메시지 표시중 여부
}

ITEM_ARRAY = [
    # { 'ID': 'spear', 'DISPLAY_NAME': '응민이의뭐든지뚫는창', 'IMAGE': SPEAR_IMAGE },

    { 'ID': 'key', 'DISPLAY_NAME': '열쇠', 'IMAGE': KEY_IMAGE, 'PATH': 'images/item/key2.gif' },
    { 'ID': 'stop', 'DISPLAY_NAME': '정지 표지판', 'IMAGE': STOP_IMAGE, 'PATH': 'images/item/stop.gif' },
    { 'ID': 'airhorn', 'DISPLAY_NAME': '에어혼', 'IMAGE': AIRHORN_IMAGE, 'PATH': 'images/item/airhorn.gif' },
    { 'ID': 'bigbolt', 'DISPLAY_NAME': '큰 나사', 'IMAGE': BIGBOLT_IMAGE, 'PATH': 'images/item/bigbolt.gif' },
    { 'ID': 'clownhorn', 'DISPLAY_NAME': '광대 나팔', 'IMAGE': CLOWNHORN_IMAGE, 'PATH': 'images/item/clownhorn.gif' },
    { 'ID': 'coffee mug', 'DISPLAY_NAME': '머그컵', 'IMAGE': COFFEE_MUG_IMAGE, 'PATH': 'images/item/coffee mug.gif' },
    { 'ID': 'comedy', 'DISPLAY_NAME': '희극', 'IMAGE': COMEDY_IMAGE, 'PATH': 'images/item/comedy.gif' },
    { 'ID': 'flask', 'DISPLAY_NAME': '플라스크', 'IMAGE': FLASK_IMAGE, 'PATH': 'images/item/flask.gif' },
    { 'ID': 'giftbox', 'DISPLAY_NAME': '선물 상자', 'IMAGE': GIFTBOX_IMAGE, 'PATH': 'images/item/giftbox.gif' },
    { 'ID': 'whoopie cushion', 'DISPLAY_NAME': '방귀 쿠션', 'IMAGE': WHOOPIE_CUSHION_IMAGE, 'PATH': 'images/item/whoopie_cushion.gif' },
    { 'ID': 'cube', 'DISPLAY_NAME': '장난감 큐브', 'IMAGE': CUBE_IMAGE, 'PATH': 'images/item/cube.gif' },
    { 'ID': 'toothpaste', 'DISPLAY_NAME': '치약', 'IMAGE': TOOTHPASTE_IMAGE, 'PATH': 'images/item/toothpaste.gif' },
    { 'ID': 'kettle', 'DISPLAY_NAME': '찻주전자', 'IMAGE': KETTLE_IMAGE, 'PATH': 'images/item/kettle.gif' },
    { 'ID': 'duck', 'DISPLAY_NAME': '고무 오리', 'IMAGE': DUCK_IMAGE, 'PATH': 'images/item/duck.gif' },
    { 'ID': 'ring', 'DISPLAY_NAME': '약혼 반지', 'IMAGE': RING_IMAGE, 'PATH': 'images/item/ring.gif' },
    { 'ID': 'soda', 'DISPLAY_NAME': '소다', 'IMAGE': SODA_IMAGE, 'PATH': 'images/item/soda.gif' },
    { 'ID': 'plastic fish', 'DISPLAY_NAME': '플라스틱 물고기', 'IMAGE': PLASTIC_FISH_IMAGE, 'PATH': 'images/item/plastic_fish.gif' },
    { 'ID': 'medicine', 'DISPLAY_NAME': '약통', 'IMAGE': MEDICINE_IMAGE, 'PATH': 'images/item/medicine.gif' },
    { 'ID': 'homesick', 'DISPLAY_NAME': '향수병', 'IMAGE': HOMESICK_IMAGE, 'PATH': 'images/item/homesick.gif' },
    { 'ID': 'reading glasses', 'DISPLAY_NAME': '돋보기', 'IMAGE': READING_GLASSES_IMAGE, 'PATH': 'images/item/reading_glasses.gif' },
    { 'ID': 'ball seven', 'DISPLAY_NAME': '마법의 7번공', 'IMAGE': BALL_SEVEN_IMAGE, 'PATH': 'images/item/ball_seven.gif' },
    { 'ID': 'hair dryer', 'DISPLAY_NAME': '헤어드라이기', 'IMAGE': HAIR_DRYER_IMAGE, 'PATH': 'images/item/hair_dryer.gif' },
    { 'ID': 'hair comb', 'DISPLAY_NAME': '빗', 'IMAGE': HAIR_COMB_IMAGE, 'PATH': 'images/item/hair_comb.gif' },
    { 'ID': 'golden cup', 'DISPLAY_NAME': '황금 컵', 'IMAGE': GOLDEN_CUP_IMAGE, 'PATH': 'images/item/golden_cup.gif' },
    { 'ID': 'egg beater', 'DISPLAY_NAME': '달걀 거품기', 'IMAGE': EGG_BEATER_IMAGE, 'PATH': 'images/item/egg_beater.gif' },
    { 'ID': 'brass bell', 'DISPLAY_NAME': '황동 종', 'IMAGE': BRASS_BELL_IMAGE, 'PATH': 'images/item/brass_bell.gif' }
]

ITEM_ARRAY_2 = [
    { 'ID': 'flashlight', 'DISPLAY_NAME': '손전등', 'IMAGE': FLASHLIGHT_IMAGE, 'PATH': 'images/item/flashlight.gif' },
    { 'ID': 'shovel', 'DISPLAY_NAME': '철제 삽', 'IMAGE': SHOVEL_IMAGE, 'PATH': 'images/item/shovel.gif' }
]

with open('data/ingame.json') as ingame:
    INGAME = json.load(ingame)
    ingame.close()

def save_ingame():
    with open('data/ingame.json', 'w') as ingame:
        NEW_INGAME = {}

        for KEY, VALUE in INGAME.items():
            if KEY in ['SCENES', 'SPRITES', 'MAPS', 'STORE', 'VISIBLE_TILES']: NEW_INGAME[KEY] = []
            elif KEY in ['SAVE_ITEM', 'PREV_HOVER']: NEW_INGAME[KEY] = None
            elif KEY == 'RECT': NEW_INGAME[KEY] = (VALUE.x, VALUE.y, VALUE.width, VALUE.height)
            elif KEY == 'RUNNING': NEW_INGAME[KEY] = True
            elif KEY in ['PREV_SCENE', 'CUR_SCENE']: NEW_INGAME[KEY] = ''
            elif KEY in 'CUR_MOD': NEW_INGAME[KEY] = 'READY'
            elif KEY == 'SAVES':
                NEW_SAVES = []
                for ITEM in VALUE: NEW_SAVES.append({ 'UUID': ITEM.UUID.hex, 'ID': ITEM.ID, 'RECT': (ITEM.RECT[0], ITEM.RECT[1], CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE']), 'PRICE': ITEM.PRICE })
                NEW_INGAME[KEY] = NEW_SAVES
            else: NEW_INGAME[KEY] = VALUE

        json.dump(NEW_INGAME, ingame)
        ingame.close()

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
        self.DISTANCE = 5 * CONFIG['TILE_SIZE'] # 넓은 원형 경계 (대부분 추적용)
        self.ATTACK_DISTANCE = .75 * CONFIG['TILE_SIZE'] # 좁은 원형 경계 (공격용)
        self.INTERACTION_DISTANCE = 1.5 * CONFIG['TILE_SIZE'] # 좁은 원형 경계 (상호작용)
        self.TRACK = False # 추적
        self.GUAGE = 100 # 게이지
        self.ALREADY_PLAY = False # 이미 재생함 여부
        self.ALREADY_NOPLAY = True # 아직 재생안함 여부
        self.NAVIGATE = None # a* 알고리즘 네비게이터
        self.NAVIGATE_IDX = 0 # a* 알고리즘 인덱스
        self.NAVIGATE_COLOR = (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)) # a* 알고리즘 색상
        self.SPAWN_POINT = (0, 0) # 스폰포인트
        self.ALREADY_ITEMS = [] # 이미 주웠던 아이템
        self.ALREADY_NAVIGATE = False # 이미 길을 찾음 여부
        self.DOING = False # 무언가 행동중 여부
        self.START_TIME = 0 # 무언가 행동을 시작한 시간
        self.END_TIME = 0 # 무언가 행동을 끝낸 시간
        self.TIMER = False # 타이머
        self.ALREADY_TIMER = False # 이미 타이머 실행됨 여부
        self.TIMEOUT = 20 # 타임아웃
        self.ANGRY = False # 변신 여부
        self.TRANSPARENT = False # 투명화 여부
        self.STACK = 0 # 스택
        self.SOUND = Sound('sounds/Lethal sounds/Sound mine/MineBeep.mp3') # 사운드

        self.FRONT_IMAGE = FRONT_IMAGE
        self.BACK_IMAGE = BACK_IMAGE
        self.LEFT_IMAGE = LEFT_IMAGE
        self.RIGHT_IMAGE = RIGHT_IMAGE
        self.FRONT_WALK_IMAGE = FRONT_WALK_IMAGE
        self.BACK_WALK_IMAGE = BACK_WALK_IMAGE
        self.LEFT_WALK_IMAGE = LEFT_WALK_IMAGE
        self.RIGHT_WALK_IMAGE = RIGHT_WALK_IMAGE

        self.WALK_SOUND = None
        
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
                X = OBJECT.RECT.x / CONFIG['TILE_SIZE']
                Y = OBJECT.RECT.y / CONFIG['TILE_SIZE']

                if CUR_MAP['ID'] == 'ship':
                    if OBJECT.TYPE == 'terminal':
                        self.crash(X, Y, OLD_RECT)
                
                if CUR_MAP['ID'] == 'experimentation':
                    if OBJECT.TYPE in ['enter', 'terminal']:
                        self.crash(X, Y, OLD_RECT)
                
                if CUR_MAP['ID'] == 'factory' and not self.ID == 'girl':
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
        if CUR_ITEM.ID in ['stop', 'shovel']: SOUND = DROP_SHOVEL
        elif CUR_ITEM.ID == 'key': SOUND = DROP_KEY
        elif CUR_ITEM.ID == 'bottle': SOUND = DROP_BOTTLE
        elif CUR_ITEM.ID == 'flashlight': SOUND = DROP_FLASHLIGHT
        elif CUR_ITEM.ID == 'airhorn': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'bigbolt': SOUND = DROP_METAL
        elif CUR_ITEM.ID == 'clownhorn': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'coffee mug': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'comedy': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'flask': SOUND = DROP_BOTTLE
        elif CUR_ITEM.ID == 'giftbox': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'whoopie cushion': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'cube': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'toothpaste': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'kettle': SOUND = DROP_METAL
        elif CUR_ITEM.ID == 'duck': SOUND = DROP_DUCK
        elif CUR_ITEM.ID == 'ring': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'soda': SOUND = DROP_CAN
        elif CUR_ITEM.ID == 'plastic fish': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'medicine': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'homesick': SOUND = DROP_GLASS
        elif CUR_ITEM.ID == 'reading glasses': SOUND = DROP_GLASS
        elif CUR_ITEM.ID == 'ball seven': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'hair dryer': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'hair comb': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'golden cup': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'egg beater': SOUND = DROP_PLASTIC
        elif CUR_ITEM.ID == 'brass bell': SOUND = DROP_BELL
        else: SOUND = DROP_PLASTIC
        VOLUME = get_sound_volume(self.RECT)
        SOUND.set_volume(VOLUME)
        SOUND.play()

        CUR_ITEM.RECT.x = self.RECT.x
        CUR_ITEM.RECT.y = self.RECT.y
        CUR_MAP['OBJECTS'].append(CUR_ITEM)
        self.INVENTORY.remove(CUR_ITEM)
    
    # 아이템 수집
    def grab_item(self):
        SOUND = GRAB_DEFAULT_ITEM
        if self.CONTAIN.ID in ['stop', 'shovel']: SOUND = GRAB_SHOVEL
        elif self.CONTAIN.ID == 'key': SOUND = GRAB_KEY
        elif self.CONTAIN.ID == 'bottle': SOUND = GRAB_BOTTLE
        elif self.CONTAIN.ID == 'flashlight': SOUND = GRAB_FLASHLIGHT
        VOLUME = get_sound_volume(self.RECT)
        SOUND.set_volume(VOLUME)
        SOUND.play()

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

# FOV 계산
def is_in_bounds(X, Y):
    # 현재 맵
    MAP_REDUCED = Map.reduced('ID')
    CUR_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
    CUR_MAP = INGAME['MAPS'][CUR_MAP_IDX]

    return 0 <= X < len(CUR_MAP['ARRAY'][0]) and 0 <= Y < len(CUR_MAP['ARRAY'])

def calculate_fov():
    # 현재 맵
    MAP_REDUCED = Map.reduced('ID')
    CUR_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
    CUR_MAP = INGAME['MAPS'][CUR_MAP_IDX]

    VISIBLE_TILES = set()
    for ANGLE in range(360):
        X, Y = int(Player.RECT.x / CONFIG['TILE_SIZE']) + .5, int(Player.RECT.y / CONFIG['TILE_SIZE']) + .5
        for R in range(9):
            X += math.cos(math.radians(ANGLE))
            Y += math.sin(math.radians(ANGLE))
            if not is_in_bounds(int(X), int(Y)) or CUR_MAP['ARRAY'][int(Y)][int(X)] == 1: break
            VISIBLE_TILES.add((int(X), int(Y)))
    return VISIBLE_TILES

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

MENU_MUSIC.play(-1)

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
Terminal.teleport(2 * CONFIG['TILE_SIZE'], 1 * CONFIG['TILE_SIZE'])

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Ship.MAP_ID)
Charger.teleport(3.25 * CONFIG['TILE_SIZE'], 1 * CONFIG['TILE_SIZE'])

# 익스페리멘테이션 맵
OUTPUT = generate_map('images/map/experimentation.png')
ExperimentationArray = OUTPUT[0]
Experimentation = Map('experimentation', 'experimentation', ExperimentationArray)

# 터미널
Terminal = Sprite('terminal', 'terminal', '터미널', TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE)
Terminal.map_to(True, Experimentation.MAP_ID)
Terminal.teleport(4 * CONFIG['TILE_SIZE'], 19 * CONFIG['TILE_SIZE'])

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Experimentation.MAP_ID)
Charger.teleport(5.25 * CONFIG['TILE_SIZE'], 19 * CONFIG['TILE_SIZE'])

# 배달
Delivery = Sprite('delivery', 'delivery', '배달', DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE)
Delivery.map_to(True, Experimentation.MAP_ID)
Delivery.teleport(17 * CONFIG['TILE_SIZE'], -10 * CONFIG['TILE_SIZE'])

# 정문
Enter1 = Sprite('enter', 'enter', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Enter1.map_to(True, Experimentation.MAP_ID)
Enter1.teleport(39 * CONFIG['TILE_SIZE'], 20 * CONFIG['TILE_SIZE'])

Enter2 = Sprite('enter', 'enter', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Enter2.map_to(True, Experimentation.MAP_ID)
Enter2.teleport(39 * CONFIG['TILE_SIZE'], 21 * CONFIG['TILE_SIZE'])

# 열리는 문
Open1 = Sprite('open', 'open_up', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open1.map_to(True, Experimentation.MAP_ID)
Open1.teleport(12 * CONFIG['TILE_SIZE'], 21 * CONFIG['TILE_SIZE'])

Open2 = Sprite('open', 'open_down', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open2.map_to(True, Experimentation.MAP_ID)
Open2.teleport(12 * CONFIG['TILE_SIZE'], 21 * CONFIG['TILE_SIZE'])

# 공장 맵
OUTPUT = generate_map('images/map/factory.png')
FactoryArray = OUTPUT[0].copy()
Factory = Map('factory', 'factory', FactoryArray)

# 문 생성
for Y, ROW in enumerate(Factory.MAP_ARRAY):
    for X, TILE in enumerate(ROW):
        if TILE == 0: Factory.MAP_ARRAY[Y][X] = random.choice([0 for _ in range(0, 20)] + [FACTORY_WEB1, FACTORY_WEB2])

        if TILE == FACTORY_DOOR:
            Factory.MAP_ARRAY[Y][X] = 0

            # 문
            if Factory.MAP_ARRAY[Y][X - 1] == FACTORY_WALL and Factory.MAP_ARRAY[Y][X + 1] == FACTORY_WALL: IMAGE = DOOR_IMAGE
            else: IMAGE = DOOR_2_IMAGE
            
            Door = Sprite('door', 'door', '문', IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE)
            Door.map_to(True, Factory.MAP_ID)
            Door.teleport(X * CONFIG['TILE_SIZE'], Y * CONFIG['TILE_SIZE'])
            Door.LOCKED = True if random.randrange(0, 40) == 0 else False

# 나가는 문
Exit = Sprite('exit', 'exit', '문', DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE, DOOR_2_IMAGE)
Exit.map_to(True, Factory.MAP_ID)
Exit.teleport(0, 3 * CONFIG['TILE_SIZE'])

# 회사 맵
_ = generate_map('images/map/company.png')
CompanyArray = _[0]
Company = Map('company', 'company', CompanyArray)

# 터미널
Terminal = Sprite('terminal', 'terminal', '터미널', TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE, TERMINAL_IMAGE)
Terminal.map_to(True, Company.MAP_ID)
Terminal.teleport(27 * CONFIG['TILE_SIZE'], 54 * CONFIG['TILE_SIZE'])

# 충전기
Charger = Sprite('charger', 'charger', '충전기', CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE, CHARGER_IMAGE)
Charger.map_to(True, Company.MAP_ID)
Charger.teleport(28.25 * CONFIG['TILE_SIZE'], 54 * CONFIG['TILE_SIZE'])

# 배달
Delivery2 = Sprite('delivery', 'delivery', '배달', DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE, DELIVERY_FIRE_IMAGE)
Delivery2.map_to(True, Company.MAP_ID)
Delivery2.teleport(40 * CONFIG['TILE_SIZE'], -10 * CONFIG['TILE_SIZE'])

# 열리는 문
Open3 = Sprite('open', 'open_up', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open3.map_to(True, Company.MAP_ID)
Open3.teleport(35 * CONFIG['TILE_SIZE'], 55 * CONFIG['TILE_SIZE'])

Open4 = Sprite('open', 'open_down', '문', WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE, WALL_IMAGE)
Open4.map_to(True, Company.MAP_ID)
Open4.teleport(35 * CONFIG['TILE_SIZE'], 57 * CONFIG['TILE_SIZE'])

SaleManager = Sprite('salemanager', 'salemanager', '판매소', COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE, COMPANY_TILE_1_IMAGE)
SaleManager.map_to(True, Company.MAP_ID)
SaleManager.teleport(49 * CONFIG['TILE_SIZE'], 51 * CONFIG['TILE_SIZE'])

SaleManager = Sprite('salemanager', 'salemanager', '판매소', COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE, COMPANY_TILE_2_IMAGE)
SaleManager.map_to(True, Company.MAP_ID)
SaleManager.teleport(49 * CONFIG['TILE_SIZE'], 52 * CONFIG['TILE_SIZE'])

CompanyMonster = Sprite('monster', 'monster', '회사 괴물', TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE, TERROR_IMAGE)
CompanyMonster.map_to(True, Company.MAP_ID)
CompanyMonster.teleport(49 * CONFIG['TILE_SIZE'], 51.50 * CONFIG['TILE_SIZE'])
CompanyMonster.DAMAGE = 100

# 플레이어
Player = Sprite('player', 'player', '플레이어', PLAYER_FRONT_IMAGE, PLAYER_BACK_IMAGE, PLAYER_LEFT_IMAGE, PLAYER_RIGHT_IMAGE, PLAYER_FRONT_WALK_IMAGE, PLAYER_BACK_WALK_IMAGE, PLAYER_LEFT_WALK_IMAGE, PLAYER_RIGHT_WALK_IMAGE)
Player.map_to(True, Ship.MAP_ID)
Player.teleport(3 * CONFIG['TILE_SIZE'], 3 * CONFIG['TILE_SIZE'])
Player.DISTANCE = (CONFIG['SCREEN_WIDTH'] / 2) + 3 * CONFIG['TILE_SIZE']
Player.ATTACK_DISTANCE = 1.5 * CONFIG['TILE_SIZE']
if CONFIG['DEBUG']: Player.INVINCIBILITY = True

# 저장된 아이템 불러오기
NEW_SAVES = []
for ITEM in INGAME['SAVES']:
    OBJECT_1 = [OBJECT for OBJECT in ITEM_ARRAY if OBJECT['ID'] == ITEM['ID']]
    OBJECT_2 = [OBJECT for OBJECT in ITEM_ARRAY_2 if OBJECT['ID'] == ITEM['ID']]
    if OBJECT_1: OBJECT = OBJECT_1[0]
    else: OBJECT = OBJECT_2[0]
    IMAGE = gif_pygame.load(OBJECT['PATH'])
    gif_pygame.transform.scale(IMAGE, (1 * CONFIG['TILE_SIZE'], 1 * CONFIG['TILE_SIZE']))
    
    Item = Sprite(OBJECT['ID'], 'item', OBJECT['DISPLAY_NAME'], IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE, IMAGE)
    Item.map_to(True, Ship.MAP_ID)
    Item.teleport(ITEM['RECT'][0], ITEM['RECT'][1])
    Item.PRICE = ITEM['PRICE']

    NEW_SAVES.append(Item)
INGAME['SAVES'] = NEW_SAVES

# 플레이어 걷는 소리 재생
def player_walk_sound():
    if Player.WALKING:
        # 현재 맵
        MAP_REDUCED = Map.reduced('ID')
        CUR_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
        CUR_MAP = INGAME['MAPS'][CUR_MAP_IDX]
        
        TILE_NUM = CUR_MAP['ARRAY'][int((Player.RECT.y + (CONFIG['TILE_SIZE'] / 2)) / CONFIG['TILE_SIZE'])][int((Player.RECT.x + (CONFIG['TILE_SIZE'] / 2)) / CONFIG['TILE_SIZE'])]

        if INGAME['CUR_MAP'] == 'ship':
            if TILE_NUM == 0: random.choice([METAL_WALK_1, METAL_WALK_2, METAL_WALK_3, METAL_WALK_4]).play()

        if INGAME['CUR_MAP'] == 'experimentation':
            if TILE_NUM == 0: random.choice([SNOW_WALK_1, SNOW_WALK_2, SNOW_WALK_3, SNOW_WALK_4]).play()
            elif TILE_NUM == 2: random.choice([METAL_WALK_1, METAL_WALK_2, METAL_WALK_3, METAL_WALK_4]).play()

        if INGAME['CUR_MAP'] == 'factory':
            if TILE_NUM == 0: random.choice([CONCRETE_WALK_1, CONCRETE_WALK_2, CONCRETE_WALK_3, CONCRETE_WALK_4]).play()

        if INGAME['CUR_MAP'] == 'company':
            if TILE_NUM == 0: random.choice([CONCRETE_WALK_1, CONCRETE_WALK_2, CONCRETE_WALK_3, CONCRETE_WALK_4]).play()
            elif TILE_NUM == 2: random.choice([METAL_WALK_1, METAL_WALK_2, METAL_WALK_3, METAL_WALK_4]).play()

# 체력 소모
def decrease_player_hp():
    if Player.DECREASING and not Player.INVINCIBILITY:
        Player.HP -= Player.DECREASING_SIZE

# 게이지
def gauge():
    INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])

    if Player.FLASHLIGHT and 'flashlight' in INVENTORY:
        if not Player.DIED and not CONFIG['DEBUG']:
            if not Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE == 0:
                Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE -= 2
    else: Player.FLASHLIGHT = False

# 해고 메시지
def write_fire_message():
    if INGAME['FIRE_MESSAGE']: INGAME['FIRE_MESSAGE_IDX'] += 1

# 해고중 플레이어 시선
def rotate_player():
    if INGAME['FIRE']:
        if Player.LAST_ROTATE == 'right':
            Player.LAST_ROTATE = 'front'
            Player.CUR_IMAGE = Player.FRONT_IMAGE

        elif Player.LAST_ROTATE == 'front':
            Player.LAST_ROTATE = 'left'
            Player.CUR_IMAGE = Player.LEFT_IMAGE

        elif Player.LAST_ROTATE == 'left':
            Player.LAST_ROTATE = 'back'
            Player.CUR_IMAGE = Player.BACK_IMAGE

        elif Player.LAST_ROTATE == 'back':
            Player.LAST_ROTATE = 'right'
            Player.CUR_IMAGE = Player.RIGHT_IMAGE

# 해고
def run_fire():
    WARNING.play()
    FIRED_VOICE.play()
    INGAME['WARNING'] = True

    def fire_true():
        SUCKED_INTO_SPACE.play()
        
        INGAME['FIRE'] = True
        INGAME['WARNING'] = False

        def fire_message_true():
            INGAME['FIRE_MESSAGE'] = True

            def fire_button_true():
                INGAME['FIRE_BUTTON'] = True
                pygame.mouse.set_visible(True)
            Timer(4, fire_button_true).start()
        Timer(2, fire_message_true).start()
    Timer(9, fire_true).start()

# 시간
def increase_time():
    if not INGAME['CUR_MOD'] == 'READY' and not INGAME['CUR_MAP'] == 'company':
        INGAME['TIME'] += 4

        if int((INGAME['TIME'] - (60 * 8)) % 60) == 28 and len(INGAME['STORE']) > 0:
            for ITEM in INGAME['STORE']:
                Item = Sprite(ITEM['ID'], 'item', ITEM['DISPLAY_NAME'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'])
                if INGAME['CUR_MAP'] == 'experimentation': Delivery.INVENTORY.append(Item)
                elif INGAME['CUR_MAP'] == 'company': Delivery2.INVENTORY.append(Item)
            INGAME['STORE'] = []

            INGAME['DELIVERY'] = True
            INGAME['DELIVERY_LANDING'] = True
            DELIVERY_COME.play(-1)
        
        if INGAME['TIME'] == (60 * 23):
            INGAME['MIDNIGHT_MESSAGE'] = True
            def midnight_message_false():
                INGAME['MIDNIGHT_MESSAGE'] = False
            Timer(4, midnight_message_false).start()
        
        if INGAME['TIME'] == (60 * 24):
            INGAME['MIDNIGHT_RUN_MESSAGE'] = True
            def midnight_run_message_false():
                INGAME['MIDNIGHT_RUN_MESSAGE'] = False

                take_off()
                
                if not is_ship():
                    Player.DIED = True
                    
                    WILL_DROP = []
                    for CUR_ITEM in Player.INVENTORY:
                        WILL_DROP.append(CUR_ITEM)
                    
                    for ITEM in WILL_DROP:
                        Player.drop_item(ITEM)
                    
                    Timer(2, resurrection).start()
            Timer(4, midnight_run_message_false).start()

# 이벤트들
def main_event():
    for event in pygame.event.get(): 
        # 종료
        if event.type == pygame.QUIT: INGAME['RUNNING'] = False
        
        if event.type == pygame.MOUSEMOTION:
            for INTERFACE in CUR_SCENE['INTERFACES']:
                if INTERFACE.INTERFACE_ID == 'menu':
                    RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                    INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                    INTERFACE.INTERFACE_HOVER = False
                    if INTERFACE_RECT.collidepoint(event.pos):
                        if not INGAME['PREV_HOVER'] == INTERFACE: HOVER_BUTTON.play()

                        INTERFACE.INTERFACE_HOVER = True
                        INGAME['PREV_HOVER'] = INTERFACE
        
        if event.type == pygame.MOUSEBUTTONUP:
            for INTERFACE in CUR_SCENE['INTERFACES']:
                if INTERFACE.INTERFACE_ID == 'menu':
                    RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                    INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                    if INTERFACE_RECT.collidepoint(event.pos):
                        CLICK_BUTTON.play()

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

def setting_event():
    global INTERFACE

    for event in pygame.event.get(): 
        # 종료
        if event.type == pygame.QUIT: INGAME['RUNNING'] = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            RECT = pygame.Rect(200, 465, 200, 30)

            INTERFACE.INTERFACE_HOVER = False
            if RECT.collidepoint(event.pos):
                CONFIG['MIXING'] = True
                CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * .01
                mixing()
            
            RECT = pygame.Rect(200, 300, 250, 80)

            if RECT.collidepoint(event.pos):
                CONFIG['DEBUG'] = not CONFIG['DEBUG']
                Player.INVINCIBILITY = not Player.INVINCIBILITY
                save_config()
            
            RECT = pygame.Rect(290, 590, 120, 60)

            if RECT.collidepoint(event.pos):
                INGAME['DIFFICULTY'] = '일식' if INGAME['DIFFICULTY'] == '평화로움' else '평화로움'
        
        if event.type == pygame.MOUSEMOTION:
            RECT = pygame.Rect(200, 465, 200, 30)

            if CONFIG['MIXING']:
                if RECT.collidepoint(event.pos):
                    CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * .01
                    mixing()
            
            else:
                for INTERFACE in CUR_SCENE['INTERFACES']:
                    if INTERFACE.INTERFACE_ID == 'menu':
                        RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                        INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                        INTERFACE.INTERFACE_HOVER = False
                        if INTERFACE_RECT.collidepoint(event.pos):
                            if not INGAME['PREV_HOVER'] == INTERFACE: HOVER_BUTTON.play()
                            INTERFACE.INTERFACE_HOVER = True
                            INGAME['PREV_HOVER'] = INTERFACE
        
        if event.type == pygame.MOUSEBUTTONUP:
            RECT = pygame.Rect(200, 465, 200, 30)

            if CONFIG['MIXING']:
                if RECT.collidepoint(event.pos):
                    CONFIG['MIXING'] = False
                    CONFIG['MASTER_SOUND'] = (event.pos[0] - 200) * .01

                    save_config()
                    mixing()
            
            else:
                for INTERFACE in CUR_SCENE['INTERFACES']:
                    if INTERFACE.INTERFACE_ID == 'menu':
                        RECT_X, RECT_Y = INTERFACE.INTERFACE_RECT
                        INTERFACE_RECT = pygame.Rect(RECT_X, RECT_Y, CONFIG['SCREEN_WIDTH'] - RECT_X, 50)

                        if INTERFACE_RECT.collidepoint(event.pos):
                            if INTERFACE.INTERFACE_DISPLAY_NAME == '메뉴1':
                                INGAME['CUR_SCENE'] = Ingame.SCENE_ID if INGAME['PREV_SCENE'] == Ingame.SCENE_ID else Main.SCENE_ID
                                if INGAME['PREV_SCENE'] == Ingame.SCENE_ID: pygame.mouse.set_visible(False)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and INGAME['PREV_SCENE'] == Ingame.SCENE_ID:
            INGAME['CUR_SCENE'] = Ingame.SCENE_ID
            pygame.mouse.set_visible(False)

def use_interval():
    set_interval(player_walk_sound, .4)
    set_interval(decrease_player_hp, .5)
    set_interval(gauge, 20)
    set_interval(write_fire_message, .05)
    set_interval(rotate_player, .5)
    set_interval(increase_time, 3)

def take_off():
    for ITEM in INGAME['SAVES']:
        RECT_X = ITEM.RECT.x - get_ship_rect().x
        RECT_Y = ITEM.RECT.y - get_ship_rect().y
        ITEM.map_to(False, Ship.MAP_ID)
        ITEM.teleport(RECT_X, RECT_Y)
    
    if INGAME['CUR_MAP'] == 'experimentation':
        NOISE_2.stop()
        INGAME['SURVIVAL_RESULT'] = True
        def survival_result_false():
            INGAME['SURVIVAL_RESULT'] = False

            if INGAME['DAY'] - 1 < 0:
                run_fire()
            
            else:
                DECREASE_DAY.play()
                INGAME['DAY'] -= 1
                INGAME['DAY_RESULT'] = True
                def day_result_false():
                    INGAME['DAY_RESULT'] = False
                Timer(4, day_result_false).start()
        Timer(5, survival_result_false).start()
    
    elif INGAME['CUR_MAP'] == 'company':
        NOISE_2.stop()
        INGAME['SURVIVAL_RESULT'] = True
        def survival_result_false():
            INGAME['SURVIVAL_RESULT'] = False
            
            if INGAME['QUOTA'] < INGAME['TARGET_QUOTA']:
                run_fire()

            else:
                INCREASE_QUOTA.play()
                def increase_quota_stop():
                    INCREASE_QUOTA.stop()
                Timer(3, increase_quota_stop).start()

                INGAME['DAY'] = 3
                INGAME['MONEY'] += INGAME['QUOTA']
                INGAME['QUOTA'] = 0
                INGAME['TARGET_QUOTA'] *= 2.25
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
    Player.teleport(Player.RECT.x - get_ship_rect().x, Player.RECT.y - get_ship_rect().y)
    
    INGAME['CUR_MAP'] = Ship.MAP_ID
    INGAME['CUR_MOD'] = 'READY'

    INGAME['TIME'] = 60 * 8

def enter_terminal(event):
    # 키를 눌렀을 떄
    if event.type == pygame.KEYDOWN:
        random.choice([KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8]).play()

        # 나가기
        if event.key == pygame.K_ESCAPE:
            EXIT_TERMINAL.play()
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

                    TERMINAL_ERROR.play()

                else:
                    DISPLAY_NAME = '철제 삽' if INGAME['COMMAND'] == 'shovel' else '손전등'
                    INGAME['MONEY'] -= 25 if INGAME['COMMAND'] == 'flashlight' else 30
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}

                    {DISPLAY_NAME} 1개를 주문했습니다.'''
                    INGAME['STORE'].append({ 'ID': INGAME['COMMAND'], 'DISPLAY_NAME': DISPLAY_NAME, 'IMAGE': SHOVEL_IMAGE if INGAME['COMMAND'] == 'shovel' else FLASHLIGHT_IMAGE })

                    PURCHASE_ITEM.play()

            elif INGAME['COMMAND'] in ['experimentation', 'company']:
                if INGAME['CUR_MOD'] == 'READY':
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                    
                    {INGAME['COMMAND']} 으로 함선이 이동했습니다.
                    이동 비용은 $0원 입니다.'''
                    INGAME['NEXT_MAP'] = INGAME['COMMAND']

                    INTRO_MUSIC.stop()
                    SHIP_FLY_TO_PLANET.play()

                    def arrive_play():
                        SHIP_ARRIVE_AT_PLANET.play()
                    Timer(4, arrive_play).start()
                
                else:
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                    
                    이륙한 다음에만 이동할 수 있습니다.'''

                    TERMINAL_ERROR.play()
            
            elif INGAME['COMMAND'] == 'land':
                if INGAME['CUR_MOD'] == 'READY':
                    for ITEM in INGAME['SAVES']:
                        RECT_X = ITEM.RECT.x + get_ship_rect(INGAME['NEXT_MAP']).x
                        RECT_Y = ITEM.RECT.y + get_ship_rect(INGAME['NEXT_MAP']).y
                        ITEM.map_to(False, INGAME['NEXT_MAP'])
                        ITEM.teleport(RECT_X, RECT_Y)
                    
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                    
                    {INGAME['NEXT_MAP']}으로 함선이 착륙합니다.'''

                    NEXT_MAP = None
                    if INGAME['NEXT_MAP'] == 'experimentation': NEXT_MAP = Experimentation
                    if INGAME['NEXT_MAP'] == 'company': NEXT_MAP = Company

                    INGAME['LOADING'] = True
                    INGAME['TERMINAL'] = False
                    
                    def run():
                        async def setting():
                            if not INGAME['NEXT_MAP'] == 'company':
                                FACTORY = INGAME['MAPS'][Map.reduced('ID').index('factory')]
                                WILL_REMOVES = []
                                for OBJECT in FACTORY['OBJECTS']:
                                    if OBJECT.TYPE in ['item', 'monster', 'door']: WILL_REMOVES.append(OBJECT)
                                
                                for OBJECT in WILL_REMOVES:
                                    if OBJECT.TYPE == 'door':
                                        Door = Sprite('door', 'door', '문', OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE, OBJECT.FRONT_IMAGE)
                                        Door.map_to(True, Factory.MAP_ID)
                                        Door.teleport(OBJECT.RECT.x, OBJECT.RECT.y)
                                        Door.LOCKED = True if random.randrange(0, 40) == 0 else False

                                    FACTORY['OBJECTS'].remove(OBJECT)
                            
                                # 아이템 생성
                                for _ in range(0, 15) if INGAME['DIFFICULTY'] == '평화로움' else range(0, 40):
                                    RECT_X = random.randrange(1, OUTPUT[1])
                                    RECT_Y = random.randrange(1, OUTPUT[2])

                                    if not Factory.MAP_ARRAY[RECT_Y][RECT_X] == FACTORY_WALL and not OUTPUT[0][RECT_Y][RECT_X] == 2:
                                        ITEM = ITEM_ARRAY[random.randrange(len(ITEM_ARRAY))]

                                        Item = Sprite(ITEM['ID'], 'item', ITEM['DISPLAY_NAME'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'], ITEM['IMAGE'])
                                        Item.map_to(True, Factory.MAP_ID)
                                        Item.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                        Item.PRICE = random.randrange(3, 70)

                                # 생명체 생성
                                HOARDING_BUG_COUNT = 2
                                COILHEAD_COUNT = 1
                                BRACKEN_COUNT = 0
                                JESTER_COUNT = 0
                                GIRL_COUNT = 0
                                MASK_COUNT = 1
                                MINE_COUNT = 4

                                if INGAME['DIFFICULTY'] == '일식':
                                    HOARDING_BUG_COUNT = 3
                                    COILHEAD_COUNT = 2
                                    BRACKEN_COUNT = 1
                                    JESTER_COUNT = 1
                                    GIRL_COUNT = 1
                                    MASK_COUNT = 2
                                    MINE_COUNT = 12

                                for _ in range(0, HOARDING_BUG_COUNT + COILHEAD_COUNT + BRACKEN_COUNT + JESTER_COUNT + GIRL_COUNT + MASK_COUNT + MINE_COUNT + 1):
                                    RECT_X = random.randrange(7, OUTPUT[1])
                                    RECT_Y = random.randrange(7, OUTPUT[2])

                                    if not Factory.MAP_ARRAY[RECT_Y][RECT_X] == FACTORY_WALL and not OUTPUT[0][RECT_Y][RECT_X] == 2:
                                        if HOARDING_BUG_COUNT > 0:
                                            HoardingBug = Sprite('hoarding bug', 'monster', '비축벌레', HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE, HOARDING_BUG_WALK_IMAGE)
                                            HoardingBug.map_to(True, Factory.MAP_ID)
                                            HoardingBug.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])

                                            NAVIGATE_ITEM = None
                                            MIN_DISTANCE = float('inf')

                                            for ITEM in FACTORY['OBJECTS']:
                                                if ITEM.TYPE == 'item':
                                                    dist = distance(OBJECT.RECT, ITEM.RECT)

                                                    if dist < MIN_DISTANCE:
                                                        MIN_DISTANCE = dist
                                                        NAVIGATE_ITEM = ITEM
                                            
                                            HoardingBug.SPAWN_POINT = (RECT_Y, RECT_X)
                                            HoardingBug.NAVIGATE = astar(Factory.MAP_ARRAY, (RECT_Y, RECT_X), (int(NAVIGATE_ITEM.RECT.y / CONFIG['TILE_SIZE']), int(NAVIGATE_ITEM.RECT.x / CONFIG['TILE_SIZE'])))

                                            HoardingBug.SPEED = 1
                                            HoardingBug.HP = 5

                                            HOARDING_BUG_COUNT -= 1

                                        elif COILHEAD_COUNT > 0:
                                            CoilHead = Sprite('coil head', 'monster', '코일헤드', COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE, COIL_HEAD_IMAGE)
                                            CoilHead.map_to(True, Factory.MAP_ID)
                                            CoilHead.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            CoilHead.INVINCIBILITY = True
                                            CoilHead.DAMAGE = 100
                                            CoilHead.SPEED = 2

                                            COILHEAD_COUNT -= 1

                                        elif BRACKEN_COUNT > 0:
                                            Bracken = Sprite('bracken', 'monster', '브레켄', BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE, BRACKEN_WALK_IMAGE)
                                            Bracken.map_to(True, Factory.MAP_ID)
                                            Bracken.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            Bracken.DAMAGE = 100
                                            Bracken.SPEED = 1
                                            Bracken.HP = 7
                                            Bracken.TIMEOUT = 4

                                            BRACKEN_COUNT -= 1
                                        
                                        elif JESTER_COUNT > 0:
                                            Jester = Sprite('jester', 'monster', '제스터', JESTER_IMAGE, JESTER_IMAGE, JESTER_IMAGE, JESTER_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE, JESTER_WALK_IMAGE)
                                            Jester.map_to(True, Factory.MAP_ID)
                                            Jester.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            Jester.INVINCIBILITY = True
                                            Jester.DAMAGE = 0
                                            Jester.SPEED = 1

                                            JESTER_COUNT -= 1
                                        
                                        elif GIRL_COUNT > 0:
                                            Girl = Sprite('girl', 'monster', '유령소녀', GIRL_IMAGE, GIRL_IMAGE, GIRL_IMAGE, GIRL_IMAGE, GIRL_WALK_IMAGE, GIRL_WALK_IMAGE, GIRL_WALK_IMAGE, GIRL_WALK_IMAGE)
                                            Girl.map_to(True, Factory.MAP_ID)
                                            Girl.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            Girl.TRANSPARENT = True
                                            Girl.DISTANCE = 3 * CONFIG['TILE_SIZE']
                                            Girl.INVINCIBILITY = True
                                            Girl.DAMAGE = 100
                                            Girl.SPEED = 1

                                            GIRL_COUNT -= 1
                                        
                                        elif MASK_COUNT > 0:
                                            Mask = Sprite('mask', 'monster', '가면 쓴 사람', MASK_FRONT_IMAGE, MASK_BACK_IMAGE, MASK_LEFT_IMAGE, MASK_RIGHT_IMAGE, MASK_FRONT_WALK_IMAGE, MASK_BACK_WALK_IMAGE, MASK_LEFT_WALK_IMAGE, MASK_RIGHT_WALK_IMAGE)
                                            Mask.map_to(True, Factory.MAP_ID)
                                            Mask.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            Mask.TIMEOUT = 6
                                            Mask.DAMAGE = 100
                                            Mask.HP = 10
                                            Mask.SPEED = 1

                                            MASK_COUNT -= 1
                                        
                                        elif MINE_COUNT > 0:
                                            Mine = Sprite('mine', 'monster', '지뢰', MINE_IMAGE, MINE_IMAGE, MINE_IMAGE, MINE_IMAGE, MINE_FIRE_IMAGE, MINE_FIRE_IMAGE, MINE_FIRE_IMAGE, MINE_FIRE_IMAGE)
                                            Mine.map_to(True, Factory.MAP_ID)
                                            Mine.teleport(RECT_X * CONFIG['TILE_SIZE'], RECT_Y * CONFIG['TILE_SIZE'])
                                            Mine.INVINCIBILITY = True
                                            Mine.TIMEOUT = 5
                                            Mine.DAMAGE = 100
                                            Mine.ATTACK_DISTANCE = 150
                                            Mine.INTERACTION_DISTANCE = 50

                                            MINE_COUNT -= 1
                        
                            INGAME['LOADING'] = False
                        
                        asyncio.run(setting())

                        INTRO_MUSIC.stop()

                        Player.map_to(False, NEXT_MAP.MAP_ID)
                        Player.teleport(get_ship_rect(NEXT_MAP.MAP_ID).x + Player.RECT.x, get_ship_rect(NEXT_MAP.MAP_ID).y + Player.RECT.y)
                        
                        INGAME['CUR_MAP'] = NEXT_MAP.MAP_ID
                        INGAME['CUR_MOD'] = 'OK'

                        INGAME['CAMERA_MOVE'] = True

                        # 착륙 사운드 재생
                        DOOR_OPENING.play()
                        NOISE.play()

                        if INGAME['NEXT_MAP'] == 'experimentation':
                            # 메인 음악 재생
                            def main_music():
                                if random.randrange(1, 3) == 1: MAIN_MUSIC_1.play()
                                else: MAIN_MUSIC_2.play()

                            Timer(10, main_music).start()
                    
                    Timer(.5, run).start()
                
                else:
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                    
                    함선이 이동한 다음에만 착륙할 수 있습니다.'''

                    TERMINAL_ERROR.play()
            
            elif INGAME['COMMAND'] == 'take-off':
                if INGAME['CUR_MOD'] == 'OK':
                    take_off()
                
                else:
                    INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                    
                    착륙한 후에만 이륙할 수 있습니다.'''

                    TERMINAL_ERROR.play()

            else:
                INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                
                알 수 없는 명령어 \'{INGAME['COMMAND']}\'.'''

                TERMINAL_ERROR.play()

            INGAME['COMMAND'] = ''
        
        # 입력 제한
        elif len(INGAME['COMMAND']) <= 30 and len(pygame.key.name(event.key)) == 1:
            INGAME['COMMAND'] += str(pygame.key.name(event.key))

def enter_ingame(event):
    global CUR_ITEM_EXISTS

    # 설정
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        pygame.mouse.set_visible(True)
        INGAME['PREV_SCENE'] = Ingame.SCENE_ID
        INGAME['CUR_SCENE'] = Setting.SCENE_ID
    
    # 공격 준비
    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        if CUR_ITEM_EXISTS:
            CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

            if CUR_ITEM.ID in ['shovel', 'stop']: HIT_READY.play()
    
    # 공격
    if event.type == pygame.KEYUP and event.key == pygame.K_r:
        if CUR_ITEM_EXISTS:
            CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

            if CUR_ITEM.ID in ['shovel', 'stop']:
                random.choice([HIT_DEFAULT_1, HIT_DEFAULT_2]).play()

                for MONSTER in CUR_MAP['OBJECTS']:
                    dist = distance(Player.RECT, MONSTER.RECT)

                    if dist < Player.ATTACK_DISTANCE:
                        if MONSTER.TYPE == 'monster':
                            if not MONSTER.INVINCIBILITY:
                                MONSTER.HP -= Player.DAMAGE

                                if MONSTER.HP < 0:
                                    if len(MONSTER.INVENTORY) > 0: MONSTER.drop_item(MONSTER.INVENTORY[0])
                                    CUR_MAP['OBJECTS'].remove(MONSTER)

                                    if MONSTER.ID == 'bracken': BRACKEN_ANGRY.stop()
    
    # e키 상호작용
    if event.type == pygame.KEYDOWN and event.key == pygame.K_e and Player.CONTAIN:
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

            ENTER_TERMINAL.play()
            Player.WALKING = False
            INGAME['TERMINAL'] = True

        # 문
        elif Player.CONTAIN.TYPE == 'door':
            DOOR_IDX = CUR_MAP['OBJECTS'].index(Player.CONTAIN)
            DOOR = CUR_MAP['OBJECTS'][DOOR_IDX]

            # 열려있다면
            if DOOR.OPENED:
                random.choice([DOOR_CLOSE_1, DOOR_CLOSE_2]).play()

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
                    random.choice([DOOR_OPEN_1, DOOR_OPEN_2]).play()
                    
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
            LOBBY_MUSIC_3.play(-1)
            METAL_DOOR_SHUT.play()

            Player.map_to(False, Factory.MAP_ID)
            Player.teleport(1 * CONFIG['TILE_SIZE'], 3 * CONFIG['TILE_SIZE'])
            Player.SPEED = 2
            
            INGAME['CUR_MAP'] = Factory.MAP_ID
            INGAME['CUR_MOD'] = 'FARMING'
        
        # 나가기
        elif Player.CONTAIN.TYPE == 'exit':
            LOBBY_MUSIC_3.stop()
            METAL_DOOR_CLOSE.play()

            Player.map_to(False, INGAME['NEXT_MAP'])
            Player.teleport(38 * CONFIG['TILE_SIZE'], 21 * CONFIG['TILE_SIZE'])
            Player.SPEED = 1
            
            INGAME['CUR_MAP'] = INGAME['NEXT_MAP']
            INGAME['CUR_MOD'] = 'OK'
        
        # 배달
        elif Player.CONTAIN.TYPE == 'delivery':
            def delivery_landing_false():
                INGAME['DELIVERY_LANDING'] = False
                DELIVERY_COME.play(-1)

                def delivery_come_stop():
                    DELIVERY_COME.stop()
                Timer(4, delivery_come_stop).start()
            Timer(5, delivery_landing_false).start()
            
            DELIVERY = Delivery2
            if INGAME['CUR_MAP'] == 'experimentation': DELIVERY = Delivery

            for ITEM in DELIVERY.INVENTORY:
                if ITEM.ID in ['stop', 'shovel']: DROP_SHOVEL.play()
                if ITEM.ID == 'key': DROP_KEY.play()
                if ITEM.ID == 'bottle': DROP_BOTTLE.play()
                if ITEM.ID == 'flashlight': DROP_FLASHLIGHT.play()

                ITEM.RECT.x = DELIVERY.RECT.x
                ITEM.RECT.y = DELIVERY.RECT.y
                CUR_MAP['OBJECTS'].append(ITEM)
            DELIVERY.INVENTORY = []
        
        # 충전
        elif Player.CONTAIN.TYPE == 'charger':
            if CUR_ITEM_EXISTS:
                CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                if CUR_ITEM.ID == 'flashlight':
                    INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])

                    INGAME['CHARGING'] = True

                    CHARGE_ITEM.play()

                    def charging_false():
                        INGAME['CHARGING'] = False

                    def charge_item():
                        Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE = 100
                    
                    Player.CUR_IMAGE = Player.BACK_WALK_IMAGE
                    Player.LAST_ROTATE = 'back'
                    
                    Timer(.8, charge_item).start()
                    Timer(.8, charging_false).start()
        
        # 올려두기
        elif Player.CONTAIN.TYPE == 'salemanager':
            if CUR_ITEM_EXISTS:
                CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]
                Player.drop_item(CUR_ITEM)
                CUR_ITEM_EXISTS = False
                CUR_ITEM.RECT.x = 49 * CONFIG['TILE_SIZE'] + random.randrange(0, 1 * CONFIG['TILE_SIZE'])
                CUR_ITEM.RECT.y = 51 * CONFIG['TILE_SIZE'] + random.randrange(0, 1 * CONFIG['TILE_SIZE'])
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
            if is_ship() and get_ship_rect().collidepoint(Player.CONTAIN.RECT.x, Player.CONTAIN.RECT.y):
                INGAME['SAVES'].remove(Player.CONTAIN)

            Player.grab_item()

    # g키 버리기
    if event.type == pygame.KEYDOWN and event.key == pygame.K_g and len(Player.INVENTORY) > 0:
        if CUR_ITEM_EXISTS:
            CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

            if CUR_ITEM:
                Player.drop_item(CUR_ITEM)

                if len(Player.INVENTORY) < Player.CUR_ITEM_IDX + 1:
                    CUR_ITEM_EXISTS = False
                
                # 플레이어가 함선 안에 있는지
                if is_ship() and get_ship_rect().collidepoint(CUR_ITEM.RECT.x, CUR_ITEM.RECT.y):
                    INGAME['SAVES'].append(CUR_ITEM)

                    INGAME['SAVE_ANIMATION'] = True
                    INGAME['SAVE_ANIMATION_Y'] = 0
                    INGAME['SAVE_ITEM'] = { 'UUID': CUR_ITEM.UUID, 'DISPLAY_NAME': CUR_ITEM.DISPLAY_NAME, 'IMAGE': CUR_ITEM.CUR_IMAGE }

                    SAVE_ITEM_SFX.play()

                    def animation_false(SAVE_ITEM):
                        if INGAME['SAVE_ITEM'] == SAVE_ITEM: INGAME['SAVE_ANIMATION'] = False
                    Timer(2, animation_false, (INGAME['SAVE_ITEM'],)).start()
    
    # f키 손전등
    if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        if CUR_ITEM_EXISTS:
            CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

            if CUR_ITEM:
                if CUR_ITEM.ID == 'flashlight':
                    Player.FLASHLIGHT = not Player.FLASHLIGHT

                    FLASHLIGHT_CLICK.play()
    
    # q키 스캔
    if event.type == pygame.KEYDOWN and event.key == pygame.K_q and not INGAME['SCAN']:
        SCAN.play()
        INGAME['SCAN'] = True
        def scan_false():
            INGAME['SCAN'] = False
        Timer(2, scan_false).start()

    # 아이템 선택
    if event.type == pygame.MOUSEWHEEL:
        if event.y == -1: Player.CUR_ITEM_IDX -= 1
        if event.y == 1: Player.CUR_ITEM_IDX += 1

        if Player.CUR_ITEM_IDX > 7: Player.CUR_ITEM_IDX = 0
        if Player.CUR_ITEM_IDX < 0: Player.CUR_ITEM_IDX = 7

        CUR_ITEM_EXISTS = len(Player.INVENTORY) > Player.CUR_ITEM_IDX

def ingame_event():
    global CUR_ITEM_EXISTS, INGAME

    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            INGAME['RUNNING'] = False

            if INGAME['CUR_MOD'] == 'READY' and not INGAME['SURVIVAL_RESULT'] and not INGAME['QUOTA_RESULT'] and not INGAME['DAY_RESULT']:
                CUR_ITEM_EXISTS = False
                WILL_DROP = []
                for CUR_ITEM in Player.INVENTORY:
                    WILL_DROP.append(CUR_ITEM)
                
                for ITEM in WILL_DROP:
                    INGAME['SAVES'].append(ITEM)
                    Player.drop_item(ITEM)
                
                save_ingame()
        
        # 다시하기 버튼 클릭
        if event.type == pygame.MOUSEBUTTONUP:
            if pygame.Rect(INGAME['FIRE_BUTTON_RECT'][0], INGAME['FIRE_BUTTON_RECT'][1], INGAME['FIRE_BUTTON_RECT'][2], INGAME['FIRE_BUTTON_RECT'][3]).collidepoint(pygame.mouse.get_pos()):
                with open('data/origin_ingame.json') as ingame:
                    INGAME = json.load(ingame)
                    save_ingame()
                    INGAME['RUNNING'] = False
                    ingame.close()

        # 플레이어가 살아있을 때
        if not Player.DIED:
            # 터미널에 입력
            if INGAME['TERMINAL']: enter_terminal(event)
                
            # 인게임에 입력
            elif not INGAME['WARNING'] and not INGAME['FIRE']: enter_ingame(event)

def draw_tile():
    for Y, ROW in enumerate(CUR_MAP['ARRAY']):
        for X, TILE in enumerate(ROW):
            RECT = (X * CONFIG['TILE_SIZE'] + OFFSET_X, Y * CONFIG['TILE_SIZE'] + OFFSET_Y)
            dist = distance(Player.RECT, pygame.Rect(X * CONFIG['TILE_SIZE'], Y * CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE']))

            if dist < Player.DISTANCE or not INGAME['CAMERA_X'] == 0:
                if not Player.NAVIGATE == (int(Player.RECT.x / CONFIG['TILE_SIZE']), int(Player.RECT.y / CONFIG['TILE_SIZE'])):
                    INGAME['VISIBLE_TILES'] = calculate_fov()
                    Player.NAVIGATE = (int(Player.RECT.x / CONFIG['TILE_SIZE']), int(Player.RECT.y / CONFIG['TILE_SIZE']))

                if Player.NAVIGATE == (X, Y) or (X, Y) in INGAME['VISIBLE_TILES'] or INGAME['FIRE'] or TILE in [SHIP_WALL, EXPERIMENTATION_WALL, FACTORY_WALL]:
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
                
                else: pygame.draw.rect(screen, (20, 20, 20), (RECT[0], RECT[1], CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE']))

def draw_object():
    if dist < Player.DISTANCE or not INGAME['CAMERA_X'] == 0:
        if OBJECT.TYPE == 'door' and OBJECT.OPENED:
            RECT_X = OBJECT_RECT.x + 50
            RECT_Y = OBJECT_RECT.y

            if OBJECT.CUR_IMAGE == OPENED_DOOR_2_IMAGE:
                RECT_X -= 50
                RECT_Y -= 50
                
            OBJECT.CUR_IMAGE.render(screen, (RECT_X, RECT_Y))
        elif OBJECT.TYPE == 'player' or not OBJECT.DIED:
            OBJECT.CUR_IMAGE.render(screen, OBJECT_RECT)

            # 몬스터가 들고 있는 아이템 표시
            if OBJECT.TYPE == 'monster' and len(OBJECT.INVENTORY) > 0: OBJECT.INVENTORY[0].CUR_IMAGE.render(screen, (OBJECT.RECT.x + OFFSET_X - 25, OBJECT.RECT.y + OFFSET_Y + 25))

    if CONFIG['DEBUG']: pygame.draw.rect(screen, (255, 255, 0), OBJECT_RECT, 1)

def draw_scan(dist):
    sum_text = None

    if INGAME['SCAN'] and dist < Player.DISTANCE and (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) in INGAME['VISIBLE_TILES']:
        if OBJECT.TYPE == 'item' and not OBJECT.ID in ['flashlight', 'shovel']:
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
        
        if OBJECT.TYPE == 'monster' and not OBJECT.ID == 'girl':
            pygame.draw.circle(screen, (150, 31, 27), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 75, 1)
            pygame.draw.circle(screen, (150, 31, 27), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 85, 1)
            pygame.draw.circle(screen, (150, 31, 27), (OBJECT_RECT.x + 50, OBJECT_RECT.y + 50), 130, 1)
            pygame.draw.rect(screen, (150, 31, 27), (OBJECT_RECT.x + 125, OBJECT_RECT.y - 50, 200, 100))

            # 정보
            text_ = font.render(OBJECT.DISPLAY_NAME, True, (0, 0, 0))
            screen.blit(text_, (OBJECT_RECT.x + 150, OBJECT_RECT.y - 25))
    
    return sum_text

def draw_letterbox():
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, (CONFIG['SCREEN_WIDTH'] / 2) - 450, CONFIG['SCREEN_HEIGHT']))
    pygame.draw.rect(screen, (0, 0, 0), (CONFIG['SCREEN_WIDTH'] - ((CONFIG['SCREEN_WIDTH'] / 2) - 450), 0, (CONFIG['SCREEN_WIDTH'] / 2) - 450, CONFIG['SCREEN_HEIGHT']))

def is_ship():
    RECT = get_ship_rect()
    IS_SHIP = RECT.collidepoint(Player.RECT.x, Player.RECT.y)
    return IS_SHIP

def get_ship_rect(MAP_ID=''):
    if len(MAP_ID) == 0: MAP_ID = INGAME['CUR_MAP']
    RECT = pygame.Rect(0, 0, 0, 0)
    if MAP_ID == Experimentation.MAP_ID: RECT = pygame.Rect(2 * CONFIG['TILE_SIZE'], 18 * CONFIG['TILE_SIZE'], 11 * CONFIG['TILE_SIZE'], 7 * CONFIG['TILE_SIZE'])
    elif MAP_ID == Company.MAP_ID: RECT = pygame.Rect(25 * CONFIG['TILE_SIZE'], 53 * CONFIG['TILE_SIZE'], 11 * CONFIG['TILE_SIZE'], 7 * CONFIG['TILE_SIZE'])
    elif MAP_ID == Ship.MAP_ID: RECT = pygame.Rect(0, 0, 11 * CONFIG['TILE_SIZE'], 7 * CONFIG['TILE_SIZE'])
    return RECT

def draw_situation():
    if IS_SHIP:
        # 마감일 표시
        pygame.draw.rect(screen, (255, 255, 255), (CONFIG['SCREEN_WIDTH'] - 400, 50, 100, 100), 1)
        text_ = font.render('마감일', True, (255, 255, 255))
        text2_ = font.render(f'{INGAME['DAY']}일', True, (255, 255, 255))
        screen.blit(text_, (CONFIG['SCREEN_WIDTH'] - 375, 70))
        screen.blit(text2_, (CONFIG['SCREEN_WIDTH'] - 375, 100))
    
        # 할당량 표시
        pygame.draw.rect(screen, (255, 255, 255), (CONFIG['SCREEN_WIDTH'] - 250, 50, 200, 100), 1)
        text_ = font.render('수익 할당량', True, (255, 255, 255))
        text2_ = font.render(f'${INGAME['QUOTA']} / ${INGAME['TARGET_QUOTA']}', True, (255, 255, 255))
        screen.blit(text_, (CONFIG['SCREEN_WIDTH'] - 220, 70))
        screen.blit(text2_, (CONFIG['SCREEN_WIDTH'] - 220, 100))
    
    # 시간
    if not INGAME['CUR_MAP'] == 'factory' and not INGAME['CUR_MOD'] == 'READY' and not INGAME['CUR_MAP'] == 'company' and not IS_SHIP:
        HOURS = int(INGAME['TIME'] / 60)
        MINUTES = int(INGAME['TIME'] % 60)
        APM = '오전' if HOURS < 12 else '오후'
        DISPLAY_HOURS = f'0{str(HOURS)}' if HOURS < 10 else str(HOURS)
        DISPLAY_MINUTES = f'0{str(MINUTES)}' if MINUTES < 10 else str(MINUTES)
        text = font.render(f'{APM} {str(DISPLAY_HOURS)}:{str(DISPLAY_MINUTES)}', True, (255, 255, 255))
        screen.blit(text, (50, 50))
    
    if INGAME['SURVIVAL_RESULT']:
        pygame.draw.rect(screen, (150, 31, 27), ((CONFIG['SCREEN_WIDTH'] // 2) - 400, CONFIG['SCREEN_HEIGHT'] // 2 - 100, 800, 200))
        text = font4.render('생존', True, (255, 255, 255))
        screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - 350, CONFIG['SCREEN_HEIGHT'] // 2 - 50))
        text = font2.render('# Player 01', True, (255, 255, 255))
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
    
    if INGAME['MIDNIGHT_MESSAGE']:
        pygame.draw.rect(screen, (150, 31, 27), (CONFIG['SCREEN_WIDTH'] - 500, CONFIG['SCREEN_HEIGHT'] - 400, 400, 125))
        
        text = font2.render(f'자정에 함선이 떠나니', True, (255, 255, 255))
        screen.blit(text, (CONFIG['SCREEN_WIDTH'] - 500 + 25, CONFIG['SCREEN_HEIGHT'] - 400 + 25))
        text = font2.render(f'빠른 복귀 부탁드립니다.', True, (255, 255, 255))
        screen.blit(text, (CONFIG['SCREEN_WIDTH'] - 500 + 25, CONFIG['SCREEN_HEIGHT'] - 400 + 65))
    
    if INGAME['MIDNIGHT_RUN_MESSAGE']:
        pygame.draw.rect(screen, (150, 31, 27), (CONFIG['SCREEN_WIDTH'] - 500, CONFIG['SCREEN_HEIGHT'] - 400, 400, 125))
        
        text = font2.render(f'자정이 되어 함선이', True, (255, 255, 255))
        screen.blit(text, (CONFIG['SCREEN_WIDTH'] - 500 + 25, CONFIG['SCREEN_HEIGHT'] - 400 + 25))
        text = font2.render(f'출발하고 있습니다.', True, (255, 255, 255))
        screen.blit(text, (CONFIG['SCREEN_WIDTH'] - 500 + 25, CONFIG['SCREEN_HEIGHT'] - 400 + 65))
    
    if INGAME['SAVE_ANIMATION']:
        if INGAME['SAVE_ANIMATION_Y'] < 100:
            INGAME['SAVE_ANIMATION_Y'] += 2

        pygame.draw.rect(screen, (150, 31, 27), (CONFIG['SCREEN_WIDTH'] - 300, CONFIG['SCREEN_HEIGHT'] - 200 - INGAME['SAVE_ANIMATION_Y'], 200, 200), 2)
        INGAME['SAVE_ITEM']['IMAGE'].render(screen, (CONFIG['SCREEN_WIDTH'] - 250, CONFIG['SCREEN_HEIGHT'] - 150 - INGAME['SAVE_ANIMATION_Y']))

        text = font.render(f'함선에 저장됨', True, (150, 31, 27))
        screen.blit(text, (CONFIG['SCREEN_WIDTH'] - 255, CONFIG['SCREEN_HEIGHT'] + 10 - INGAME['SAVE_ANIMATION_Y']))

def draw_player_detail():
    global CUR_ITEM_EXISTS

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

    # 플레이어 상세
    PLAYER_OUTLINE_IMAGE.render(screen, (50, 130))
    PLAYER_DETAIL_IMAGE.render(screen, (90, 160))

    # 게이지 표시
    INVENTORY = reduce(lambda acc, cur: acc + [cur.ID], Player.INVENTORY, [])
    if 'flashlight' in INVENTORY:
        pygame.draw.rect(screen, (255, 255, 0), (50, 300, 120, 30), 3)
        pygame.draw.rect(screen, (255, 255, 0), (60, 310, Player.INVENTORY[INVENTORY.index('flashlight')].GUAGE, 10))

def draw_uiux():
    # 터미널이 열려있다면
    if INGAME['TERMINAL']:
        TERMINAL_SCREEN_IMAGE.render(screen, ((CONFIG['SCREEN_WIDTH'] // 2) - 450, CONFIG['SCREEN_HEIGHT'] // 2 - 450))

        # 한 줄 마다 나눠서 그리기
        for IDX, LINE in enumerate(INGAME['HELP'].split('\n')):
            text = font.render(LINE.strip(), True, (0, 255, 0))
            screen.blit(text, (((CONFIG['SCREEN_WIDTH'] // 2) - 450) + 200, ((CONFIG['SCREEN_HEIGHT'] // 2) - 450) + 200 + IDX * 30))
        
        text = font.render(f'> {INGAME['COMMAND']}', True, (0, 255, 0))
        screen.blit(text, (((CONFIG['SCREEN_WIDTH'] // 2) - 450) + 200, ((CONFIG['SCREEN_HEIGHT'] // 2) - 450) + 700))
    
    # 로딩중이라면
    if INGAME['LOADING']:
        surface = pygame.Surface((CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT']))
        surface.set_alpha(128)
        surface.fill((0, 0, 0))
        screen.blit(surface, (0, 0))
        text = font4.render('로딩 중...', True, (255, 255, 255))
        screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - (text.get_size()[0] / 2), CONFIG['SCREEN_HEIGHT'] - 200))
    
    if INGAME['WARNING']:
        if INGAME['WARNING_ALPHA'] >= 128: INGAME['WARNING_ALPHA_TOGGLE'] = True
        if INGAME['WARNING_ALPHA'] <= 32: INGAME['WARNING_ALPHA_TOGGLE'] = False
        if INGAME['WARNING_ALPHA_TOGGLE']: INGAME['WARNING_ALPHA'] -= 1
        else: INGAME['WARNING_ALPHA'] += 1

        surface = pygame.Surface((CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT']))
        surface.set_alpha(INGAME['WARNING_ALPHA'])
        surface.fill((255, 0, 0))
        screen.blit(surface, (0, 0))
    
    if INGAME['FIRE_MESSAGE']:
        text = font2.render('\'# Player 01\'은 끝내 임무를 완수하지 못했습니다.'[0:INGAME['FIRE_MESSAGE_IDX']], True, (255, 255, 255))
        screen.blit(text, ((CONFIG['SCREEN_WIDTH'] // 2) - (text.get_size()[0] / 2), CONFIG['SCREEN_HEIGHT'] - 100))
    
    if INGAME['FIRE_BUTTON']:
        text = font2.render('다시하기', True, (0, 0, 0))
        SURFACE_RECT = (100, CONFIG['SCREEN_HEIGHT'] - 100 - text.get_size()[1] + (10 * 2), text.get_size()[0] + (20 * 2), text.get_size()[1] + (10 * 2))
        INGAME['FIRE_BUTTON_RECT'] = SURFACE_RECT
        SURFACE_COLOR = (255, 255, 255)
        SURFACE_RADIUS = 10
        pygame.draw.rect(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RADIUS, SURFACE_RECT[1], SURFACE_RECT[2] - 2 * SURFACE_RADIUS, SURFACE_RECT[3]))
        pygame.draw.rect(screen, SURFACE_COLOR, (SURFACE_RECT[0], SURFACE_RECT[1] + SURFACE_RADIUS, SURFACE_RECT[2], SURFACE_RECT[3] - 2 * SURFACE_RADIUS))
        pygame.draw.circle(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RADIUS, SURFACE_RECT[1] + SURFACE_RADIUS), SURFACE_RADIUS)
        pygame.draw.circle(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RECT[2] - SURFACE_RADIUS, SURFACE_RECT[1] + SURFACE_RADIUS), SURFACE_RADIUS)
        pygame.draw.circle(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RADIUS, SURFACE_RECT[1] + SURFACE_RECT[3] - SURFACE_RADIUS), SURFACE_RADIUS)
        pygame.draw.circle(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RECT[2] - SURFACE_RADIUS, SURFACE_RECT[1] + SURFACE_RECT[3] - SURFACE_RADIUS), SURFACE_RADIUS)
        pygame.draw.rect(screen, SURFACE_COLOR, (SURFACE_RECT[0] + SURFACE_RADIUS, SURFACE_RECT[1] + SURFACE_RECT[3] - SURFACE_RADIUS, SURFACE_RECT[2] - 2 * SURFACE_RADIUS, SURFACE_RADIUS))
        screen.blit(text, (SURFACE_RECT[0] + 20, SURFACE_RECT[1] + 10))

def camera_movement():
    if INGAME['CUR_MAP'] == 'experimentation':
        if INGAME['CAMERA_X'] <= -7 * CONFIG['TILE_SIZE']:
            INGAME['CAMERA_MOVE'] = False

            def camera_move_false():
                INGAME['CAMERA_X'] = 0
                INGAME['CAMERA_Y'] = 0
            
            Timer(2, camera_move_false).start()
        
        else: INGAME['CAMERA_X'] -= 2

        if Open1.RECT.y >= 19 * CONFIG['TILE_SIZE']:
            Open1.RECT.y -= 1

        if Open2.RECT.y <= 23 * CONFIG['TILE_SIZE']:
            Open2.RECT.y += 1
    
    elif INGAME['CUR_MAP'] == 'company':
        if INGAME['CAMERA_X'] <= -7 * CONFIG['TILE_SIZE']:
            INGAME['CAMERA_MOVE'] = False

            def camera_move_false():
                INGAME['CAMERA_X'] = 0
                INGAME['CAMERA_Y'] = 0
            
            Timer(2, camera_move_false).start()
        
        else: INGAME['CAMERA_X'] -= 2

        if Open3.RECT.y >= 54 * CONFIG['TILE_SIZE']:
            Open3.RECT.y -= 1

        if Open4.RECT.y <= 58 * CONFIG['TILE_SIZE']:
            Open4.RECT.y += 1

def delivery_movement():
    if INGAME['CUR_MAP'] == 'experimentation':
        if INGAME['DELIVERY_LANDING']:
            # 착륙
            if Delivery.RECT.y >= 20 * CONFIG['TILE_SIZE']:
                Delivery.CUR_IMAGE = Delivery.FRONT_IMAGE
                
                if not Delivery.ALREADY_PLAY:
                    DELIVERY_COME.stop()
                    DELIVERY_DROP_ITEM.play()

                    def music_play():
                        MAIN_MUSIC_1.stop()
                        MAIN_MUSIC_2.stop()

                        DELIVERY_MUSIC.play()
                    Timer(1.75, music_play).start()
                Delivery.ALREADY_PLAY = True
            
            # 하늘에서 날라오기
            else: Delivery.move(0, Delivery.SPEED, True)
        
        else:
            Delivery.ALREADY_PLAY = False
            DELIVERY_MUSIC.stop()

            # 이륙
            if Delivery.RECT.y <= -10 * CONFIG['TILE_SIZE']: Delivery.CUR_IMAGE = Delivery.FRONT_IMAGE

            # 하늘로 날라가기
            else: Delivery.move(0, -Delivery.SPEED, True)
    
    elif INGAME['CUR_MAP'] == 'company':
        if INGAME['DELIVERY_LANDING']:
            # 착륙
            if Delivery2.RECT.y >= 54 * CONFIG['TILE_SIZE']: Delivery2.CUR_IMAGE = Delivery2.FRONT_IMAGE
            # 하늘에서 날라오기
            else: Delivery2.move(0, Delivery2.SPEED, True)
        
        else:
            DELIVERY_MUSIC.stop()
            # 이륙
            if Delivery2.RECT.y <= -10 * CONFIG['TILE_SIZE']: Delivery2.CUR_IMAGE = Delivery2.FRONT_IMAGE
            # 하늘로 날라가기
            else: Delivery2.move(0, -Delivery2.SPEED, True)

def player_movement():
    global CUR_ITEM_EXISTS

    text = None

    # 플레이어 이동
    if not Player.DIED and INGAME['CAMERA_X'] == 0 and not INGAME['CHARGING'] and not INGAME['WARNING'] and not INGAME['FIRE']:
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
    if CONFIG['DEBUG']: pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], Player.INTERACTION_DISTANCE, 1)
    
    for ITEM in CUR_MAP['OBJECTS']:
        # 플레이어 원형 경계
        dist = distance(Player.RECT, ITEM.RECT)

        if dist < Player.INTERACTION_DISTANCE:
            # 단축키 + 메시지 표시
            if ITEM.TYPE == 'item':
                shortcut = '(E)'

                if len(OBJECT.INVENTORY) == 8: shortcut = '(가득참)'
                OBJECT.CONTAIN = ITEM

                text = font.render(f'{shortcut} {ITEM.DISPLAY_NAME} 들기', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'terminal':
                OBJECT.CONTAIN = ITEM

                text = font.render('(E) 터미널 사용하기', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'door':
                OBJECT.CONTAIN = ITEM

                shortcut = '(E)'
                if ITEM.LOCKED: shortcut = '(잠김)'

                message = '문 열기'
                if ITEM.OPENED: message = '문 닫기'
                
                text = font.render(f'{shortcut} {message}', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'enter':
                OBJECT.CONTAIN = ITEM

                text = font.render('(E) 입장하기', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'exit':
                OBJECT.CONTAIN = ITEM

                text = font.render('(E) 나가기', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'delivery':
                OBJECT.CONTAIN = ITEM

                text = font.render('(E) 열기', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'charger':
                OBJECT.CONTAIN = ITEM

                shortcut = '(E)'
                message = '충전할 수 있는 아이템이 아닙니다.'

                if CUR_ITEM_EXISTS:
                    CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                    if CUR_ITEM.ID == 'flashlight':
                        message = '충전하기'

                text = font.render(f'{shortcut} {message}', True, (255, 255, 255), (0, 0, 0))
                break

            elif ITEM.TYPE == 'salemanager':
                OBJECT.CONTAIN = ITEM
                
                text = font.render('(E) 올려두기', True, (255, 255, 255), (0, 0, 0))
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
    
    return text

def resurrection():
    MAIN_MUSIC_1.stop()
    MAIN_MUSIC_2.stop()
    JESTER_SCREAM.stop()
    BRACKEN_ANGRY.stop()

    Player.DIED = False

    WILL_REMOVES = []
    for ITEM in INGAME['SAVES']:
        if not ITEM.ID in ['key', 'flashlight', 'shovel']:
            WILL_REMOVES.append(ITEM)
    
    try:
        for ITEM in WILL_REMOVES:
            INGAME['SAVES'].remove(ITEM)
    except: ...

    MAP_REDUCED = Map.reduced('ID')
    NEXT_MAP_IDX = MAP_REDUCED.index('ship')
    NEXT_MAP = INGAME['MAPS'][NEXT_MAP_IDX]

    for ITEM in INGAME['SAVES']:
        ITEM.RECT.x = (get_ship_rect(Ship.MAP_ID).width // 2) - 1
        ITEM.RECT.y = (get_ship_rect(Ship.MAP_ID).height // 2) - 1
        NEXT_MAP['OBJECTS'].append(ITEM)
    
    Player.FRONT_IMAGE = PLAYER_FRONT_IMAGE
    Player.BACK_IMAGE = PLAYER_BACK_IMAGE
    Player.LEFT_IMAGE = PLAYER_LEFT_IMAGE
    Player.RIGHT_IMAGE = PLAYER_RIGHT_IMAGE
    Player.FRONT_WALK_IMAGE = PLAYER_FRONT_WALK_IMAGE
    Player.BACK_WALK_IMAGE = PLAYER_BACK_WALK_IMAGE
    Player.LEFT_WALK_IMAGE = PLAYER_LEFT_WALK_IMAGE
    Player.RIGHT_WALK_IMAGE = PLAYER_RIGHT_WALK_IMAGE

    Player.DECREASING = False
    Player.SPEED = 1
    Player.map_to(False, Ship.MAP_ID)
    Player.teleport(get_ship_rect(Ship.MAP_ID).width // 2, get_ship_rect(Ship.MAP_ID).height // 2)
    INGAME['TIME'] = 60 * 8
    INGAME['CUR_MOD'] = 'READY'
    INGAME['CUR_MAP'] = Ship.MAP_ID

    INGAME['SURVIVAL_RESULT'] = True
    def survival_result_false():
        INGAME['SURVIVAL_RESULT'] = False

        if INGAME['DAY'] - 1 < 0:
            run_fire()
        
        else:
            DECREASE_DAY.play()
            INGAME['DAY'] -= 1
            INGAME['DAY_RESULT'] = True
            def day_result_false():
                INGAME['DAY_RESULT'] = False
            Timer(4, day_result_false).start()
    Timer(5, survival_result_false).start()

def get_sound_volume(RECT):
    DX = abs((Player.RECT.x + (CONFIG['TILE_SIZE'] / 2)) - (RECT.x + RECT.width))
    DY = abs((Player.RECT.y + (CONFIG['TILE_SIZE'] / 2)) - (RECT.y + RECT.height))
    VOLUME = CONFIG['MASTER_SOUND'] - ((DX if DX > DY else DY) / Player.DISTANCE)
    return 0 if VOLUME < 0 else VOLUME

def is_visible(OBJECT):
    return (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) in INGAME['VISIBLE_TILES']

def track(callback=None):
    if OBJECT.NAVIGATE and len(OBJECT.NAVIGATE) > OBJECT.NAVIGATE_IDX:
        CUR_NAVIGATE = OBJECT.NAVIGATE[OBJECT.NAVIGATE_IDX]

        if CUR_NAVIGATE[1] * CONFIG['TILE_SIZE'] > OBJECT.RECT.x: OBJECT.move(OBJECT.SPEED, 0)
        if CUR_NAVIGATE[1] * CONFIG['TILE_SIZE'] < OBJECT.RECT.x: OBJECT.move(-OBJECT.SPEED, 0)
        if CUR_NAVIGATE[0] * CONFIG['TILE_SIZE'] > OBJECT.RECT.y: OBJECT.move(0, OBJECT.SPEED)
        if CUR_NAVIGATE[0] * CONFIG['TILE_SIZE'] < OBJECT.RECT.y: OBJECT.move(0, -OBJECT.SPEED)
        
        if CUR_NAVIGATE == (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])):
            if distance(Player.RECT, OBJECT.RECT) < Player.DISTANCE and not OBJECT.TRANSPARENT:
                if OBJECT.WALK_SOUND:
                    VOLUME = get_sound_volume(OBJECT.RECT)
                    OBJECT.WALK_SOUND.set_volume(VOLUME)
                    OBJECT.WALK_SOUND.play()

            OBJECT.NAVIGATE_IDX += 1
            return

    if callback: callback()

def open_door():
    for DOOR in CUR_MAP['OBJECTS']:
        if DOOR.TYPE == 'door' and not DOOR.OPENED:
            if distance(OBJECT.RECT, DOOR.RECT) < OBJECT.INTERACTION_DISTANCE:
                if dist < Player.DISTANCE:
                    SOUND = random.choice([DOOR_OPEN_1, DOOR_OPEN_2])
                    VOLUME = get_sound_volume(OBJECT.RECT)
                    SOUND.set_volume(VOLUME)
                    SOUND.play()
                
                DOOR.LOCKED = False
                DOOR.OPENED = True

                IMAGE = OPENED_DOOR_IMAGE
                if DOOR.FRONT_IMAGE == DOOR_2_IMAGE: IMAGE = OPENED_DOOR_2_IMAGE
                DOOR.CUR_IMAGE = IMAGE

def attack(CONDITION=None):
    global CUR_ITEM_EXISTS

    if not CONDITION: CONDITION = distance(OBJECT.RECT, Player.RECT) < OBJECT.ATTACK_DISTANCE

    if CONDITION:
        Player.DECREASING = True
        Player.DECREASING_SIZE = OBJECT.DAMAGE
        
        if Player.HP < 0 and not Player.DIED:
            Player.DIED = True

            IMAGE = gif_pygame.load('images/player/dead.gif')
            gif_pygame.transform.scale(IMAGE, (1 * CONFIG['TILE_SIZE'], 1 * CONFIG['TILE_SIZE']))
            Player.FRONT_IMAGE = IMAGE
            Player.BACK_IMAGE = IMAGE
            Player.LEFT_IMAGE = IMAGE
            Player.RIGHT_IMAGE = IMAGE
            Player.FRONT_WALK_IMAGE = IMAGE
            Player.BACK_WALK_IMAGE = IMAGE
            Player.LEFT_WALK_IMAGE = IMAGE
            Player.RIGHT_WALK_IMAGE = IMAGE
            
            CUR_ITEM_EXISTS = False
            WILL_DROP = []
            for CUR_ITEM in Player.INVENTORY:
                WILL_DROP.append(CUR_ITEM)
            
            for ITEM in WILL_DROP:
                Player.drop_item(ITEM)
            
            Timer(3, resurrection).start()
    else: Player.DECREASING = False

def monster_movement():
    global CUR_ITEM_EXISTS
    
    dist = distance(OBJECT.RECT, Player.RECT)

    if CONFIG['DEBUG']:
        pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], OBJECT.DISTANCE, 1)
        pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], OBJECT.ATTACK_DISTANCE, 1)
        pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], OBJECT.INTERACTION_DISTANCE, 1)
        if OBJECT.NAVIGATE and len(OBJECT.NAVIGATE) >= 2: pygame.draw.lines(screen, OBJECT.NAVIGATE_COLOR, False, reduce(lambda acc, cur: acc + [((cur[1] * CONFIG['TILE_SIZE']) + OFFSET_X + (CONFIG['TILE_SIZE'] / 2), (cur[0] * CONFIG['TILE_SIZE']) + OFFSET_Y + (CONFIG['TILE_SIZE'] / 2))], OBJECT.NAVIGATE, []))

    # 비축벌레
    if OBJECT.ID == 'hoarding bug':
        # 문 열기
        open_door()

        # 발소리
        OBJECT.WALK_SOUND = random.choice([HOARDING_BUG_WALK_1, HOARDING_BUG_WALK_2, HOARDING_BUG_WALK_3, HOARDING_BUG_WALK_4])

        # 네비게이터 따라가기
        track()

        # 주위에 있는 아이템
        for ITEM in CUR_MAP['OBJECTS']:
            if ITEM.TYPE == 'item':
                dist = distance(OBJECT.RECT, ITEM.RECT)

                if dist < OBJECT.INTERACTION_DISTANCE and len(OBJECT.INVENTORY) == 0 and not ITEM in OBJECT.ALREADY_ITEMS:
                    OBJECT.CONTAIN = ITEM
        
        # 아이템 수집
        if OBJECT.CONTAIN:
            OBJECT.ALREADY_ITEMS.append(OBJECT.CONTAIN)
            OBJECT.grab_item()

            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), OBJECT.SPAWN_POINT)
            OBJECT.NAVIGATE_IDX = 0
        
        # 아이템 버리기
        if len(OBJECT.INVENTORY) > 0 and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.drop_item(OBJECT.INVENTORY[0])
            
            NAVIGATE_ITEM = None
            MIN_DISTANCE = float('inf')

            FACTORY = INGAME['MAPS'][Map.reduced('ID').index('factory')]
            for ITEM in FACTORY['OBJECTS']:
                if ITEM.TYPE == 'item' and not ITEM in OBJECT.ALREADY_ITEMS:
                    dist = distance(OBJECT.RECT, ITEM.RECT)

                    if dist < MIN_DISTANCE:
                        MIN_DISTANCE = dist
                        NAVIGATE_ITEM = ITEM
            
            if NAVIGATE_ITEM:
                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(NAVIGATE_ITEM.RECT.y / CONFIG['TILE_SIZE']), int(NAVIGATE_ITEM.RECT.x / CONFIG['TILE_SIZE'])))
                OBJECT.NAVIGATE_IDX = 0

    # 코일헤드
    elif OBJECT.ID == 'coil head':
        # 공격
        attack()
        
        # 문 열기
        open_door()

        # 발소리
        OBJECT.WALK_SOUND = random.choice([COILHEAD_WALK_1, COILHEAD_WALK_2, COILHEAD_WALK_3, COILHEAD_WALK_4])
        
        # 네비게이터 따라가기
        def retrack():
            track()
        track(retrack)

        def search(CONDITION):
            if CONDITION:
                OBJECT.SPEED = 0
                if not OBJECT.ALREADY_PLAY:
                    random.choice([COILHEAD_ATTACK_1, COILHEAD_ATTACK_2]).play()
                OBJECT.ALREADY_PLAY = True
                OBJECT.ALREADY_NOPLAY = False
            else:
                OBJECT.SPEED = 2
                OBJECT.ALREADY_PLAY = False
                if not OBJECT.ALREADY_NOPLAY:
                    OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))
                    OBJECT.NAVIGATE_IDX = 0
                OBJECT.ALREADY_NOPLAY = True
        
        if is_visible(OBJECT) or dist < OBJECT.DISTANCE and OBJECT.TRACK:
            if Player.LAST_ROTATE == 'front': search(Player.RECT.y < OBJECT.RECT.y)
            elif Player.LAST_ROTATE == 'back': search(Player.RECT.y > OBJECT.RECT.y)
            elif Player.LAST_ROTATE == 'left': search(Player.RECT.x > OBJECT.RECT.x)
            elif Player.LAST_ROTATE == 'right': search(Player.RECT.x < OBJECT.RECT.x)

        if OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0
    
    # 브래켄
    elif OBJECT.ID == 'bracken':
        # 문 열기
        open_door()
        
        # 돌아다니다가
        if not OBJECT.ANGRY and not OBJECT.TRACK and not OBJECT.ALREADY_NAVIGATE:
            RECT_X = random.randrange(0, OUTPUT[1])
            RECT_Y = random.randrange(0, OUTPUT[2])

            if Factory.MAP_ARRAY[RECT_Y][RECT_X] == 0:
                OBJECT.ALREADY_NAVIGATE = True
                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (RECT_Y, RECT_X))
                
                if OBJECT.NAVIGATE: OBJECT.NAVIGATE_IDX = 0
                else: OBJECT.ALREADY_NAVIGATE = False
        
        # 다왔다면
        if not OBJECT.ANGRY and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if not OBJECT.ANGRY and OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        # 플레이어와 마주치면
        if not OBJECT.ANGRY and not OBJECT.TRACK and distance(OBJECT.RECT, Player.RECT) < OBJECT.DISTANCE:
            OBJECT.TRACK = True
            
            OBJECT.TIMER = True
            OBJECT.START_TIME = time.time()
            OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT

        # 4초동안 뒤로 도망가기 (astar)
        track()

        # 4초가 지나도 플레이어가 계속 쳐다보고 있다면 공격 시작
        if not OBJECT.ALREADY_TIMER and OBJECT.TIMER and time.time() > OBJECT.END_TIME:
            if INGAME['CUR_MAP'] == 'factory' and distance(OBJECT.RECT, Player.RECT) < OBJECT.DISTANCE and (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) in INGAME['VISIBLE_TILES']:
                OBJECT.ALREADY_TIMER = True
                OBJECT.START_TIME = 0
                OBJECT.END_TIME = 0

                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))
                if not OBJECT.NAVIGATE: OBJECT.TRACK = False
                else: OBJECT.NAVIGATE_IDX = 0

                OBJECT.ANGRY = True
                OBJECT.SPEED = 2
                BRACKEN_ANGRY.play()
            
            else:
                OBJECT.TRACK = False
                
                OBJECT.TIMER = False
                OBJECT.START_TIME = 0
                OBJECT.END_TIME = 0

        # 다왔다면
        if OBJECT.ANGRY and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if OBJECT.ANGRY and OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        if OBJECT.ANGRY:
            # 공격중이라면 플레이어를 추적 (astar)
            track()

            # 공격중이고, 플레이어가 브래켄의 attack distance안에 있다면 플레이어 목꺽기 (attack)
            attack()
            
            VOLUME = get_sound_volume(OBJECT.RECT)
            BRACKEN_ANGRY.set_volume(VOLUME)
    
    # 제스터
    elif OBJECT.ID == 'jester':
        # 문 열기
        open_door()
        
        # 돌아다니다가
        if not OBJECT.ANGRY and not OBJECT.DOING and not OBJECT.TRACK and not OBJECT.ALREADY_NAVIGATE:
            RECT_X = random.randrange(0, OUTPUT[1])
            RECT_Y = random.randrange(0, OUTPUT[2])

            if Factory.MAP_ARRAY[RECT_Y][RECT_X] == 0:
                OBJECT.ALREADY_NAVIGATE = True
                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (RECT_Y, RECT_X))
                
                if OBJECT.NAVIGATE: OBJECT.NAVIGATE_IDX = 0
                else: OBJECT.ALREADY_NAVIGATE = False
        
        # 다왔다면
        if not OBJECT.ANGRY and not OBJECT.DOING and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if not OBJECT.ANGRY and not OBJECT.DOING and OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        # 플레이어와 마주치면
        if not OBJECT.ANGRY and not OBJECT.DOING and not OBJECT.TRACK and distance(OBJECT.RECT, Player.RECT) < OBJECT.DISTANCE:
            OBJECT.TRACK = True

            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if OBJECT.NAVIGATE:
                OBJECT.NAVIGATE_IDX = 0
                OBJECT.TIMER = True
                OBJECT.START_TIME = time.time()
                OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT

        # 20초동안 플레이어를 추적 (astar)
        track()

        # 20초가 지난 후 플레이어가 Factory에 있다면
        if not OBJECT.ALREADY_TIMER and OBJECT.TIMER and time.time() > OBJECT.END_TIME and INGAME['CUR_MAP'] == 'factory':
            # 오르골을 돌리며, 오르골 사운드 재생 (오르골 돌리는 소리랑 함께)
            OBJECT.ALREADY_TIMER = True
            OBJECT.TIMEOUT = 39
            OBJECT.START_TIME = time.time()
            OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT

            OBJECT.DOING = True
            OBJECT.CUR_IMAGE = JESTER_DOING_IMAGE

            JESTER_DOING.play()
            def crank_sound(OBJECT):
                if OBJECT.ALREADY_TIMER:
                    SOUND = random.choice([JESTER_DOING_CRANK_1, JESTER_DOING_CRANK_2, JESTER_DOING_CRANK_3])
                    VOLUME = get_sound_volume(OBJECT.RECT)
                    SOUND.set_volume(VOLUME)
                    SOUND.play()
            set_interval(crank_sound, 1, OBJECT)

        # 오르골이 끝나면
        if OBJECT.ALREADY_TIMER and OBJECT.TIMER and time.time() > OBJECT.END_TIME:
            OBJECT.ALREADY_TIMER = False
            OBJECT.TIMER = False
            OBJECT.TIMEOUT = 0
            OBJECT.START_TIME = 0
            OBJECT.END_TIME = 0

            # 변신을 하면서, 변신 사운드 재생
            OBJECT.DOING = False
            OBJECT.CUR_IMAGE = JESTER_OPENED_IMAGE
            JESTER_POP.play()
            JESTER_SCREAM.play(-1)

            OBJECT.DAMAGE = 100
            OBJECT.SPEED = 2
            OBJECT.ANGRY = True
        
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))
            if not OBJECT.NAVIGATE: OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (3, 3))
            OBJECT.NAVIGATE_IDX = 0

        if OBJECT.ANGRY:
            # 변신이 끝나면 플레이어를 추적 (astar)
            track()
            OBJECT.CUR_IMAGE = JESTER_OPENED_WALK_IMAGE

            # 발소리
            OBJECT.WALK_SOUND = random.choice([JESTER_WALK_1, JESTER_WALK_2, JESTER_WALK_3])

            # 변신이 끝나고, 플레이어가 제스터의 attack distance안에 있다면 플레이어 먹기
            attack()

        # 다왔다면
        if OBJECT.ANGRY and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if OBJECT.ANGRY and OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0
        
        VOLUME = get_sound_volume(OBJECT.RECT)
        if OBJECT.DOING:
            JESTER_DOING.set_volume(VOLUME)
            JESTER_DOING_CRANK_1.set_volume(VOLUME)
            JESTER_DOING_CRANK_2.set_volume(VOLUME)
            JESTER_DOING_CRANK_3.set_volume(VOLUME)
        if OBJECT.ANGRY:
            JESTER_POP.set_volume(VOLUME)
            JESTER_SCREAM.set_volume(VOLUME)
    
    # 유령소녀
    elif OBJECT.ID == 'girl':
        # 네비게이터 따라가기
        track()

        # 발소리
        OBJECT.WALK_SOUND = random.choice([GIRL_WALK_1, GIRL_WALK_2, GIRL_WALK_3, GIRL_WALK_4, GIRL_WALK_5, GIRL_WALK_6])

        # 투명한 상태로 돌아다니다가
        if OBJECT.TRANSPARENT and not OBJECT.ANGRY and not OBJECT.TRACK and not OBJECT.ALREADY_NAVIGATE:
            RECT_X = random.randrange(0, OUTPUT[1])
            RECT_Y = random.randrange(0, OUTPUT[2])

            if Factory.MAP_ARRAY[RECT_Y][RECT_X] == 0:
                OBJECT.ALREADY_NAVIGATE = True
                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (RECT_Y, RECT_X))
                
                if OBJECT.NAVIGATE: OBJECT.NAVIGATE_IDX = 0
                else: OBJECT.ALREADY_NAVIGATE = False
        
        # 다왔다면
        if OBJECT.TRANSPARENT and not OBJECT.ANGRY and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if OBJECT.ANGRY and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        # 플레이어가 유령소녀의 distance 안에 있다면
        if OBJECT.TRANSPARENT and not OBJECT.ANGRY and not OBJECT.TRACK and distance(OBJECT.RECT, Player.RECT) < OBJECT.DISTANCE:
            OBJECT.TRACK = True

            # 투명한 상태 해제
            OBJECT.TRANSPARENT = False

            # 웃는소리 재생
            random.choice([GIRL_LAUGH_1, GIRL_LAUGH_2]).play()

            # 숨소리 재생
            random.choice([GIRL_BREATH_1, GIRL_BREATH_2]).play()

            OBJECT.NAVIGATE = []
            OBJECT.NAVIGATE_IDX = 0
            OBJECT.CUR_IMAGE = GIRL_IMAGE
        
        if not OBJECT.TRANSPARENT: track()

        # 투명한 상태가 해제되어있고, 플레이어가 바라봤다면 스택을 추가하고 도망가기
        def search(CONDITION):
            if CONDITION and not OBJECT.ALREADY_PLAY:
                OBJECT.STACK += 1

                OBJECT.TRACK = False
                OBJECT.DOING = True

                OBJECT.NAVIGATE = [(int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']) - 4, int(OBJECT.RECT.x / CONFIG['TILE_SIZE']))]
                if OBJECT.STACK >= 3:
                    OBJECT.ANGRY = True
                    OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))
                OBJECT.NAVIGATE_IDX = 0

                OBJECT.ALREADY_PLAY = True
                OBJECT.ALREADY_NOPLAY = False

                if OBJECT.STACK < 3:
                    def other_movement(OBJECT):
                        OBJECT.TRANSPARENT = True

                        OBJECT.NAVIGATE = []
                        OBJECT.NAVIGATE_IDX = 0

                        OBJECT.teleport(1 * CONFIG['TILE_SIZE'], (OUTPUT[2] - 2) * CONFIG['TILE_SIZE'])

                        OBJECT.DOING = False
                        OBJECT.TRACK = False
                        OBJECT.ALREADY_NAVIGATE = False
                        OBJECT.ALREADY_PLAY = False
                        OBJECT.ALREADY_NOPLAY = True
                    Timer(.3, other_movement, (OBJECT,)).start()
        
        if not OBJECT.DOING and not OBJECT.TRANSPARENT or OBJECT.TRACK:
            if Player.LAST_ROTATE == 'front': search(Player.RECT.y < OBJECT.RECT.y)
            elif Player.LAST_ROTATE == 'back': search(Player.RECT.y > OBJECT.RECT.y)
            elif Player.LAST_ROTATE == 'left': search(Player.RECT.x > OBJECT.RECT.x)
            elif Player.LAST_ROTATE == 'right': search(Player.RECT.x < OBJECT.RECT.x)
        
        if OBJECT.ANGRY and not (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) in INGAME['VISIBLE_TILES'] and not (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) == (int(Player.RECT.x / CONFIG['TILE_SIZE']), int(Player.RECT.y / CONFIG['TILE_SIZE'])):
            OBJECT.ANGRY = False
            OBJECT.TRANSPARENT = True

            OBJECT.teleport(1 * CONFIG['TILE_SIZE'], (OUTPUT[2] - 2) * CONFIG['TILE_SIZE'])

            OBJECT.TRACK = False
            OBJECT.ALREADY_NAVIGATE = False
            OBJECT.ALREADY_PLAY = False
            OBJECT.ALREADY_NOPLAY = True

        if OBJECT.ANGRY: attack()
    
    # 가면 쓴 사람
    elif OBJECT.ID == 'mask':
        # 문 열기
        open_door()
        
        # 돌아다니다가
        if not OBJECT.TIMER and not OBJECT.ANGRY and not OBJECT.TRACK and not OBJECT.ALREADY_NAVIGATE:
            RECT_X = random.randrange(0, OUTPUT[1])
            RECT_Y = random.randrange(0, OUTPUT[2])

            if Factory.MAP_ARRAY[RECT_Y][RECT_X] == 0:
                OBJECT.ALREADY_NAVIGATE = True
                OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (RECT_Y, RECT_X))
                
                if OBJECT.NAVIGATE: OBJECT.NAVIGATE_IDX = 0
                else: OBJECT.ALREADY_NAVIGATE = False
        
        # 다왔다면
        if not OBJECT.TIMER and not OBJECT.ANGRY and not OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]: OBJECT.ALREADY_NAVIGATE = False
        if not OBJECT.TIMER and not OBJECT.ANGRY and OBJECT.TRACK and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        # 플레이어와 마주치면
        if not OBJECT.TIMER and not OBJECT.ANGRY and not OBJECT.TRACK and distance(OBJECT.RECT, Player.RECT) < OBJECT.DISTANCE:
            OBJECT.NAVIGATE = []
            OBJECT.NAVIGATE_IDX = 0
            OBJECT.TIMER = True
            OBJECT.START_TIME = time.time()
            OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT

        # 네비게이터 따라가기
        track()

        # 6초간 대기
        if not OBJECT.ALREADY_TIMER and OBJECT.TIMER and time.time() > OBJECT.END_TIME and INGAME['CUR_MAP'] == 'factory':
            OBJECT.ALREADY_TIMER = True
            OBJECT.START_TIME = 0
            OBJECT.END_TIME = 0

            OBJECT.ANGRY = True

            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        # 발소리
        OBJECT.WALK_SOUND = random.choice([MASK_WALK_1, MASK_WALK_2, MASK_WALK_3, MASK_WALK_4])

        # 다왔다면
        if OBJECT.ANGRY and OBJECT.NAVIGATE and (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])) == OBJECT.NAVIGATE[len(OBJECT.NAVIGATE) - 1]:
            OBJECT.NAVIGATE = astar(Factory.MAP_ARRAY, (int(OBJECT.RECT.y / CONFIG['TILE_SIZE']), int(OBJECT.RECT.x / CONFIG['TILE_SIZE'])), (int(Player.RECT.y / CONFIG['TILE_SIZE']), int(Player.RECT.x / CONFIG['TILE_SIZE'])))

            if not OBJECT.NAVIGATE: OBJECT.TRACK = False
            else: OBJECT.NAVIGATE_IDX = 0

        if OBJECT.ANGRY:
            attack()

            # 플레이어가 멀리있으면 더 빨리 추적
            if distance(OBJECT.RECT, Player.RECT) > OBJECT.DISTANCE: track()
    
    # 지뢰
    elif OBJECT.ID == 'mine':
        if not OBJECT.DOING and not OBJECT.TIMER:
            if OBJECT.ANGRY:
                OBJECT.TIMEOUT = .5
                OBJECT.TIMER = True
                OBJECT.START_TIME = time.time()
                OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT
            
            else:
                OBJECT.TIMEOUT = 5
                OBJECT.TIMER = True
                OBJECT.START_TIME = time.time()
                OBJECT.END_TIME = OBJECT.START_TIME + OBJECT.TIMEOUT
        
        if not OBJECT.DOING and OBJECT.TIMER and time.time() > OBJECT.END_TIME:
            if OBJECT.ANGRY:
                OBJECT.DOING = True
                OBJECT.TIMER = False
                VOLUME = get_sound_volume(OBJECT.RECT)
                MINE_FIRE.set_volume(VOLUME)
                MINE_FIRE.play()
                IMAGE = gif_pygame.load('images/monster/mine/fire.gif')
                gif_pygame.transform.scale(IMAGE, (3 * CONFIG['TILE_SIZE'], 3 * CONFIG['TILE_SIZE']))
                OBJECT.CUR_IMAGE = IMAGE
                OBJECT.teleport(OBJECT.RECT.x - (1 * CONFIG['TILE_SIZE']), OBJECT.RECT.y - (2 * CONFIG['TILE_SIZE']))

                def remove(OBJECT):
                    CUR_MAP['OBJECTS'].remove(OBJECT)
                Timer(1, remove, (OBJECT,)).start()
            
            else:
                OBJECT.TIMER = False
                VOLUME = get_sound_volume(OBJECT.RECT)
                OBJECT.SOUND.set_volume(VOLUME)
                OBJECT.SOUND.play()
        
        if OBJECT.DOING: attack(distance(pygame.Rect(OBJECT.RECT.x + (1 * CONFIG['TILE_SIZE']), OBJECT.RECT.y + (2 * CONFIG['TILE_SIZE']), CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE']), Player.RECT) < OBJECT.ATTACK_DISTANCE)
        
        if not OBJECT.DOING and not OBJECT.ALREADY_PLAY and distance(OBJECT.RECT, Player.RECT) < OBJECT.INTERACTION_DISTANCE:
            OBJECT.ALREADY_PLAY = True
            OBJECT.ANGRY = True
            OBJECT.TIMER = False
            MINE_PRESS.play()
            MINE_TRIGGER.play()

use_interval()

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
            main_event()
        
        elif INGAME['CUR_SCENE'] == 'setting':
            # 현재 씬
            SCENE_REDUCED = Scene.reduced('ID')
            CUR_SCENE_IDX = SCENE_REDUCED.index(INGAME['CUR_SCENE'])
            CUR_SCENE = INGAME['SCENES'][CUR_SCENE_IDX]

            screen.fill((0, 0, 0))

            for INTERFACE in CUR_SCENE['INTERFACES']:
                text_ = font2.render(INTERFACE.INTERFACE_BEFORE_TEXT, True, (255, 255, 255))
                if INTERFACE.INTERFACE_HOVER: text_ = font2.render(INTERFACE.INTERFACE_AFTER_TEXT, True, (255, 255, 255))
                screen.blit(text_, INTERFACE.INTERFACE_RECT)

            pygame.draw.rect(screen, (255, 255, 255), (200, 300, 250, 80), 1)
            pygame.draw.rect(screen, (255, 255, 255), (210, 310, 230, 60), 0 if CONFIG['DEBUG'] else 1)
            text_ = font2.render(f'디버그 모드 {'켜짐' if CONFIG['DEBUG'] else '꺼짐'}', True, (0, 0, 0) if CONFIG['DEBUG'] else (255, 255, 255))
            screen.blit(text_, (225, 320))
            
            text_ = font2.render('주 음량', True, (255, 255, 255))
            screen.blit(text_, (200, 430))
            pygame.draw.rect(screen, (255, 255, 255), (200, 490, 200, 3), 3)
            pygame.draw.circle(screen, (0, 0, 0), (200 + CONFIG['MASTER_SOUND'] * 100, 490), 10)
            pygame.draw.circle(screen, (255, 255, 255), (200 + CONFIG['MASTER_SOUND'] * 100, 490), 5)

            text_ = font2.render('난이도', True, (255, 255, 255))
            screen.blit(text_, (200, 600))
            pygame.draw.rect(screen, (255, 255, 255), (290, 590, 120, 60))
            text_ = font2.render(INGAME['DIFFICULTY'], True, (0, 0, 0))
            screen.blit(text_, (305, 600))
            MESSAGE_1 = '일식보다 몬스터가 적게 스폰됩니다.'
            MESSAGE_2 = '하지만 그만큼 폐기물이 적게 생성됩니다.'
            if INGAME['DIFFICULTY'] == '일식':
                MESSAGE_1 = '평화로움보다 몬스터가 많이 스폰됩니다.'
                MESSAGE_2 = '하지만 그만큼 폐기물이 방대하게 생성됩니다.'
            text_ = font.render(MESSAGE_1, True, (255, 255, 255))
            screen.blit(text_, (200, 670))
            text_ = font.render(MESSAGE_2, True, (255, 255, 255))
            screen.blit(text_, (200, 700))

            text_ = font2.render('기획 · 하성민', True, (255, 255, 255))
            screen.blit(text_, (900, 300 - 50))
            text_ = font2.render('개발 · 고서온, 하성민', True, (255, 255, 255))
            screen.blit(text_, (900, 350 - 50))
            text_ = font2.render('디자인 · 고서온', True, (255, 255, 255))
            screen.blit(text_, (900, 400 - 50))
            text_ = font2.render('2d 리썰컴퍼니?', True, (255, 255, 255))
            screen.blit(text_, (900, 500 - 50))
            text_ = font.render('기존 룰과 다를 것 없이', True, (255, 255, 255))
            screen.blit(text_, (900, 560 - 50))
            text_ = font.render('함선을 타고 여러 행성을 돌아다니면서', True, (255, 255, 255))
            screen.blit(text_, (900, 610 - 50))
            text_ = font.render('폐기물들을 모아 마감일이 지나가기 전에', True, (255, 255, 255))
            screen.blit(text_, (900, 660 - 50))
            text_ = font.render('회사에 폐기물을 팔아 할당량을 채우는', True, (255, 255, 255))
            screen.blit(text_, (900, 710 - 50))
            text_ = font.render('싱글플레이 게임입니다.', True, (255, 255, 255))
            screen.blit(text_, (900, 760 - 50))
            
            # 이벤트
            setting_event()
        
        elif INGAME['CUR_SCENE'] == 'ingame':
            # 현재 맵
            MAP_REDUCED = Map.reduced('ID')
            CUR_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
            CUR_MAP = INGAME['MAPS'][CUR_MAP_IDX]

            CUR_ITEM_EXISTS = len(Player.INVENTORY) > Player.CUR_ITEM_IDX

            if CONFIG['DEBUG']: screen.fill((0, 0, 255))
            else: screen.fill((0, 0, 0))

            if INGAME['FIRE']: STARS_VIDEO.render(screen, ((CONFIG['SCREEN_WIDTH'] // 2) - 450, (CONFIG['SCREEN_HEIGHT'] // 2) - 450))
            
            keys = pygame.key.get_pressed()

            # 이벤트
            ingame_event()

            sum_text = None
            
            # 터미널이 안열려있으면
            if not INGAME['TERMINAL']:
                if INGAME['FIRE']: Player.RECT.x += 5
                
                # 카메라 무빙
                if INGAME['CAMERA_MOVE']: camera_movement()
                
                # 카메라 시점 계산
                OFFSET_X = CONFIG['SCREEN_WIDTH'] // 2 - Player.RECT.centerx + INGAME['CAMERA_X']
                OFFSET_Y = CONFIG['SCREEN_HEIGHT'] // 2 - Player.RECT.centery + INGAME['CAMERA_Y']

                # 타일 그리기
                draw_tile()

                # 현재 맵에 존재하는 오브젝트들
                for OBJECT in CUR_MAP['OBJECTS']:
                    text = None

                    # 카메라 시점에 대한 오브젝트 위치
                    OBJECT_RECT = OBJECT.RECT.move(OFFSET_X, OFFSET_Y)

                    # 배달이라면
                    if OBJECT.TYPE == 'delivery' and INGAME['DELIVERY']: delivery_movement()

                    # 플레이어라면
                    elif OBJECT.TYPE == 'player': text = player_movement()

                    # 몬스터라면 (제작중)
                    elif OBJECT.TYPE == 'monster': monster_movement()
                    
                    # 오브젝트 이미지 그리기
                    dist = distance(Player.RECT, OBJECT.RECT)
                    if not OBJECT.ID == 'girl' and Player.NAVIGATE == (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) or not OBJECT.ID == 'girl' and (int(OBJECT.RECT.x / CONFIG['TILE_SIZE']), int(OBJECT.RECT.y / CONFIG['TILE_SIZE'])) in INGAME['VISIBLE_TILES'] or INGAME['FIRE'] or OBJECT.ID == 'girl' and not OBJECT.TRANSPARENT or OBJECT.ID == 'mine' and OBJECT.ANGRY: draw_object()

                    # 스캔 정보 표시
                    if INGAME['SCAN']: sum_text = draw_scan(dist)

                    # 아이템 상호작용 표시
                    if text and Player.CONTAIN: screen.blit(text, (Player.CONTAIN.RECT.centerx + OFFSET_X - (text.get_size()[0] / 2), Player.CONTAIN.RECT.y + OFFSET_Y - 50))
            
            # 레터박스 그리기
            draw_letterbox()

            # 총합계 표시
            if INGAME['SCAN'] and sum_text: screen.blit(sum_text, (50, 80))
            
            # 플레이어가 함선 안에 있는지
            IS_SHIP = is_ship()

            # 플레이어 상세 그리기 (들고있는 아이템, 손전등 비네트, 인벤토리 아이템, 게이지)
            draw_player_detail()

            # 상황 (할당량, 마감일, 시간) 그리기
            draw_situation()

            # UI 그리기
            draw_uiux()

            if Player.DECREASING:
                surface = pygame.Surface((CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT']))
                surface.set_alpha(64)
                surface.fill((255, 0, 0))
                screen.blit(surface, (0, 0))

            # 공장 로비 사운드 볼륨 조절
            if INGAME['CUR_MAP'] == 'factory':
                RECT = pygame.Rect(0, 0, 6 * CONFIG['TILE_SIZE'], 6 * CONFIG['TILE_SIZE'])
                if distance(RECT, Player.RECT):
                    VOLUME = get_sound_volume(RECT)
                    LOBBY_MUSIC_3.set_volume(VOLUME)
            
            # 딜리버리 사운드 볼륨 조절
            if INGAME['CUR_MAP'] == 'experimentation':
                if distance(Delivery.RECT, Player.RECT):
                    VOLUME = get_sound_volume(Delivery.RECT)
                    DELIVERY_COME.set_volume(VOLUME)
                    DELIVERY_MUSIC.set_volume(VOLUME)

        # 중요한 거
        pygame.display.flip()
    # except: ...

for INTERVAL in INTERVALS:
    INTERVAL.cancel()

pygame.quit()
sys.exit()