# enemies/slime.py (수정됨)
import pygame
import math
import os
import config
import utils

class Slime:
    # --- 각 슬라임 종류별 애니메이션 이미지 캐싱을 위한 클래스 변수 ---
    _animation_cache = {}

    # current_total_max_hp: 이 슬라임이 생성될 시점의 실시간 현재 기준 총 HP (main.py의 current_slime_max_hp 값)
    # hp_multiplier: 이 슬라임 종류가 가지는 HP 배율 (예: 민트 슬라임은 0.5, 보스 슬라임은 100)
    def __init__(self, world_x, world_y, radius, color, speed, current_total_max_hp, hp_multiplier=1.0):
        self.world_x = float(world_x % config.MAP_WIDTH)
        self.world_y = float(world_y % config.MAP_HEIGHT)
        self.radius = radius
        self.color = color
        self.speed = speed
        
        # main.py에서 전달받은 현재 총 HP에 해당 슬라임 종류의 배율을 곱하여 max_hp 설정
        self.max_hp = math.ceil(current_total_max_hp * hp_multiplier) # 소수점 올림 처리
        self.hp = self.max_hp

       # 🟢 피격 이펙트 타이머 추가 (0이면 평상시, 0보다 크면 빨간 상태)
        self.hit_flash_timer = 0
        self.flash_duration = 5 # 빨간색이 유지될 프레임 (약 0.1초)
        
        self.rect = pygame.Rect(0,0,radius*2,radius*2)
        self.rect.center = (self.world_x,self.world_y)
        self.lifespan = config.SLIME_LIFESPAN_SECONDS * config.FPS
        self.damage_to_player = config.SLIME_DAMAGE_TO_PLAYER

        # --- 애니메이션 이미지 로드 (인스턴스 변수) ---
        self.animation_images = self._load_animation_images()

        # 애니메이션 관련 변수
        self.animation_sequence = [0, 1, 2, 3, 2, 1, 4, 0] # 1->2->3->4->3->2->5->1 순서로 변경
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.1 # 프레임 변경 속도 (값이 작을수록 빠름)

    def _get_image_filename_prefix(self):
        """클래스 이름에 따라 이미지 파일 이름의 접두사를 결정합니다."""
        class_name = self.__class__.__name__
        if class_name == "Slime": return "slime"
        if class_name == "MintSlime": return "mintslime"
        if class_name == "ShooterSlime": return "shooterslime"
        if class_name == "BossSlime": return "slimeboss"
        if class_name == "BossMinionSlime": return "minislime"
        return "slime" # 기본값

    def _load_animation_images(self):
        """슬라임 종류에 맞는 애니메이션 이미지들을 로드하고 캐시에 저장합니다."""
        prefix = self._get_image_filename_prefix()
        if prefix in Slime._animation_cache:
            return Slime._animation_cache[prefix]

        images = []
        try:
            path = os.path.join('image', 'slimes') # 'slimes' 폴더로 경로 수정
            for i in range(1, 6):
                img_path = os.path.join(path, f"{prefix}{i}.png") # 각 슬라임에 맞는 파일 이름으로 수정
                original_image = pygame.image.load(img_path).convert_alpha()
                scaled_image = pygame.transform.scale(original_image, (self.radius * 2, self.radius * 2))
                images.append(scaled_image)
            print(f"정보: '{prefix}' 슬라임 애니메이션 로드 성공.")
            Slime._animation_cache[prefix] = images
        except pygame.error as e:
            print(f"경고: '{prefix}' 슬라임 이미지 로드 실패: {e}. 원으로 표시됩니다.")
            Slime._animation_cache[prefix] = [] # 실패 시 빈 리스트 캐싱
        return Slime._animation_cache[prefix]

    def update(self, target_player_world_x, target_player_world_y, game_entities_lists=None):
        if self.hp <= 0: return False

         # 🟢 이펙트 타이머 감소
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        self.lifespan -= 1
        if self.lifespan <= 0: self.hp = 0; return False

        dist_sq = utils.distance_sq_wrapped(self.world_x, self.world_y, target_player_world_x, target_player_world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
        dist = math.sqrt(dist_sq)
        stop_distance = config.PLAYER_SIZE / 2 + self.radius

        if dist > self.speed + stop_distance :
            dx = utils.get_wrapped_delta(self.world_x,target_player_world_x,config.MAP_WIDTH)
            dy = utils.get_wrapped_delta(self.world_y,target_player_world_y,config.MAP_HEIGHT)
            self.world_x = (self.world_x + (dx / dist) * self.speed) % config.MAP_WIDTH
            self.world_y = (self.world_y + (dy / dist) * self.speed) % config.MAP_HEIGHT

        # 애니메이션 프레임 업데이트
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * config.FPS:
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_sequence)


        self.rect.center = (int(self.world_x), int(self.world_y))
        return True

    def take_damage(self, amount):
        self.hp -= amount
        # 🟢 데미지 입을 때 타이머 작동
        self.hit_flash_timer = self.flash_duration 
        if self.hp <= 0: self.hp = 0; return True
        return False
    
    def draw(self, surface, camera_offset_x, camera_offset_y):
            for dx_off in [-config.MAP_WIDTH, 0, config.MAP_WIDTH]:
                for dy_off in [-config.MAP_HEIGHT, 0, config.MAP_HEIGHT]:
                    obj_wx_render, obj_wy_render = self.world_x+dx_off, self.world_y+dy_off
                    scr_x, scr_y = obj_wx_render-camera_offset_x, obj_wy_render-camera_offset_y

                    if -self.radius < scr_x < config.SCREEN_WIDTH+self.radius and \
                    -self.radius < scr_y < config.SCREEN_HEIGHT+self.radius:

                        if self.animation_images:
                            frame_index = self.animation_sequence[self.current_frame_index]
                            original_image = self.animation_images[frame_index]
                            
                            # 🟢 렌더링용 이미지 결정
                            render_image = original_image
                            if self.hit_flash_timer > 0:
                                # 이미지를 복사해서 빨간색 틴트를 입힘
                                render_image = original_image.copy()
                                # 빨간색 표면 생성
                                flash_surf = pygame.Surface(render_image.get_size(), pygame.SRCALPHA)
                                flash_surf.fill((255, 50, 50, 255)) # 밝은 빨강
                                # 이미지의 투명도 정보를 유지하며 빨간색 덧씌우기
                                render_image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            
                            surface.blit(render_image, render_image.get_rect(center=(int(scr_x), int(scr_y))))
                        else: 
                            # 이미지 실패 시 원 그리기 (피격 시 흰색/빨간색 테두리 효과)
                            draw_color = (255, 0, 0) if self.hit_flash_timer > 0 else self.color
                            pygame.draw.circle(surface, draw_color, (int(scr_x), int(scr_y)), self.radius)

                        # HP 바 그리기 (동일)
                        if self.hp < self.max_hp and self.hp > 0:
                            bar_width = self.radius * 2
                            bar_height = config.SLIME_HP_BAR_HEIGHT
                            bar_screen_x = scr_x - bar_width//2
                            bar_screen_y = scr_y - self.radius - bar_height - 5
                            pygame.draw.rect(surface, config.DARK_RED, (bar_screen_x, bar_screen_y, bar_width, bar_height))
                            current_hp_bar_width = int(bar_width*(self.hp/self.max_hp)) if self.max_hp>0 else 0
                            if current_hp_bar_width > 0: pygame.draw.rect(surface, config.HP_BAR_GREEN, (bar_screen_x, bar_screen_y, current_hp_bar_width, bar_height))
                        return