import pygame
import math
import random
from threading import Timer
from functools import reduce

# 이미지, 사운드, 맵
from images import SAND_IMAGE, TILE_IMAGE, WALL_IMAGE, PIPE1_IMAGE, PIPE2_IMAGE, PIPE3_IMAGE, DOOR_IMAGE, OPENED_DOOR_IMAGE, DOOR_2_IMAGE, OPENED_DOOR_2_IMAGE, WEB1_IMAGE, WEB2_IMAGE, WALL2_IMAGE, WALL3_IMAGE, WALL4_IMAGE, TERMINAL_IMAGE, TERMINAL_SCREEN_IMAGE, PLAYER_OUTLINE_IMAGE, PLAYER_DETAIL_IMAGE, PLAYER_FRONT_IMAGE, PLAYER_BACK_IMAGE, PLAYER_LEFT_IMAGE, PLAYER_RIGHT_IMAGE, PLAYER_FRONT_WALK_IMAGE, PLAYER_BACK_WALK_IMAGE, PLAYER_LEFT_WALK_IMAGE, PLAYER_RIGHT_WALK_IMAGE, VIGNETTE1_IMAGE, VIGNETTE2_IMAGE, STOP_IMAGE, BOTTLE_IMAGE, KEY_IMAGE, FLASHLIGHT_IMAGE, HOARDING_BUG_IMAGE, BRACKEN_IMAGE, BRACKEN_WALK_IMAGE, COIL_HEAD_IMAGE, HOARDING_BUG_WALK_IMAGE, JESTER_IMAGE, JESTER_DOING_IMAGE, JESTER_WALK_IMAGE, JESTER_OPENED_IMAGE, JESTER_OPENED_WALK_IMAGE
from sounds import MAIN_MUSIC_1, MAIN_MUSIC_2, LOBBY_MUSIC_3, INTRO_MUSIC, METAL_DOOR_SHUT, DOOR_OPENING, NOISE, METAL_WALK_1, METAL_WALK_2, METAL_WALK_3, METAL_WALK_4, GRAB_SHOVEL, GRAB_KEY, GRAB_BOTTLE, GRAB_FLASHLIGHT, DROP_SHOVEL, DROP_KEY, DROP_BOTTLE, DROP_FLASHLIGHT, FLASHLIGHT_CLICK
from maps import ShipArray
from seeds import generate_maze

# 전체적인 설정
CONFIG = {
    'SCREEN_WIDTH': 900, # 너비
    'SCREEN_HEIGHT': 900, # 높이
    'TILE_SIZE': 100, # 타일 사이즈
    'DEBUG': True # 디버그
}

# 초기화
pygame.init()
screen = pygame.display.set_mode((CONFIG['SCREEN_WIDTH'], CONFIG['SCREEN_HEIGHT']))
pygame.display.set_caption('COMPANY')
pygame.display.set_icon(pygame.image.load('./images/icon.ico'))

# 폰트
font = pygame.font.Font('./fonts/Orbit-Regular.ttf', 18)

# 인게임 변수
INGAME = {
    'RUNNING': True, # 실행 상태
    'SPRITES': [], # 사용되는 스프라이트
    'MAPS': [], # 맵들
    'CUR_MAP': '', # 현재 맵
    'NEXT_MAP': '', # 다음으로 착륙할 맵
    'CUR_MOD': 'READY', # READY: 착륙 준비 완료, OK: 착륙 후, FARMING: 미로 맵 입장 후
    'TERMINAL': False, # 터미널 on/off 토글
    'COMMAND': '', # 터미널에 입력한 커맨드
    'HELP': '', # 터미널에 출력되는 문자열
    'STORE': [], # 상점에서 구매한 아이템
    'SCAN': False, # 스캔중 여부
    'TIME': 60 * 8, # 8시부터 시작
    'MONEY': 60 # 현금
}

