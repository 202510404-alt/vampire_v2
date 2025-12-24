# entities/bat_minion.py (최적화 버전)
import pygame
import math
import random
import config
import utils
from core.grid import enemy_grid # 🟢 개쩌는 그리드 엔진 임포트

class BatMinion:
    STATE_WANDERING = 0
    STATE_ATTACKING = 1
    STATE_COOLDOWN = 2

    def __init__(self, controller_ref, world_x, world_y):
        self.controller = controller_ref
        self.player = self.controller.player 
        self.world_x = float(world_x % config.MAP_WIDTH)
        self.world_y = float(world_y % config.MAP_HEIGHT)
        self.size = config.BAT_SIZE
        self.color = config.BAT_COLOR
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifespan = config.BAT_LIFESPAN_SECONDS * config.FPS
        self.current_speed = config.BAT_WANDER_SPEED
        self.state = BatMinion.STATE_WANDERING
        self.target_slime = None
        self.attack_cooldown_timer = 0
        self.wander_target_x = self.world_x
        self.wander_target_y = self.world_y
        self.time_to_new_wander_target = 0

    def update(self, slimes_list, game_entities_lists):
        self.lifespan -= 1
        if self.lifespan <= 0: return False

        # 1. 적 발사체 제거 로직 (이것도 주변 발사체만 체크하도록 나중에 고칠 수 있음)
        slime_bullets_list_ref = game_entities_lists.get('slime_bullets')
        if slime_bullets_list_ref:
            for sb in slime_bullets_list_ref:
                if sb.is_hit_by_player_attack: continue
                dist_sq_bullet = utils.distance_sq_wrapped(self.world_x, self.world_y, sb.world_x, sb.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
                if dist_sq_bullet < (self.size + sb.size)**2:
                    sb.is_hit_by_player_attack = True

        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -=1
            if self.attack_cooldown_timer <= 0: self.state = BatMinion.STATE_WANDERING

        # 2. 🟢 타겟 검색 로직 (최적화 핵심)
        if self.state == BatMinion.STATE_WANDERING:
            self.current_speed = config.BAT_WANDER_SPEED
            closest_slime, min_dist_sq = None, (config.BAT_DETECTION_RADIUS ** 2)

            # 🚩 기존: 전수조사 (all_slimes = slimes_list + boss_slimes)
            # 🚩 변경: 주변 청크(250x250) 2칸 범위 내의 적들만 조사
            nearby_enemies = enemy_grid.get_nearby_enemies(self.world_x, self.world_y, search_radius_cells=2)
            
            for slime in nearby_enemies:
                if slime.hp <= 0: continue
                dist_sq = utils.distance_sq_wrapped(self.world_x, self.world_y, slime.world_x, slime.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
                if dist_sq < min_dist_sq: 
                    min_dist_sq = dist_sq
                    closest_slime = slime
            
            if closest_slime: 
                self.target_slime = closest_slime
                self.state = BatMinion.STATE_ATTACKING
            else: 
                self._wander()

        elif self.state == BatMinion.STATE_ATTACKING:
            self.current_speed = config.BAT_ATTACK_SPEED
            if not self.target_slime or self.target_slime.hp <= 0:
                self.target_slime = None; self.state = BatMinion.STATE_WANDERING; self._wander(); return True
            
            dist_sq_to_target = utils.distance_sq_wrapped(self.world_x, self.world_y, self.target_slime.world_x, self.target_slime.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
            dist_to_target = math.sqrt(dist_sq_to_target)
            required_hit_dist = self.size + self.target_slime.radius
            
            if dist_to_target < required_hit_dist:
                actual_damage = self.controller.damage
                self.target_slime.take_damage(actual_damage)
                healed_amount = actual_damage * self.controller.lifesteal_percentage
                if healed_amount > 0: self.player.heal(healed_amount)
                self.target_slime = None; self.state = BatMinion.STATE_COOLDOWN
                self.attack_cooldown_timer = config.BAT_ATTACK_COOLDOWN
            elif dist_to_target > 0 :
                dx_move = utils.get_wrapped_delta(self.world_x, self.target_slime.world_x, config.MAP_WIDTH)
                dy_move = utils.get_wrapped_delta(self.world_y, self.target_slime.world_y, config.MAP_HEIGHT)
                self.angle = math.atan2(dy_move, dx_move)
                self.world_x += math.cos(self.angle) * self.current_speed
                self.world_y += math.sin(self.angle) * self.current_speed

        self.world_x %= config.MAP_WIDTH; self.world_y %= config.MAP_HEIGHT
        return True

    def _wander(self):
        # ... (이하 동일하므로 생략하지만 실제 코드에는 그대로 유지)
        self.time_to_new_wander_target -= 1
        if self.time_to_new_wander_target <= 0:
            angle_to_player_offset = random.uniform(0, 2 * math.pi)
            dist_from_player = random.uniform(config.BAT_WANDER_RADIUS_FROM_PLAYER*0.5, config.BAT_WANDER_RADIUS_FROM_PLAYER)
            target_rel_x = dist_from_player * math.cos(angle_to_player_offset)
            target_rel_y = dist_from_player * math.sin(angle_to_player_offset)
            self.wander_target_x = (self.player.world_x + target_rel_x) % config.MAP_WIDTH
            self.wander_target_y = (self.player.world_y + target_rel_y) % config.MAP_HEIGHT
            self.time_to_new_wander_target = random.randint(config.FPS * 1, config.FPS * 3)

        dist_sq_to_wander_target = utils.distance_sq_wrapped(self.world_x, self.world_y, self.wander_target_x, self.wander_target_y, config.MAP_WIDTH, config.MAP_HEIGHT)
        if dist_sq_to_wander_target > (self.current_speed ** 2) :
            dx_move = utils.get_wrapped_delta(self.world_x, self.wander_target_x, config.MAP_WIDTH)
            dy_move = utils.get_wrapped_delta(self.world_y, self.wander_target_y, config.MAP_HEIGHT)
            self.angle = math.atan2(dy_move, dx_move)
            self.world_x += math.cos(self.angle) * self.current_speed
            self.world_y += math.sin(self.angle) * self.current_speed
        else:
            self.time_to_new_wander_target = 0

    def draw(self, surface, camera_offset_x, camera_offset_y):
        # ... (이하 드로우 로직 동일)
        for dx_offset in [-config.MAP_WIDTH, 0, config.MAP_WIDTH]:
            for dy_offset in [-config.MAP_HEIGHT, 0, config.MAP_HEIGHT]:
                obj_world_x_render = self.world_x + dx_offset
                obj_world_y_render = self.world_y + dy_offset
                screen_x = obj_world_x_render - camera_offset_x
                screen_y = obj_world_y_render - camera_offset_y
                if -self.size < screen_x < config.SCREEN_WIDTH + self.size and \
                   -self.size < screen_y < config.SCREEN_HEIGHT + self.size:
                    pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.size)
                    return