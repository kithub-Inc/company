import pygame

pygame.init()

SOUNDS = []

class Sound:
    def __init__(self, PATH):
        self.PATH = PATH
        self.SOUND = pygame.mixer.Sound(self.PATH)
        SOUNDS.append(self.SOUND)
    
    def play(self, LOOPS=0):
        self.SOUND.play(LOOPS)
    
    def stop(self):
        self.SOUND.stop()
    
    def set_volume(self, VOLUME):
        self.SOUND.set_volume(VOLUME)

SAVE_ITEM_SFX = Sound('sounds/Lethal sounds/Sound ship/CollectScrapSmall-sharedassets3.assets-1124.wav')

MAIN_MUSIC_1 = Sound('sounds/013. Ambient Music1.mp3')
MAIN_MUSIC_2 = Sound('sounds/014. Ambient Music2.mp3')
LOBBY_MUSIC_3 = Sound('sounds/088. Breaker Box Hum.mp3')

INTRO_MUSIC = Sound('sounds/427. Intro Company Speech.mp3')
MENU_MUSIC = Sound('sounds/512. Menu1.mp3')

DELIVERY_MUSIC = Sound('sounds/Voicy_Lethal Company Ice Cream Truck Theme.mp3')
DELIVERY_DROP_ITEM = Sound('sounds/Lethal sounds/Sound icecream/ItemDropshipLand.ogg')
DELIVERY_COME = Sound('sounds/Lethal sounds/Sound icecream/ShipThrusterClose.ogg')

DOOR_OPENING = Sound('sounds/389. Hangar Door Opening.mp3')

METAL_DOOR_SHUT = Sound('sounds/514. Metal Door Shut1 1.mp3')
METAL_DOOR_CLOSE = Sound('sounds/517. Metal Hatch Close.mp3')
NOISE = Sound('sounds/673. Ship Thruster Ambiance.mp3')
NOISE_2 = Sound('sounds/399. High Wind.mp3')

METAL_WALK_1 = Sound('sounds/523. Metal Walk.mp3')
METAL_WALK_2 = Sound('sounds/524. Metal Walk2.mp3')
METAL_WALK_3 = Sound('sounds/525. Metal Walk3.mp3')
METAL_WALK_4 = Sound('sounds/526. Metal Walk4.mp3')
CONCRETE_WALK_1 = Sound('sounds/Lethal sounds/Sound steps/Concrete1.wav')
CONCRETE_WALK_2 = Sound('sounds/Lethal sounds/Sound steps/Concrete2.wav')
CONCRETE_WALK_3 = Sound('sounds/Lethal sounds/Sound steps/Concrete3.wav')
CONCRETE_WALK_4 = Sound('sounds/Lethal sounds/Sound steps/Concrete4.wav')
SNOW_WALK_1 = Sound('sounds/Lethal sounds/Sound steps/Snow1-sharedassets3.assets-1007.wav')
SNOW_WALK_2 = Sound('sounds/Lethal sounds/Sound steps/Snow2-sharedassets3.assets-1091.wav')
SNOW_WALK_3 = Sound('sounds/Lethal sounds/Sound steps/Snow3-sharedassets3.assets-1021.wav')
SNOW_WALK_4 = Sound('sounds/Lethal sounds/Sound steps/Snow4-sharedassets3.assets-1123.wav')

GRAB_SHOVEL = Sound('sounds/367. Grab Shovel.mp3')
GRAB_KEY = Sound('sounds/363. Grab Key.mp3')
GRAB_BOTTLE = Sound('sounds/359. Grab Bottle.mp3')
GRAB_FLASHLIGHT = Sound('sounds/362. Grab Flashlight.mp3')
GRAB_DEFAULT_ITEM = Sound('sounds/360. Grab Cardboard Box.mp3')

DROP_SHOVEL = Sound('sounds/278. Drop Shovel.mp3')
DROP_KEY = Sound('sounds/267. Drop Key.mp3')
DROP_BOTTLE = Sound('sounds/258. Drop Bottle Single.mp3')
DROP_FLASHLIGHT = Sound('sounds/262. Drop Flashlight.mp3')
DROP_PLASTIC = Sound('sounds/Lethal sounds/Sound Drop Items/DropPlastic2-sharedassets1.assets-861.wav')
DROP_METAL = Sound('sounds/Lethal sounds/Sound Drop Items/DropMetalObject1-sharedassets1.assets-1097.wav')
DROP_DUCK = Sound('sounds/Lethal sounds/Sound Drop Items/DropRubberDuck-sharedassets1.assets-926.wav')
DROP_GLASS = Sound('sounds/Lethal sounds/Sound Drop Items/DropGlass1-sharedassets1.assets-1051.wav')
DROP_THIN_METAL = Sound('sounds/Lethal sounds/Sound Drop Items/DropThinMetal-sharedassets1.assets-1082.wav')
DROP_CAN = Sound('sounds/Lethal sounds/Sound Drop Items/DropCan-sharedassets1.assets-927.wav')
DROP_BELL = Sound('sounds/Lethal sounds/Sound Drop Items/DropBell-sharedassets1.assets-942.wav')