# 스프라이트 객체
class Sprite(pygame.sprite.Sprite):
    def __init__(self, SPRITE_ID, TYPE, DISPLAY_NAME, FRONT_IMAGE, BACK_IMAGE, LEFT_IMAGE, RIGHT_IMAGE, FRONT_WALK_IMAGE, BACK_WALK_IMAGE, LEFT_WALK_IMAGE, RIGHT_WALK_IMAGE):
        super().__init__()

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
    def move(self, DX, DY):
        self.WALKING = True
        
        OLD_RECT = self.RECT.copy()

        self.RECT.x += DX
        self.RECT.y += DY

        # 충돌
        for Y, ROW in enumerate(CUR_MAP['ARRAY']):
            for X, TILE in enumerate(ROW):
                if CUR_MAP['ID'] == 'ship':
                    if TILE in [SHIP_WALL, SHIP_TERMINAL]:
                        self.crash(X=X, Y=Y, OLD_RECT=OLD_RECT)
                
                elif CUR_MAP['ID'] == 'factory':
                    if TILE == FACTORY_WALL:
                        self.crash(X=X, Y=Y, OLD_RECT=OLD_RECT)
        
        for OBJECT in CUR_MAP['OBJECTS']:
            X = OBJECT.RECT.x / 100
            Y = OBJECT.RECT.y / 100

            if CUR_MAP['ID'] == 'ship':
                if OBJECT.TYPE == 'terminal':
                    self.crash(X=X, Y=Y, OLD_RECT=OLD_RECT)
            
            if CUR_MAP['ID'] == 'factory':
                if OBJECT.TYPE == 'door' and not OBJECT.OPENED:
                    self.crash(X=X, Y=Y, OLD_RECT=OLD_RECT)

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
    def crash(self, X, Y, OLD_RECT):
        WALL_RECT = pygame.Rect(X * CONFIG['TILE_SIZE'], Y * CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE'], CONFIG['TILE_SIZE'])
        if self.RECT.colliderect(WALL_RECT):
            self.RECT = OLD_RECT
            return
    
    # 해당 좌표로 이동
    def teleport(self, X, Y):
        self.RECT.x = X
        self.RECT.y = Y
    
    # 맵 이동
    def map_to(self, FIRST, MAP_ID):
        MAP_REDUCED = Map.reduced(PROPERTY='ID')
        FROM_MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
        TO_MAP_IDX = MAP_REDUCED.index(MAP_ID)

        INGAME['MAPS'][TO_MAP_IDX]['OBJECTS'].append(self)
        
        if not FIRST:
            INGAME['MAPS'][FROM_MAP_IDX]['OBJECTS'].remove(self)
    
    # 아이템 드랍
    def drop_item(self, CUR_ITEM):
        if CUR_ITEM.ID == 'stop': DROP_SHOVEL.play()
        if CUR_ITEM.ID == 'key': DROP_KEY.play()
        if CUR_ITEM.ID == 'bottle': DROP_BOTTLE.play()
        if CUR_ITEM.ID == 'flashlight': DROP_FLASHLIGHT.play()

        CUR_ITEM.RECT.x = self.RECT.x
        CUR_ITEM.RECT.y = self.RECT.y
        CUR_MAP['OBJECTS'].append(CUR_ITEM)
        self.INVENTORY.remove(CUR_ITEM)
    
    # 아이템 수집
    def grab_item(self):
        if self.CONTAIN.ID == 'stop': GRAB_SHOVEL.play()
        if self.CONTAIN.ID == 'key': GRAB_KEY.play()
        if self.CONTAIN.ID == 'bottle': GRAB_BOTTLE.play()
        if self.CONTAIN.ID == 'flashlight': GRAB_FLASHLIGHT.play()

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
    
    # 맵 이름을 리스트로
    @staticmethod
    def reduced(PROPERTY):
        return reduce(lambda acc, cur: acc + [cur[PROPERTY]], INGAME['MAPS'], [])

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

# 타일
SHIP_SAND = 0
SHIP_GRAND = 1
SHIP_WALL = 2
SHIP_TERMINAL = 3

FACTORY_WALL = 1
FACTORY_DOOR = 2
FACTORY_PIPE1 = 3
FACTORY_PIPE2 = 4
FACTORY_PIPE3 = 5
FACTORY_WEB1 = 6
FACTORY_WEB2 = 7

# 함선 맵
Ship = Map(MAP_ID='ship', MAP_DISPLAY_NAME='ship', MAP_ARRAY=ShipArray)
# INGAME['CUR_MAP'] = Ship.MAP_ID

# 공장 맵
maze = generate_maze(41, 41)
FactoryArray = maze

Factory = Map(MAP_ID='factory', MAP_DISPLAY_NAME='factory', MAP_ARRAY=FactoryArray)
INGAME['CUR_MAP'] = Factory.MAP_ID

for IDX in range(0, 100):
    RECT_X = random.randrange(1, 41) * 100
    RECT_Y = random.randrange(1, 41) * 100

    if not Factory.MAP_ARRAY[int(RECT_Y / 100)][int(RECT_X / 100)] == 1:
        Array = [
            { 'ID': 'key', 'IMAGE': KEY_IMAGE }
        ]
        ITEM = Array[random.randrange(len(Array))]

        Item = Sprite(SPRITE_ID=ITEM['ID'], TYPE='item', DISPLAY_NAME=ITEM['ID'], FRONT_IMAGE=ITEM['IMAGE'], BACK_IMAGE=ITEM['IMAGE'], LEFT_IMAGE=ITEM['IMAGE'], RIGHT_IMAGE=ITEM['IMAGE'], FRONT_WALK_IMAGE=ITEM['IMAGE'], BACK_WALK_IMAGE=ITEM['IMAGE'], LEFT_WALK_IMAGE=ITEM['IMAGE'], RIGHT_WALK_IMAGE=ITEM['IMAGE'])
        Item.map_to(FIRST=True, MAP_ID=Factory.MAP_ID)
        Item.teleport(RECT_X, RECT_Y)
        Item.PRICE = random.randrange(3, 70)

for Y, ROW in enumerate(Factory.MAP_ARRAY):
    for X, TILE in enumerate(ROW):
        if TILE == FACTORY_DOOR:
            Factory.MAP_ARRAY[Y][X] = 0

            # 문
            if Factory.MAP_ARRAY[Y][X - 1] == 1 and Factory.MAP_ARRAY[Y][X + 1] == 1: IMAGE = DOOR_IMAGE
            else: IMAGE = DOOR_2_IMAGE
                
            Door = Sprite(SPRITE_ID='door', TYPE='door', DISPLAY_NAME='door', FRONT_IMAGE=IMAGE, BACK_IMAGE=IMAGE, LEFT_IMAGE=IMAGE, RIGHT_IMAGE=IMAGE, FRONT_WALK_IMAGE=IMAGE, BACK_WALK_IMAGE=IMAGE, LEFT_WALK_IMAGE=IMAGE, RIGHT_WALK_IMAGE=IMAGE)
            Door.map_to(FIRST=True, MAP_ID=Factory.MAP_ID)
            Door.teleport(X * 100, Y * 100)
            Door.LOCKED = True if random.randrange(0, 4) == 0 else False

# 플레이어
Player = Sprite(SPRITE_ID='player', TYPE='player', DISPLAY_NAME='player', FRONT_IMAGE=PLAYER_FRONT_IMAGE, BACK_IMAGE=PLAYER_BACK_IMAGE, LEFT_IMAGE=PLAYER_LEFT_IMAGE, RIGHT_IMAGE=PLAYER_RIGHT_IMAGE, FRONT_WALK_IMAGE=PLAYER_FRONT_WALK_IMAGE, BACK_WALK_IMAGE=PLAYER_BACK_WALK_IMAGE, LEFT_WALK_IMAGE=PLAYER_LEFT_WALK_IMAGE, RIGHT_WALK_IMAGE=PLAYER_RIGHT_WALK_IMAGE)
Player.map_to(FIRST=True, MAP_ID=Factory.MAP_ID)
# Player.teleport(300, 300)
Player.teleport(100, 100)
Player.SPEED = 2
if CONFIG['DEBUG']: Player.INVINCIBILITY = True

# 몬스터
HoardingBug = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='hoarding bug', FRONT_IMAGE=HOARDING_BUG_IMAGE, BACK_IMAGE=HOARDING_BUG_IMAGE, LEFT_IMAGE=HOARDING_BUG_IMAGE, RIGHT_IMAGE=HOARDING_BUG_IMAGE, FRONT_WALK_IMAGE=HOARDING_BUG_WALK_IMAGE, BACK_WALK_IMAGE=HOARDING_BUG_WALK_IMAGE, LEFT_WALK_IMAGE=HOARDING_BUG_WALK_IMAGE, RIGHT_WALK_IMAGE=HOARDING_BUG_WALK_IMAGE)
HoardingBug.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
HoardingBug.teleport(500, 400)

