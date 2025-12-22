# player.py
import pygame
import math
import random
import config
import utils

# 무기 클래스 import
from weapons.base_weapon import Weapon
from weapons.dagger_launcher import DaggerLauncher
from weapons.flail_weapon import FlailWeapon
from weapons.whip_weapon import WhipWeapon
from weapons.bat_controller import BatController

# 스킬 클래스 import
from skills.storm_skill import StormSkill


class Player(pygame.sprite.Sprite):
    def __init__(self, initial_world_x, initial_world_y, name="Player"):
        super().__init__()
        self.image = pygame.Surface([config.PLAYER_SIZE, config.PLAYER_SIZE])
        self.image.fill(config.BLUE)
        self.total_enemies_killed = 0
        self.total_bosses_killed = 0
        self.rect = self.image.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.world_x = float(initial_world_x)
        self.world_y = float(initial_world_y)
        self.prev_world_x = self.world_x
        self.prev_world_y = self.world_y
        self.name = name
        self.hp = config.PLAYER_INITIAL_HP
        self.max_hp = config.PLAYER_INITIAL_HP
        self.invincible_timer = 0
        self.level = config.PLAYER_INITIAL_LEVEL
        self.exp = 0
        self.exp_to_level_up = config.PLAYER_INITIAL_EXP_TO_LEVEL_UP
        self.active_weapons = []

                # 🟢 화면 흔들림 강도 변수 추가
        self.shake_intensity = 0.0

        # 사용 가능한 새로운 무기 클래스 목록
        self.available_new_weapons = [DaggerLauncher, FlailWeapon, WhipWeapon, BatController]
        
        # 시작 무기 획득
        self.acquire_new_weapon(DaggerLauncher)
        
        self.is_selecting_upgrade = False
        self.upgrade_options_to_display = []

        self.special_skill = None
        self.is_selecting_boss_reward = False
        self.boss_reward_options_to_display = []

    def acquire_new_weapon(self, weapon_class_to_acquire):
        MAX_WEAPON_SLOTS = 10
        if any(isinstance(w, weapon_class_to_acquire) for w in self.active_weapons):
            if weapon_class_to_acquire in self.available_new_weapons:
                self.available_new_weapons.remove(weapon_class_to_acquire)
            return None

        if weapon_class_to_acquire in self.available_new_weapons:
            if len(self.active_weapons) >= MAX_WEAPON_SLOTS:
                removed_weapon = self.active_weapons.pop(0)
                print(f"무기 슬롯 초과: {removed_weapon.name} 제거.")
                removed_weapon_type = type(removed_weapon)
                if removed_weapon_type not in self.available_new_weapons:
                    self.available_new_weapons.append(removed_weapon_type)
                return removed_weapon # 제거된 무기를 반환하여 main.py에서 정리하도록

            new_weapon = weapon_class_to_acquire(self)
            self.active_weapons.append(new_weapon)
            if weapon_class_to_acquire in self.available_new_weapons:
                self.available_new_weapons.remove(weapon_class_to_acquire)
            print(f"{new_weapon.name} 획득!")
            return None # 제거된 무기가 없을 경우 None 반환
        return None

    def update(self, slimes_list, game_entities_lists):
        if self.hp <= 0 or self.is_selecting_upgrade or self.is_selecting_boss_reward:
             return

        self.prev_world_x = self.world_x
        self.prev_world_y = self.world_y

        if self.invincible_timer > 0: self.invincible_timer -= 1

        # 🟢 흔들림 감쇄 (더 확실하게 보이도록 선형 감소 사용)
        if self.shake_intensity > 0:
            self.shake_intensity -= 1.5  # 매 프레임 1.5씩 일정하게 감소
            if self.shake_intensity < 0:
                self.shake_intensity = 0

        keys = pygame.key.get_pressed()
        dx, dy = 0,0
        if keys[pygame.K_LEFT]: dx = -config.PLAYER_SPEED
        if keys[pygame.K_RIGHT]: dx = config.PLAYER_SPEED
        if keys[pygame.K_UP]: dy = -config.PLAYER_SPEED
        if keys[pygame.K_DOWN]: dy = config.PLAYER_SPEED

        self.world_x = (self.world_x + dx) % config.MAP_WIDTH
        self.world_y = (self.world_y + dy) % config.MAP_HEIGHT

        for weapon in self.active_weapons: weapon.update(slimes_list, game_entities_lists)
        if self.special_skill:
            self.special_skill.update()

    def take_damage(self, amount):
        self.shake_intensity = amount / 3.0 
        if self.invincible_timer > 0: return
        self.hp = max(0, self.hp - amount)
        self.invincible_timer = config.PLAYER_INVINCIBILITY_DURATION

    def heal(self, amount):
        if amount <= 0: return
        self.hp = min(self.max_hp, self.hp + math.ceil(amount))

    def gain_exp(self, amount):
        if self.hp <= 0 or self.is_selecting_upgrade or self.is_selecting_boss_reward: return
        self.exp += amount
        self.check_level_up()

    def check_level_up(self):
        if self.exp >= self.exp_to_level_up:
            self.exp -= self.exp_to_level_up
            self.level += 1
            self.exp_to_level_up = math.ceil(self.exp_to_level_up * 1.5)
            self.hp = self.max_hp
            print(f"LEVEL UP! Lv: {self.level}, Next EXP: {self.exp_to_level_up}")
            self.is_selecting_upgrade = True
            self.generate_upgrade_options()

    def generate_upgrade_options(self):
        self.upgrade_options_to_display = []
        pool = []

        if self.available_new_weapons:
            available_for_new_acquisition = [
                wt for wt in self.available_new_weapons
                if not any(isinstance(aw, wt) for aw in self.active_weapons)
            ]
            if available_for_new_acquisition:
                chosen_new_weapon_class = random.choice(available_for_new_acquisition)
                temp_instance = chosen_new_weapon_class(self)
                pool.append({"text": f"새 무기: {temp_instance.name}", "type": "new_weapon", "weapon_class": chosen_new_weapon_class})
                del temp_instance

        for wpn in self.active_weapons:
            weapon_upgrade_options = wpn.get_level_up_options()
            for opt_detail in weapon_upgrade_options:
                pool.append({"text": f"{wpn.name} (L{wpn.level}) 업그레이드: {opt_detail['text']}", "type": "existing_weapon_upgrade", "weapon_instance": wpn, "upgrade_details": opt_detail})

        if not pool and self.active_weapons :
             pool.append({"text": "최대 HP +20 증가", "type": "stat_hp", "value": 20})

        if pool:
            self.upgrade_options_to_display = random.sample(pool, min(len(pool), 3))

        if not self.upgrade_options_to_display:
            self.is_selecting_upgrade = False
            print("업그레이드 항목 없음!")
            self.max_hp += 10
            self.hp = self.max_hp
            print("대체 업그레이드: 최대 HP +10")

    def apply_chosen_upgrade(self, option_index):
        if not (self.is_selecting_upgrade and 0 <= option_index < len(self.upgrade_options_to_display)): return
        
        chosen_option = self.upgrade_options_to_display[option_index]
        
        removed_weapon_to_clean_up = None

        if chosen_option["type"] == "new_weapon":
            removed_weapon_to_clean_up = self.acquire_new_weapon(chosen_option["weapon_class"])
        elif chosen_option["type"] == "existing_weapon_upgrade":
            chosen_option["weapon_instance"].apply_upgrade(chosen_option["upgrade_details"])
        elif chosen_option["type"] == "stat_hp":
            self.max_hp += chosen_option["value"]
            self.hp = self.max_hp
            print(f"최대 HP +{chosen_option['value']} 증가!")
        
        self.is_selecting_upgrade = False
        self.upgrade_options_to_display = []
        return removed_weapon_to_clean_up # main.py에 제거된 무기를 전달하여 엔티티 정리

    def trigger_boss_reward_selection(self):
        if not self.special_skill:
             self.special_skill = StormSkill(self)
             print("보스 처치! 특수 스킬 '폭풍'을 획득했습니다! (마우스 우클릭으로 사용)")
        else:
            self.is_selecting_boss_reward = True
            self.boss_reward_options_to_display = self.special_skill.generate_upgrade_options()

    def apply_chosen_boss_reward(self, option_index):
        if not (self.is_selecting_boss_reward and 0 <= option_index < len(self.boss_reward_options_to_display)):
            return

        chosen_option = self.boss_reward_options_to_display[option_index]
        self.special_skill.apply_upgrade(chosen_option)

        self.is_selecting_boss_reward = False
        self.boss_reward_options_to_display = []

    def get_world_rect(self):
        return pygame.Rect(self.world_x-config.PLAYER_SIZE//2, self.world_y-config.PLAYER_SIZE//2, config.PLAYER_SIZE,config.PLAYER_SIZE)