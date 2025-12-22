import config
from player import Player
from camera import Camera

# 게임 상태 상수
GAME_STATE_MENU = "MENU"
GAME_STATE_PLAYING = "PLAYING"
GAME_STATE_RANKING = "RANKING"
GAME_STATE_INVENTORY = "INVENTORY"

# 전역 엔티티 리스트
player = None
camera_obj = None
slimes = []
daggers = []
exp_orbs = []
bats = []
slime_bullets = []
boss_slimes = []
storm_projectiles = []

# 게임 정보 및 타이머
game_state = GAME_STATE_MENU
current_slime_max_hp = config.SLIME_INITIAL_BASE_HP
slime_spawn_timer = 0
slime_hp_increase_timer = 0
boss_active = False
is_game_over_for_menu = False
is_name_entered = False
input_box = None

# 랭킹 관련
online_rankings = None
current_rank_category_index = 0
RANK_CATEGORIES = ["DifficultyScore", "Levels", "Kills", "Bosses", "SurvivalTime"]

def get_entities_dict():
    """모든 엔티티 리스트를 딕셔너리로 반환 (충돌 로직 등에 사용)"""
    return {
        'slimes': slimes,
        'daggers': daggers,
        'exp_orbs': exp_orbs,
        'bats': bats,
        'slime_bullets': slime_bullets,
        'boss_slimes': boss_slimes,
        'storm_projectiles': storm_projectiles
    }

def reset_game_state():
    """게임 상태를 초기화합니다."""
    global player, camera_obj, slimes, daggers, exp_orbs, bats, slime_bullets, boss_slimes, storm_projectiles
    global slime_spawn_timer, current_slime_max_hp, slime_hp_increase_timer
    global boss_active, is_game_over_for_menu, is_name_entered, online_rankings

    # 1. 닉네임 결정
    player_name_to_use = input_box.text if input_box and input_box.text else "익명 개발자"
    
    # 2. 핵심 객체 생성
    player = Player(config.MAP_WIDTH/2, config.MAP_HEIGHT/2, player_name_to_use)
    camera_obj = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    # 3. 리스트 비우기
    slimes.clear(); daggers.clear(); exp_orbs.clear(); bats.clear()
    slime_bullets.clear(); boss_slimes.clear(); storm_projectiles.clear()
    
    # 4. 값 초기화
    slime_spawn_timer = 0
    current_slime_max_hp = config.SLIME_INITIAL_BASE_HP
    slime_hp_increase_timer = 0
    boss_active = False
    is_game_over_for_menu = False
    
    # 5. 입력창 초기화 (선택 사항)
    if input_box:
        input_box.text = ""
        is_name_entered = False
    
    online_rankings = None