FLASHLIGHT_CLICK = Sound('sounds/317. Flashlight Click.mp3')

MASK_WALK_1 = Sound('sounds/Lethal sounds/Sound steps/Concrete1.wav')
MASK_WALK_2 = Sound('sounds/Lethal sounds/Sound steps/Concrete2.wav')
MASK_WALK_3 = Sound('sounds/Lethal sounds/Sound steps/Concrete3.wav')
MASK_WALK_4 = Sound('sounds/Lethal sounds/Sound steps/Concrete4.wav')

BRACKEN_ATTACK = Sound('sounds/Lethal sounds/Creatures/Sound bracken/CrackNeck.ogg')
BRACKEN_ANGRY = Sound('sounds/Lethal sounds/Creatures/Sound bracken/Angered.ogg')

JESTER_DOING = Sound('sounds/430. Jack In The Box Theme.mp3')
JESTER_SCREAM = Sound('sounds/649. Scream1.mp3')
JESTER_WALK_1 = Sound('sounds/Lethal sounds/Creatures/Sound jester/JesterStomp1.mp3')
JESTER_WALK_2 = Sound('sounds/Lethal sounds/Creatures/Sound jester/JesterStomp2.mp3')
JESTER_WALK_3 = Sound('sounds/Lethal sounds/Creatures/Sound jester/JesterStomp3.mp3')
JESTER_DOING_CRANK_1 = Sound('sounds/Lethal sounds/Creatures/Sound jester/TurnCrank1.mp3')
JESTER_DOING_CRANK_2 = Sound('sounds/Lethal sounds/Creatures/Sound jester/TurnCrank2.mp3')
JESTER_DOING_CRANK_3 = Sound('sounds/Lethal sounds/Creatures/Sound jester/TurnCrank3.mp3')
JESTER_POP = Sound('sounds/Lethal sounds/Creatures/Sound jester/Pop1.mp3')

COILHEAD_WALK_1 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/BareFootstep1.mp3')
COILHEAD_WALK_2 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/BareFootstep2.mp3')
COILHEAD_WALK_3 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/BareFootstep3.mp3')
COILHEAD_WALK_4 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/BareFootstep4.mp3')
COILHEAD_ATTACK_1 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/Spring1.mp3')
COILHEAD_ATTACK_2 = Sound('sounds/Lethal sounds/Creatures/Sound springhead/Spring2.mp3')

HOARDING_BUG_WALK_1 = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/BugWalk1.mp3')
HOARDING_BUG_WALK_2 = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/BugWalk2.mp3')
HOARDING_BUG_WALK_3 = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/BugWalk3.mp3')
HOARDING_BUG_WALK_4 = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/BugWalk4.mp3')
HOARDING_BUG_FLY = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/Fly.mp3')
HOARDING_BUG_ANGRY = Sound('sounds/Lethal sounds/Creatures/Sound lootbug/AngryScreech.mp3')

GIRL_LAUGH_1 = Sound('sounds/Lethal sounds/Creatures/Sound girl/Laugh1.ogg')
GIRL_LAUGH_2 = Sound('sounds/Lethal sounds/Creatures/Sound girl/Laugh2.ogg')
GIRL_BREATH_1 = Sound('sounds/Lethal sounds/Creatures/Sound girl/Breath2.ogg')
GIRL_BREATH_2 = Sound('sounds/Lethal sounds/Creatures/Sound girl/Breath3.ogg')
GIRL_WALK_1 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk1.ogg')
GIRL_WALK_2 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk2.ogg')
GIRL_WALK_3 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk3.ogg')
GIRL_WALK_4 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk4.ogg')
GIRL_WALK_5 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk5.ogg')
GIRL_WALK_6 = Sound('sounds/Lethal sounds/Creatures/Sound girl/SkipWalk6.ogg')