CoilHead = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='coil head', FRONT_IMAGE=COIL_HEAD_IMAGE, BACK_IMAGE=COIL_HEAD_IMAGE, LEFT_IMAGE=COIL_HEAD_IMAGE, RIGHT_IMAGE=COIL_HEAD_IMAGE, FRONT_WALK_IMAGE=COIL_HEAD_IMAGE, BACK_WALK_IMAGE=COIL_HEAD_IMAGE, LEFT_WALK_IMAGE=COIL_HEAD_IMAGE, RIGHT_WALK_IMAGE=COIL_HEAD_IMAGE)
CoilHead.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
CoilHead.teleport(600, 400)
CoilHead.INVINCIBILITY = True
CoilHead.DAMAGE = 100

Bracken = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='bracken', FRONT_IMAGE=BRACKEN_IMAGE, BACK_IMAGE=BRACKEN_IMAGE, LEFT_IMAGE=BRACKEN_IMAGE, RIGHT_IMAGE=BRACKEN_IMAGE, FRONT_WALK_IMAGE=BRACKEN_WALK_IMAGE, BACK_WALK_IMAGE=BRACKEN_WALK_IMAGE, LEFT_WALK_IMAGE=BRACKEN_WALK_IMAGE, RIGHT_WALK_IMAGE=BRACKEN_WALK_IMAGE)
Bracken.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Bracken.teleport(700, 400)
CoilHead.DAMAGE = 100

