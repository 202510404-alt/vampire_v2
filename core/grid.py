# core/grid.py
import config
import utils

class GridSystem:
    def __init__(self, cell_size=250): # 청크 크기 (픽셀 단위)
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        """매 프레임마다 그리드를 비웁니다."""
        self.grid.clear()

    def register_enemy(self, enemy):
        """적의 현재 월드 좌표를 계산해 해당 청크에 등록합니다."""
        # 5000x5000 무한 루프 맵 대응
        cell_x = int((enemy.world_x % config.MAP_WIDTH) // self.cell_size)
        cell_y = int((enemy.world_y % config.MAP_HEIGHT) // self.cell_size)
        
        cell_key = (cell_x, cell_y)
        if cell_key not in self.grid:
            self.grid[cell_key] = []
        self.grid[cell_key].append(enemy)

    def get_nearby_enemies(self, world_x, world_y, search_radius_cells=2):
        """특정 좌표 주변 n칸 청크 내의 적들만 반환합니다."""
        center_x = int((world_x % config.MAP_WIDTH) // self.cell_size)
        center_y = int((world_y % config.MAP_HEIGHT) // self.cell_size)
        
        nearby_enemies = []
        # 그리드 개수 계산
        grid_width_cells = config.MAP_WIDTH // self.cell_size
        grid_height_cells = config.MAP_HEIGHT // self.cell_size

        for dx in range(-search_radius_cells, search_radius_cells + 1):
            for dy in range(-search_radius_cells, search_radius_cells + 1):
                # 맵 끝과 끝이 연결된 무한 루프 대응
                target_x = (center_x + dx) % grid_width_cells
                target_y = (center_y + dy) % grid_height_cells
                
                cell_key = (target_x, target_y)
                if cell_key in self.grid:
                    nearby_enemies.extend(self.grid[cell_key])
        
        return nearby_enemies

# 전역 객체 생성
enemy_grid = GridSystem(cell_size=250)