MINE_BEEP = Sound('sounds/Lethal sounds/Sound mine/MineBeep.mp3')
MINE_PRESS = Sound('sounds/Lethal sounds/Sound mine/PressLandmine.mp3')
MINE_TRIGGER = Sound('sounds/Lethal sounds/Sound mine/MineTrigger.mp3')
MINE_FIRE = Sound('sounds/Lethal sounds/Sound mine/MineDetonate.mp3')

SUCKED_INTO_SPACE = Sound('sounds/Lethal sounds/Sound Ship/SuckedIntoSpace-sharedassets3.assets-1249.wav')
SHIP_FLY_TO_PLANET = Sound('sounds/667. Ship Fly To Planet.mp3')
SHIP_ARRIVE_AT_PLANET = Sound('sounds/Lethal sounds/Sound Ship/ShipArriveAtPlanet-sharedassets3.assets-1031.wav')
CHARGE_ITEM = Sound('sounds/Lethal sounds/Sound Ship/ChargeItem-sharedassets3.assets-1141.wav')
SAVE_ITEM = Sound('sounds/Lethal sounds/Sound Ship/CollectScrapSmall-sharedassets3.assets-1124.wav')
ITEM_PRICE = Sound('sounds/Lethal sounds/Sound Ship/CounterAdd-sharedassets3.assets-1193.wav')
WARNING = Sound('sounds/Lethal sounds/Sound Ship/DeadlineAlarm-sharedassets3.assets-1061.wav')
FIRED_VOICE = Sound('sounds/Lethal sounds/Sound Ship/FiredVoiceline-sharedassets3.assets-1246.wav')
SHIP_LIGHT_SQUEAK = Sound('sounds/Lethal sounds/Sound Ship/ShipAmbianceLightSqueak-sharedassets3.assets-1100.wav')
ENTER_TERMINAL = Sound('sounds/Lethal sounds/Sound ship/EnterTerminal-sharedassets3.assets-1053.wav')
EXIT_TERMINAL = Sound('sounds/Lethal sounds/Sound ship/ExitTerminal-sharedassets3.assets-1137.wav')
PURCHASE_ITEM = Sound('sounds/Lethal sounds/Sound ship/PurchaseSFX-sharedassets3.assets-1229.wav')
TERMINAL_ERROR = Sound('sounds/Lethal sounds/Sound ship/TerminalTypoError-sharedassets3.assets-1179.wav')
KEY_1 = Sound('sounds/443. Key1.mp3')
KEY_2 = Sound('sounds/444. Key2.mp3')
KEY_3 = Sound('sounds/445. Key3.mp3')
KEY_4 = Sound('sounds/446. Key4.mp3')
KEY_5 = Sound('sounds/447. Key5.mp3')
KEY_6 = Sound('sounds/448. Key6.mp3')
KEY_7 = Sound('sounds/449. Key7.mp3')
KEY_8 = Sound('sounds/450. Key8.mp3')

HOVER_BUTTON = Sound('sounds/415. Hover Button1.mp3')
CLICK_BUTTON = Sound('sounds/145. Button Press1-1.mp3')

HIT_READY = Sound('sounds/694. Shovel Reel Up.mp3')
HIT_DEFAULT_1 = Sound('sounds/691. Shovel Hit Default.mp3')
HIT_DEFAULT_2 = Sound('sounds/692. Shovel Hit Default2.mp3')

SCAN = Sound('sounds/648. Scan.mp3')

REACHED_QUOTA = Sound('sounds/614. Reached Quota S F X.mp3')
INCREASE_QUOTA = Sound('sounds/Lethal sounds/Sound ship/NewProfitQuota-sharedassets3.assets-1110.wav')
DECREASE_DAY = Sound('sounds/307. Final Day Before Deadline.mp3')

DOOR_OPEN_1 = Sound('sounds/Lethal sounds/Sound door/DoorOpen1-sharedassets1.assets-813.wav')
DOOR_OPEN_2 = Sound('sounds/Lethal sounds/Sound door/DoorOpen2-sharedassets1.assets-924.wav')
DOOR_CLOSE_1 = Sound('sounds/Lethal sounds/Sound door/DoorClose1-sharedassets1.assets-824.wav')
DOOR_CLOSE_2 = Sound('sounds/Lethal sounds/Sound door/DoorClose2-sharedassets1.assets-877.wav')

HIGH_ACTION_1 = Sound('sounds/Lethal sounds/Sound ambient/HighAction1.ogg')
HIGH_ACTION_2 = Sound('sounds/Lethal sounds/Sound ambient/HighAction2.ogg')