Jester = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='jester', FRONT_IMAGE=JESTER_OPENED_IMAGE, BACK_IMAGE=JESTER_OPENED_IMAGE, LEFT_IMAGE=JESTER_OPENED_IMAGE, RIGHT_IMAGE=JESTER_OPENED_IMAGE, FRONT_WALK_IMAGE=JESTER_OPENED_WALK_IMAGE, BACK_WALK_IMAGE=JESTER_OPENED_WALK_IMAGE, LEFT_WALK_IMAGE=JESTER_OPENED_WALK_IMAGE, RIGHT_WALK_IMAGE=JESTER_OPENED_WALK_IMAGE)
Jester.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Jester.teleport(800, 200)
Jester.INVINCIBILITY = True
Jester.DAMAGE = 100

Jester = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='jester', FRONT_IMAGE=JESTER_DOING_IMAGE, BACK_IMAGE=JESTER_DOING_IMAGE, LEFT_IMAGE=JESTER_DOING_IMAGE, RIGHT_IMAGE=JESTER_DOING_IMAGE, FRONT_WALK_IMAGE=JESTER_DOING_IMAGE, BACK_WALK_IMAGE=JESTER_DOING_IMAGE, LEFT_WALK_IMAGE=JESTER_DOING_IMAGE, RIGHT_WALK_IMAGE=JESTER_DOING_IMAGE)
Jester.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Jester.teleport(800, 300)
Jester.INVINCIBILITY = True
Jester.DAMAGE = 100

Jester = Sprite(SPRITE_ID='monster', TYPE='monster', DISPLAY_NAME='jester', FRONT_IMAGE=JESTER_IMAGE, BACK_IMAGE=JESTER_IMAGE, LEFT_IMAGE=JESTER_IMAGE, RIGHT_IMAGE=JESTER_IMAGE, FRONT_WALK_IMAGE=JESTER_WALK_IMAGE, BACK_WALK_IMAGE=JESTER_WALK_IMAGE, LEFT_WALK_IMAGE=JESTER_WALK_IMAGE, RIGHT_WALK_IMAGE=JESTER_WALK_IMAGE)
Jester.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Jester.teleport(800, 400)
Jester.INVINCIBILITY = True
Jester.DAMAGE = 100

