# weapons/dagger_launcher.py (그리드 최적화 버전)
import random
import math
import pygame
import config
import utils
from weapons.base_weapon import Weapon
from entities.dagger import Dagger 
from core.grid import enemy_grid # 🟢 그리드 엔진 임포트 추가

class DaggerLauncher(Weapon):
    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.name = "단검"
        self.damage = config.PLAYER_DAGGER_DAMAGE_BASE
        self.cooldown = config.PLAYER_ATTACK_COOLDOWN
        self.attack_timer = 0
        self.num_daggers_per_shot = 1
        # 🟢 단검의 타겟팅 탐지 거리 (2칸 청크 정도면 충분)
        self.target_search_radius_cells = 2

    def update(self, slimes_list, game_entities_lists):
        daggers_list_ref = game_entities_lists.get('daggers')
        if daggers_list_ref is None: return

        self.attack_timer += 1
        if self.attack_timer >= self.cooldown:
            
            self.attack_timer = 0
            player_wx,player_wy = self.player.world_x,self.player.world_y
            
            # 🟢 1. 그리드 엔진을 사용하여 플레이어 주변 적만 가져오기
            # 전체 맵의 적이 아니라, 주변 2칸 청크의 적들만!
            nearby_enemies = enemy_grid.get_nearby_enemies(player_wx, player_wy, self.target_search_radius_cells)
            
            # 2. 살아있는 적들만 필터링
            living_slimes = [s for s in nearby_enemies if s.hp > 0]
            if not living_slimes: return

            targets_to_shoot = []
            
            if len(living_slimes) <= self.num_daggers_per_shot:
                # 3. 주변 적이 발사할 단검 수보다 적다면 모두 타겟으로 지정
                targets_to_shoot.extend(living_slimes)
            else:
                # 4. 주변 적들만 대상으로 거리를 계산하고, 가까운 순서대로 단검 수만큼 타겟 지정
                sorted_slimes = sorted(living_slimes,key=lambda s:utils.distance_sq_wrapped(player_wx,player_wy,s.world_x,s.world_y,config.MAP_WIDTH,config.MAP_HEIGHT))
                targets_to_shoot.extend(sorted_slimes[:self.num_daggers_per_shot])
                
            # 5. 타겟팅된 적들에게 단검 발사
            for target_slime_for_dagger in targets_to_shoot:
                if target_slime_for_dagger:
                    daggers_list_ref.append(Dagger(player_wx,player_wy,target_slime_for_dagger,self.damage))

    # ... (이하 get_level_up_options, apply_upgrade, draw 함수는 동일하므로 생략)
    def get_level_up_options(self):
        options=[{"text":f"데미지 ({self.damage} -> {math.ceil(self.damage*config.PLAYER_DAGGER_DAMAGE_MULTIPLIER_PER_LEVEL)})","type":"damage","value":math.ceil(self.damage*config.PLAYER_DAGGER_DAMAGE_MULTIPLIER_PER_LEVEL)},
                 {"text":f"공속 (쿨다운 {self.cooldown} -> {max(10,self.cooldown-5)})","type":"cooldown","value":max(10,self.cooldown-5)},
                 {"text":f"발사 수 ({self.num_daggers_per_shot} -> {self.num_daggers_per_shot+1})","type":"num_daggers","value":self.num_daggers_per_shot+1}]
        return random.sample(options,min(len(options),2))

    def apply_upgrade(self, upgrade_info):
        if upgrade_info["type"]=="damage":self.damage=upgrade_info["value"]
        elif upgrade_info["type"]=="cooldown":self.cooldown=upgrade_info["value"]
        elif upgrade_info["type"]=="num_daggers":self.num_daggers_per_shot=upgrade_info["value"]
        self.level+=1

    def draw(self, surface, camera_offset_x, camera_offset_y):
        # 단검 발사기는 그리는 요소가 없으므로 pass
        pass