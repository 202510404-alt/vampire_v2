import pygame
import config
from ui.fonts import font, small_font, medium_font, large_font

def draw_game_ui(surface, player_obj, game_entities, current_slime_max_hp_val, boss_defeat_count_val, slime_kill_count_val, boss_spawn_threshold_val):
    """게임 플레이 중의 UI를 그립니다. (숫자 표시 복구 완료)"""
    
    # 1. 닉네임 표시 (우측 상단)
    name_text = font.render(f"ID: {player_obj.name}", True, config.WHITE)
    surface.blit(name_text, (config.SCREEN_WIDTH - name_text.get_width() - 10, 10))

    # 2. HP 게이지 바 및 숫자 (좌측 상단)
    hp_x, hp_y, hp_w, hp_h = 10, 10, 150, 20
    hp_ratio = player_obj.hp / player_obj.max_hp if player_obj.max_hp > 0 else 0
    
    # 바 배경 및 채우기
    pygame.draw.rect(surface, config.DARK_RED, (hp_x, hp_y, hp_w, hp_h), border_radius=3) 
    if hp_ratio > 0:
        pygame.draw.rect(surface, config.HP_BAR_GREEN, (hp_x, hp_y, int(hp_w * hp_ratio), hp_h), border_radius=3)
    
    # 🚩 HP 숫자 표시 복구
    hp_text = small_font.render(f"HP: {player_obj.hp}/{player_obj.max_hp}", True, config.WHITE)
    surface.blit(hp_text, hp_text.get_rect(center=(hp_x + hp_w//2, hp_y + hp_h//2)))

    # 3. 레벨 표시
    level_text = font.render(f"레벨: {player_obj.level}", True, config.WHITE)
    surface.blit(level_text, (hp_x, hp_y + hp_h + 5))

    # 4. 경험치 바 및 숫자
    exp_x, exp_y, exp_w, exp_h = hp_x, hp_y + hp_h + 35, 150, 15
    exp_ratio = player_obj.exp / player_obj.exp_to_level_up if player_obj.exp_to_level_up > 0 else 0
    
    pygame.draw.rect(surface, config.DARK_RED, (exp_x, exp_y, exp_w, exp_h), border_radius=3)
    if exp_ratio > 0:
        pygame.draw.rect(surface, config.EXP_BAR_COLOR, (exp_x, exp_y, int(exp_w * exp_ratio), exp_h), border_radius=3)
    
    # 🚩 EXP 숫자 표시 복구
    exp_text = small_font.render(f"EXP: {player_obj.exp}/{player_obj.exp_to_level_up}", True, config.WHITE)
    surface.blit(exp_text, exp_text.get_rect(center=(exp_x + exp_w//2, exp_y + exp_h//2)))

    # 6. 난이도 및 보스 처치 수 (좌측 하단)
    info_y = config.SCREEN_HEIGHT - 90
    diff_val = current_slime_max_hp_val / config.SLIME_INITIAL_BASE_HP
    diff_text = font.render(f"난이도: {diff_val:.1f}x", True, config.WHITE)
    surface.blit(diff_text, (10, info_y))
    
    boss_kill_text = font.render(f"보스 처치: {boss_defeat_count_val}", True, config.YELLOW)
    surface.blit(boss_kill_text, (10, info_y + 30))

    # 7. 보스 소환 게이지 및 숫자 (상단 중앙)
    bg_w, bg_h = 400, 25
    bg_x, bg_y = (config.SCREEN_WIDTH - bg_w) // 2, 10
    
    progress = slime_kill_count_val % boss_spawn_threshold_val
    bg_ratio = progress / boss_spawn_threshold_val if boss_spawn_threshold_val > 0 else 0

    pygame.draw.rect(surface, (100, 50, 0), (bg_x, bg_y, bg_w, bg_h), border_radius=5) 
    if bg_ratio > 0:
        pygame.draw.rect(surface, (255, 140, 0), (bg_x, bg_y, int(bg_w * bg_ratio), bg_h), border_radius=5)
    
    # 🚩 보스 소환 숫자 표시 복구
    boss_gauge_text = medium_font.render(f"다음 보스: {progress}/{boss_spawn_threshold_val}", True, config.WHITE)
    surface.blit(boss_gauge_text, boss_gauge_text.get_rect(center=(bg_x + bg_w//2, bg_y + bg_h//2)))

    # 8. 레벨업/보상 선택창 (Overlay)
    if player_obj.is_selecting_upgrade:
        draw_upgrade_overlay(surface, player_obj.upgrade_options_to_display, "레벨업!")
    elif getattr(player_obj, 'is_selecting_boss_reward', False): # 보스 보상 창 대응
        draw_upgrade_overlay(surface, player_obj.boss_reward_options_to_display, "보스 보상!")

def draw_upgrade_overlay(surface, options, title_text):
    """레벨업 또는 보스 보상 선택창 오버레이"""
    overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    title_s = large_font.render(title_text, True, config.WHITE)
    surface.blit(title_s, title_s.get_rect(center=(config.SCREEN_WIDTH//2, config.SCREEN_HEIGHT//4)))
    
    box_w, box_h, spacing = 600, 60, 15
    start_y = config.SCREEN_HEIGHT//2 - 50
    for i, opt in enumerate(options):
        rect = pygame.Rect((config.SCREEN_WIDTH - box_w)//2, start_y + i*(box_h + spacing), box_w, box_h)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BG_COLOR, rect, border_radius=10)
        pygame.draw.rect(surface, config.UI_OPTION_BOX_BORDER_COLOR, rect, 2, border_radius=10)
        
        txt = small_font.render(f"[{i+1}] {opt['text']}", True, config.WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))