# 아이템
Flashlight = Sprite(SPRITE_ID='flashlight', TYPE='item', DISPLAY_NAME='flashlight', FRONT_IMAGE=FLASHLIGHT_IMAGE, BACK_IMAGE=FLASHLIGHT_IMAGE, LEFT_IMAGE=FLASHLIGHT_IMAGE, RIGHT_IMAGE=FLASHLIGHT_IMAGE, FRONT_WALK_IMAGE=FLASHLIGHT_IMAGE, BACK_WALK_IMAGE=FLASHLIGHT_IMAGE, LEFT_WALK_IMAGE=FLASHLIGHT_IMAGE, RIGHT_WALK_IMAGE=FLASHLIGHT_IMAGE)
Flashlight.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Flashlight.teleport(300, 400)
Stop = Sprite(SPRITE_ID='stop', TYPE='item', DISPLAY_NAME='stop', FRONT_IMAGE=STOP_IMAGE, BACK_IMAGE=STOP_IMAGE, LEFT_IMAGE=STOP_IMAGE, RIGHT_IMAGE=STOP_IMAGE, FRONT_WALK_IMAGE=STOP_IMAGE, BACK_WALK_IMAGE=STOP_IMAGE, LEFT_WALK_IMAGE=STOP_IMAGE, RIGHT_WALK_IMAGE=STOP_IMAGE)
Stop.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Stop.teleport(300, 400)
Stop.PRICE = 7
Key = Sprite(SPRITE_ID='key', TYPE='item', DISPLAY_NAME='key', FRONT_IMAGE=KEY_IMAGE, BACK_IMAGE=KEY_IMAGE, LEFT_IMAGE=KEY_IMAGE, RIGHT_IMAGE=KEY_IMAGE, FRONT_WALK_IMAGE=KEY_IMAGE, BACK_WALK_IMAGE=KEY_IMAGE, LEFT_WALK_IMAGE=KEY_IMAGE, RIGHT_WALK_IMAGE=KEY_IMAGE)
Key.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Key.teleport(300, 400)
Key.PRICE = 3

# 터미널
Terminal = Sprite(SPRITE_ID='terminal', TYPE='terminal', DISPLAY_NAME='terminal', FRONT_IMAGE=TERMINAL_IMAGE, BACK_IMAGE=TERMINAL_IMAGE, LEFT_IMAGE=TERMINAL_IMAGE, RIGHT_IMAGE=TERMINAL_IMAGE, FRONT_WALK_IMAGE=TERMINAL_IMAGE, BACK_WALK_IMAGE=TERMINAL_IMAGE, LEFT_WALK_IMAGE=TERMINAL_IMAGE, RIGHT_WALK_IMAGE=TERMINAL_IMAGE)
Terminal.map_to(FIRST=True, MAP_ID=Ship.MAP_ID)
Terminal.teleport(200, 100)

# 착륙 사운드 재생
# DOOR_OPENING.play()
# NOISE.play()

# 메인 음악 재생
# def main_music():
#     if random.randrange(1, 3) == 1: MAIN_MUSIC_1.play()
#     else: MAIN_MUSIC_2.play()

# timer = Timer(10, main_music)
# timer.start()

# 공장 로비 사운드 재생
# LOBBY_MUSIC_3.play(loops=-1)
# METAL_DOOR_SHUT.play()

# 인트로 사운드 재생
# def intro_music():
#     INTRO_MUSIC.play()

# timer = Timer(2, intro_music)
# timer.start()

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

# 시간
def increase_time():
    INGAME['TIME'] += 4

def start_increase():
    set_interval(increase_time, 3)

timer = Timer(3, start_increase)
timer.start()

