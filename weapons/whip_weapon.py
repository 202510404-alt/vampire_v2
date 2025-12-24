# weapons/whip_weapon.py (그리드 최적화 버전)
import random
import math
import pygame
import config
import utils
from weapons.base_weapon import Weapon
from core.grid import enemy_grid # 🟢 그리드 엔진 임포트 추가

class WhipWeapon(Weapon):
    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.name = "채찍"
        self.damage = 5
        self.knockback_strength = 45
        self.attack_reach = 130
        self.attack_angle_range = math.pi
        self.cooldown = config.FPS*0.75
        self.attack_timer = self.cooldown
        self.is_attacking = False
        self.attack_animation_timer = 0
        self.attack_animation_duration = config.FPS*0.2
        self.current_attack_start_angle_on_screen = 0
        self.hit_slimes_this_attack = set()
        # 🟢 탐색 범위: 공격 범위(130)를 커버하기 위해 1칸 청크(250)면 충분
        self.target_search_radius_cells = 1 

    def update(self, slimes_list, game_entities_lists):
        if self.is_attacking:
            self.attack_animation_timer-=1
            if self.attack_animation_timer<=0: self.is_attacking=False
        
        self.attack_timer+=1
        if self.attack_timer>=self.cooldown and not self.is_attacking:
            
            # 🟢 1단계 렉 제거: 전체 적이 아닌 주변 적만 가져오기
            player_wx,player_wy=self.player.world_x,self.player.world_y
            # 주변 1칸 청크의 적들만 가져와서 검사 (search_radius_cells=1)
            nearby_enemies = enemy_grid.get_nearby_enemies(player_wx, player_wy, self.target_search_radius_cells)
            living_slimes=[s for s in nearby_enemies if s.hp>0] # 주변 적들 중에서만 살아있는 적 필터링
            
            closest_slime,min_dist_sq=None,float('inf')
            
            # 🟢 타겟 검색 (주변 적들만 대상으로 루프)
            if living_slimes:
                for slime_candidate in living_slimes:
                    dist_sq=utils.distance_sq_wrapped(player_wx,player_wy,slime_candidate.world_x,slime_candidate.world_y,config.MAP_WIDTH,config.MAP_HEIGHT)
                    if dist_sq<min_dist_sq: min_dist_sq=dist_sq; closest_slime=slime_candidate
            
            target_angle_rad=0
            # ... (이하 타겟 각도 계산 로직 동일) ...
            if closest_slime and min_dist_sq<(self.attack_reach*2)**2:
                dx_to_slime=utils.get_wrapped_delta(player_wx,closest_slime.world_x,config.MAP_WIDTH)
                dy_to_slime=utils.get_wrapped_delta(player_wy,closest_slime.world_y,config.MAP_HEIGHT)
                if not (dx_to_slime==0 and dy_to_slime==0): target_angle_rad=math.atan2(dy_to_slime,dx_to_slime)
            else:
                player_moved_dx=utils.get_wrapped_delta(self.player.prev_world_x,self.player.world_x,config.MAP_WIDTH)
                player_moved_dy=utils.get_wrapped_delta(self.player.prev_world_y,self.player.world_y,config.MAP_HEIGHT)
                if not (player_moved_dx==0 and player_moved_dy==0): target_angle_rad=math.atan2(player_moved_dy,player_moved_dx)
                else: target_angle_rad=self.current_attack_start_angle_on_screen+self.attack_angle_range/2
            
            self.attack_timer=0; self.is_attacking=True; self.attack_animation_timer=self.attack_animation_duration
            self.current_attack_start_angle_on_screen=target_angle_rad-(self.attack_angle_range/2)
            self.hit_slimes_this_attack.clear()

            # 🟢 2단계 렉 제거: 충돌 처리도 주변 적들만 대상으로 루프
            for slime in living_slimes: # 🚩 전체 적이 아닌 living_slimes (주변 적)만 대상으로 변경
                if slime in self.hit_slimes_this_attack: continue
                
                # ... (이하 충돌 및 각도 계산 로직 동일) ...
                dist_sq_to_slime=utils.distance_sq_wrapped(player_wx,player_wy,slime.world_x,slime.world_y,config.MAP_WIDTH,config.MAP_HEIGHT)
                if dist_sq_to_slime<=(self.attack_reach+slime.radius)**2:
                    dx_s=utils.get_wrapped_delta(player_wx,slime.world_x,config.MAP_WIDTH); dy_s=utils.get_wrapped_delta(player_wy,slime.world_y,config.MAP_HEIGHT)
                    angle_to_slime_rad=self.current_attack_start_angle_on_screen if dx_s==0 and dy_s==0 else math.atan2(dy_s,dx_s)
                    norm_start_angle=self.current_attack_start_angle_on_screen%(2*math.pi)
                    norm_slime_angle=angle_to_slime_rad%(2*math.pi)
                    norm_end_angle=(self.current_attack_start_angle_on_screen+self.attack_angle_range)%(2*math.pi)
                    in_angle=False
                    if norm_start_angle<=norm_end_angle:
                        if norm_start_angle<=norm_slime_angle<=norm_end_angle: in_angle=True
                    else:
                        if norm_start_angle<=norm_slime_angle or norm_slime_angle<=norm_end_angle: in_angle=True

                    if in_angle:
                        slime.take_damage(self.damage); self.hit_slimes_this_attack.add(slime)
                        if slime.hp>0:
                            dist_to_slime=math.sqrt(dist_sq_to_slime) if dist_sq_to_slime>0 else 1
                            norm_kb_dx=dx_s/dist_to_slime; norm_kb_dy=dy_s/dist_to_slime
                            slime.world_x=(slime.world_x+norm_kb_dx*self.knockback_strength)%config.MAP_WIDTH
                            slime.world_y=(slime.world_y+norm_kb_dy*self.knockback_strength)%config.MAP_HEIGHT
                            slime.rect.center=(int(slime.world_x),int(slime.world_y))

            # 적 발사체와의 충돌 (이것도 주변 발사체로 최적화 가능하지만, 일단 놔둡니다)
            slime_bullets_list_ref = game_entities_lists.get('slime_bullets')
            if slime_bullets_list_ref and self.is_attacking:
                for sb in slime_bullets_list_ref:
                    # ... (발사체 충돌 로직은 렉이 덜하므로 그대로 유지) ...
                    if sb.is_hit_by_player_attack: continue
                    dist_sq_to_bullet = utils.distance_sq_wrapped(player_wx, player_wy, sb.world_x, sb.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
                    if dist_sq_to_bullet <= (self.attack_reach + sb.size)**2:
                        dx_b = utils.get_wrapped_delta(player_wx, sb.world_x, config.MAP_WIDTH)
                        dy_b = utils.get_wrapped_delta(player_wy, sb.world_y, config.MAP_HEIGHT)
                        angle_to_bullet_rad = self.current_attack_start_angle_on_screen if dx_b == 0 and dy_b == 0 else math.atan2(dy_b, dx_b)
                        norm_start_angle_whip = self.current_attack_start_angle_on_screen % (2 * math.pi)
                        norm_bullet_angle = angle_to_bullet_rad % (2 * math.pi)
                        norm_end_angle_whip = (self.current_attack_start_angle_on_screen + self.attack_angle_range) % (2 * math.pi)
                        in_angle_bullet = False
                        if norm_start_angle_whip <= norm_end_angle_whip:
                            if norm_start_angle_whip <= norm_bullet_angle <= norm_end_angle_whip: in_angle_bullet = True
                        else:
                            if norm_start_angle_whip <= norm_bullet_angle or norm_bullet_angle <= norm_end_angle_whip: in_angle_bullet = True
                        if in_angle_bullet:
                            sb.is_hit_by_player_attack = True

    def draw(self, surface, camera_offset_x, camera_offset_y):
        if self.is_attacking:
            player_screen_x,player_screen_y=config.SCREEN_WIDTH//2,config.SCREEN_HEIGHT//2
            arc_visual_reach=self.attack_reach; points=[(player_screen_x,player_screen_y)]; num_segments=20
            for i in range(num_segments+1):
                angle=self.current_attack_start_angle_on_screen+(self.attack_angle_range*i/num_segments)
                x=player_screen_x+arc_visual_reach*math.cos(angle); y=player_screen_y+arc_visual_reach*math.sin(angle)
                points.append((x,y))
            if len(points)>=3:
                temp_surface=pygame.Surface((config.SCREEN_WIDTH,config.SCREEN_HEIGHT),pygame.SRCALPHA)
                try: pygame.draw.polygon(temp_surface,config.WHIP_TRANSPARENT_COLOR,points)
                except TypeError: pygame.draw.polygon(temp_surface,config.WHIP_TRANSPARENT_COLOR,[(int(p[0]),int(p[1])) for p in points])
                surface.blit(temp_surface,(0,0))

    def get_level_up_options(self):
        options=[{"text":f"데미지 ({self.damage} -> {self.damage+3})","type":"damage","value":self.damage+3},
                 {"text":f"넉백 ({self.knockback_strength} -> {self.knockback_strength+12})","type":"knockback","value":self.knockback_strength+12},
                 {"text":f"사거리 ({self.attack_reach} -> {self.attack_reach+25})","type":"reach","value":self.attack_reach+25},
                 {"text":f"공속 (쿨다운 {self.cooldown/config.FPS:.2f}초 -> {max(config.FPS*0.2,self.cooldown-config.FPS*0.1)/config.FPS:.2f}초)","type":"cooldown","value":max(config.FPS*0.2,self.cooldown-config.FPS*0.1)}]
        return random.sample(options,min(len(options),2))

    def apply_upgrade(self, upgrade_info):
        if upgrade_info["type"]=="damage":self.damage=upgrade_info["value"]
        elif upgrade_info["type"]=="knockback":self.knockback_strength=upgrade_info["value"]
        elif upgrade_info["type"]=="reach":self.attack_reach=upgrade_info["value"]
        elif upgrade_info["type"]=="cooldown":self.cooldown=upgrade_info["value"]
        self.level+=1