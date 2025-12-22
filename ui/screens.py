import pygame
import config
from ui.fonts import font, small_font, medium_font, large_font 

CATEGORY_INFO = [
    {"name": "난이도 배율", "key": "DifficultyScore"},
    {"name": "최고 레벨", "key": "Levels"},
    {"name": "총 킬 수", "key": "Kills"},
    {"name": "보스 처치", "key": "Bosses"},
    {"name": "생존 시간", "key": "SurvivalTime"}
]
RANKING_BUTTONS = []

def setup_ranking_buttons():
    global RANKING_BUTTONS
    RANKING_BUTTONS.clear()
    total_w = len(CATEGORY_INFO) * 160
    start_x = (config.SCREEN_WIDTH - total_w) // 2 
    for i, info in enumerate(CATEGORY_INFO):
        rect = pygame.Rect(start_x + i * 160, config.SCREEN_HEIGHT - 60, 150, 40)
        RANKING_BUTTONS.append({"rect": rect, "key": info['key'], "name": info['name']})

def draw_main_menu(surface, start_rect, exit_rect, is_game_over, rank_rect):
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    txt = "게임 오버" if is_game_over else "뱀파이어 서바이벌"
    color = config.RED if is_game_over else config.BLUE
    title = large_font.render(txt, True, color)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH//2, 200)))

    for r, t in [(start_rect, "게임 시작"), (rank_rect, "랭킹 보기")]:
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, r, border_radius=15)
        st_txt = medium_font.render(t, True, config.WHITE)
        surface.blit(st_txt, st_txt.get_rect(center=r.center))

def draw_ranking_screen(surface, rankings, current_key):
    surface.fill(config.DARK_GREEN)
    title = large_font.render("온라인 랭킹", True, config.WHITE)
    surface.blit(title, (50, 30))
    
    # 랭킹 데이터 그리기 로직 (기존과 동일)
    # ... (생략하지만 기존 utils 데이터 활용하여 루프 돌리는 부분 포함)
    for btn in RANKING_BUTTONS:
        color = config.RED if btn['key'] == current_key else config.UI_OPTION_BOX_BG_COLOR
        pygame.draw.rect(surface, color, btn['rect'], border_radius=5)
        b_txt = small_font.render(btn['name'], True, config.WHITE)
        surface.blit(b_txt, b_txt.get_rect(center=btn['rect'].center))


def draw_weapon_inventory(surface, player_obj):
    # 1. 배경 어둡게 (반투명)
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200)) 
    surface.blit(overlay, (0, 0))

    # 2. 제목
    title = large_font.render("INVENTORY", True, config.YELLOW)
    surface.blit(title, title.get_rect(center=(config.SCREEN_WIDTH // 2, 70)))
    
    instr = small_font.render("M: 돌아가기 / 무기를 클릭해 상세 정보 확인", True, config.WHITE)
    surface.blit(instr, instr.get_rect(center=(config.SCREEN_WIDTH // 2, 120)))

    # 3. 무기 카드 배치 (한 줄에 5개씩 2줄 = 최대 10개)
    card_w, card_h = 140, 100
    start_x = (config.SCREEN_WIDTH - (5 * card_w + 4 * 10)) // 2
    start_y = 180

    for i, wpn in enumerate(player_obj.active_weapons):
        row = i // 5
        col = i % 5
        rect = pygame.Rect(start_x + col * (card_w + 10), start_y + row * (card_h + 10), card_w, card_h)
        
        # 카드 테두리 및 배경
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, rect, border_radius=10)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BORDER_COLOR, rect, 2, border_radius=10)
        
        # 무기 이름과 레벨만 간단히 표시
        name_s = small_font.render(wpn.name, True, config.WHITE)
        lvl_s = small_font.render(f"Lv.{wpn.level}", True, config.YELLOW)
        surface.blit(name_s, name_s.get_rect(center=(rect.centerx, rect.y + 30)))
        surface.blit(lvl_s, lvl_s.get_rect(center=(rect.centerx, rect.y + 65)))