# 현재 맵
MAP_REDUCED = Map.reduced(PROPERTY='ID')
MAP_IDX = MAP_REDUCED.index(INGAME['CUR_MAP'])
CUR_MAP = INGAME['MAPS'][MAP_IDX]

while INGAME['RUNNING']:
    # try:
        if CONFIG['DEBUG']: screen.fill((0, 0, 255))
        else: screen.fill((0, 0, 0))
        
        keys = pygame.key.get_pressed()

        CUR_ITEM_EXISTS = len(Player.INVENTORY) >= Player.CUR_ITEM_IDX + 1

        # 이벤트
        for event in pygame.event.get():
            # 종료
            if event.type == pygame.QUIT:
                INGAME['RUNNING'] = False

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
                                INGAME['MONEY'] -= 25 if INGAME['COMMAND'] == 'flashlight' else 30
                                INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}

                                {INGAME['COMMAND']} 1개를 주문했습니다.'''
                                INGAME['STORE'].append(INGAME['COMMAND'])
                            elif INGAME['COMMAND'] in ['experimentation', 'company']:
                                INGAME['HELP'] = f'''현금: ${INGAME['MONEY']}
                                
                                {INGAME['COMMAND']} 으로 함선이 이동했습니다.'''
                                INGAME['NEXT_MAP'] = INGAME['COMMAND']
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
                                주문을 완료하면 하늘에서 배달이 옵니다.'''
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

                                                if len(Player.INVENTORY) == 0:
                                                    CUR_ITEM_EXISTS = False

                                    # 잠겨있지 않다면
                                    else:
                                        DOOR.OPENED = True

                                        IMAGE = OPENED_DOOR_IMAGE
                                        if DOOR.FRONT_IMAGE == DOOR_2_IMAGE: IMAGE = OPENED_DOOR_2_IMAGE
                                        DOOR.CUR_IMAGE = IMAGE
                            
                            # 아이템 수집
                            else:
                                Player.grab_item()

                        # g키 버리기
                        if event.key == pygame.K_g and len(Player.INVENTORY) > 0:
                            if CUR_ITEM_EXISTS:
                                CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]

                                if CUR_ITEM:
                                    Player.drop_item(CUR_ITEM=CUR_ITEM)

                                    if len(Player.INVENTORY) == 0:
                                        CUR_ITEM_EXISTS = False
                        
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
                            timer = Timer(2, scan_false)
                            timer.start()

                        # 아이템 선택
                        if event.key == pygame.K_1: Player.CUR_ITEM_IDX = 0
                        elif event.key == pygame.K_2: Player.CUR_ITEM_IDX = 1
                        elif event.key == pygame.K_3: Player.CUR_ITEM_IDX = 2
                        elif event.key == pygame.K_4: Player.CUR_ITEM_IDX = 3

        # 터미널이 안열려있으면
        if not INGAME['TERMINAL']:
            # 카메라 시점 계산
            offset_x = CONFIG['SCREEN_WIDTH'] // 2 - Player.RECT.centerx
            offset_y = CONFIG['SCREEN_HEIGHT'] // 2 - Player.RECT.centery

            # 타일 그리기
            for Y, ROW in enumerate(CUR_MAP['ARRAY']):
                for X, TILE in enumerate(ROW):
                    RECT = (X * CONFIG['TILE_SIZE'] + offset_x, Y * CONFIG['TILE_SIZE'] + offset_y)

                    if CUR_MAP['ID'] == 'ship':
                        SAND_IMAGE.render(screen, RECT)
                        if TILE == SHIP_GRAND: TILE_IMAGE.render(screen, RECT)
                        elif TILE == SHIP_WALL: WALL_IMAGE.render(screen, RECT)
                        elif TILE == SHIP_TERMINAL: TERMINAL_IMAGE.render(screen, RECT)
                    
                    if CUR_MAP['ID'] == 'factory':
                        TILE_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_WALL: WALL_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_DOOR: DOOR_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_PIPE1: PIPE1_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_PIPE2: PIPE2_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_PIPE3: PIPE3_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_WEB1: WEB1_IMAGE.render(screen, RECT)
                        if TILE == FACTORY_WEB2: WEB2_IMAGE.render(screen, RECT)

            # 현재 맵에 존재하는 오브젝트
            for OBJECT in CUR_MAP['OBJECTS']:
                # 카메라 시점에 대한 오브젝트 위치
                OBJECT_RECT = OBJECT.RECT.move(offset_x, offset_y)

                # 플레이어라면
                if OBJECT.TYPE == 'player':
                    # 플레이어 이동
                    if not Player.DIED:
                        if keys[pygame.K_w]: Player.move(0, -Player.SPEED)
                        if keys[pygame.K_s]: Player.move(0, Player.SPEED)
                        if keys[pygame.K_a]: Player.move(-Player.SPEED, 0)
                        if keys[pygame.K_d]: Player.move(Player.SPEED, 0)

                    if CONFIG['DEBUG']: pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], Player.ATTACK_DISTANCE, 1)
                    
                    # 현재 맵에 존재하는 오브젝트
                    for ITEM in CUR_MAP['OBJECTS']:
                        # 플레이어 원형 경계
                        dist = distance(OBJECT.RECT, ITEM.RECT)

                        if dist < Player.ATTACK_DISTANCE:
                            # 단축키 + 메시지 표시
                            if ITEM.TYPE == 'item':
                                shortcut = '(E)'

                                if len(OBJECT.INVENTORY) == 4: shortcut = '(FULL)'
                                else: OBJECT.CONTAIN = ITEM

                                text = font.render(shortcut + f' {ITEM.DISPLAY_NAME}', True, (255, 255, 255))
                                screen.blit(text, (OBJECT_RECT.x, OBJECT_RECT.y - 30))
                                
                                break
                            elif ITEM.TYPE == 'terminal':
                                OBJECT.CONTAIN = ITEM

                                text = font.render(f'(E) Use {ITEM.DISPLAY_NAME}', True, (255, 255, 255))
                                screen.blit(text, (OBJECT_RECT.x, OBJECT_RECT.y - 30))
                                
                                break
                            elif ITEM.TYPE == 'door':
                                OBJECT.CONTAIN = ITEM

                                shortcut = '(E)'
                                if ITEM.LOCKED == True: shortcut = '(잠김)'

                                message = ' 문 열기'
                                if ITEM.OPENED == True: message = ' 문 닫기'
                                
                                text = font.render(shortcut + message, True, (255, 255, 255))
                                screen.blit(text, (OBJECT_RECT.x, OBJECT_RECT.y - 30))
                                
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
                        pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], 500, 1)
                        pygame.draw.circle(screen, (255, 0, 0), [OBJECT_RECT.x + 45, OBJECT_RECT.y + 45], 100, 1)
                    
                    dist = distance(OBJECT.RECT, Player.RECT)
                    
                    if dist < OBJECT.DISTANCE and not CONFIG['DEBUG']:
                        if Player.RECT.x > OBJECT.RECT.x: OBJECT.move(OBJECT.SPEED, 0)
                        if Player.RECT.x < OBJECT.RECT.x: OBJECT.move(-OBJECT.SPEED, 0)
                        if Player.RECT.y > OBJECT.RECT.y: OBJECT.move(0, OBJECT.SPEED)
                        if Player.RECT.y < OBJECT.RECT.y: OBJECT.move(0, -OBJECT.SPEED)
                    else: OBJECT.WALKING = False

                    if dist < OBJECT.ATTACK_DISTANCE:
                        Player.DECREASING = True
                        Player.DECREASING_SIZE = OBJECT.DAMAGE
                        
                        if Player.HP < 0:
                            Player.DIED = True
                            
                            for CUR_ITEM_IDX, CUR_ITEM in enumerate(Player.INVENTORY):
                                Player.drop_item(CUR_ITEM=CUR_ITEM)
                            
                            CUR_ITEM_EXISTS = False
                    else: Player.DECREASING = False
                
                # 오브젝트 이미지 그리기
                dist = distance(Player.RECT, OBJECT.RECT)

                if dist < 400:
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
                dist = distance(Player.RECT, OBJECT.RECT)

                if INGAME['SCAN'] and dist < Player.DISTANCE:
                    pygame.draw.circle(screen, (0, 255, 0), [OBJECT_RECT.x + 50, OBJECT_RECT.y + 50], 75, 1)
                    pygame.draw.circle(screen, (0, 255, 0), [OBJECT_RECT.x + 50, OBJECT_RECT.y + 50], 85, 1)
                    pygame.draw.circle(screen, (0, 255, 0), [OBJECT_RECT.x + 50, OBJECT_RECT.y + 50], 130, 1)
                    pygame.draw.rect(screen, (0, 255, 0), [OBJECT_RECT.x + 125, OBJECT_RECT.y - 50, 200, 100])

                    # 정보
                    text = font.render(OBJECT.DISPLAY_NAME, True, (0, 0, 0))
                    screen.blit(text, (OBJECT_RECT.x + 150, OBJECT_RECT.y - 25))
                    text = font.render(f'${str(OBJECT.PRICE)}', True, (0, 0, 0))
                    screen.blit(text, (OBJECT_RECT.x + 150, OBJECT_RECT.y))

                    # 합계
                    SUM = reduce(lambda acc, cur: acc + cur.PRICE, CUR_MAP['OBJECTS'], 0)
                    text = font.render(f'합계: ${str(SUM)}', True, (255, 255, 255))
                    screen.blit(text, (50, 75))

        # 플레이어가 들고 있는 아이템 표시
        if CUR_ITEM_EXISTS:
            CUR_ITEM = Player.INVENTORY[Player.CUR_ITEM_IDX]
            CUR_ITEM.CUR_IMAGE.render(screen, (430, 420))

        # 손전등 비네트 효과
        INVENTORY = reduce(lambda acc, cur: acc + [cur.DISPLAY_NAME], Player.INVENTORY, [])
        if not Player.DIED and not CONFIG['DEBUG']:
            if Player.FLASHLIGHT and 'flashlight' in INVENTORY: VIGNETTE1_IMAGE.render(screen, (0, 0))
            else: VIGNETTE2_IMAGE.render(screen, (0, 0))

        # 인벤토리 아이템 표시
        for IDX, ITEM in enumerate(Player.INVENTORY):
            if ITEM:
                if Player.CUR_ITEM_IDX == IDX: RGB = (255, 255, 255)
                else: RGB = (0, 0, 0)

                ITEM.CUR_IMAGE.render(screen, (50 + IDX * 150, CONFIG['SCREEN_HEIGHT'] - 150))

            pygame.draw.rect(screen, RGB, (50 + IDX * 150, CONFIG['SCREEN_HEIGHT'] - 150, 100, 100), 2)

        # 시간
        HOURS = int(INGAME['TIME'] / 60)
        MINUTES = int(INGAME['TIME'] % 60)
        APM = '오전' if HOURS < 12 else '오후'
        DISPLAY_HOURS = f'0{str(HOURS)}' if HOURS < 10 else str(HOURS)
        DISPLAY_MINUTES = f'0{str(MINUTES)}' if MINUTES < 10 else str(MINUTES)
        text = font.render(f'{APM} {str(DISPLAY_HOURS)}:{str(DISPLAY_MINUTES)}', True, (255, 255, 255))
        screen.blit(text, (50, 50))

        # 플레이어 상세
        PLAYER_OUTLINE_IMAGE.render(screen, (50, 100))
        PLAYER_DETAIL_IMAGE.render(screen, (90, 130))

        # 터미널이 열려있다면
        if INGAME['TERMINAL']:
            TERMINAL_SCREEN_IMAGE.render(screen, (0, 0))

            # 한 줄 마다 나눠서 그리기
            for IDX, LINE in enumerate(INGAME['HELP'].split('\n')):
                text = font.render(LINE.strip(), True, (0, 255, 0))
                screen.blit(text, (200, 200 + IDX * 30))
            
            text = font.render(f'> {INGAME['COMMAND']}', True, (0, 255, 0))
            screen.blit(text, (200, 700))

        # 중요한 거
        pygame.display.flip()
    # except: print('Error')