# utils.py (JSONbin.io 온라인 통신 버전 - 클린)
import math
import json
import config
# 🚩 온라인 통신을 위한 라이브러리 import (Pygbag 호환)
import urllib.request
import urllib.parse
import pygame 

# 랭킹 항목 정의 (정렬 및 필터링에 사용)
RANK_CATEGORIES = [
  "Levels", "Kills", "Bosses", "DifficultyScore", "SurvivalTime"
]

# ----------------------------------------------------
# 랭킹 저장/로드 함수 (JSONbin.io 버전)
# ----------------------------------------------------

def load_rankings_jsonbin():
    """JSONbin에서 전체 랭킹 데이터를 GET 요청으로 수신합니다."""
    
    req = urllib.request.Request(
        config.JSONBIN_BIN_URL + "/latest", # 최신 버전 가져오기
        headers={'X-Master-Key': config.JSONBIN_API_KEY, 'Accept': 'application/json'},
        method='GET'
    )
    
    try:
        context = ssl._create_unverified_context() 
        with urllib.request.urlopen(req, context=context) as response:
            data = response.read().decode('utf-8')
            # JSONbin의 응답 형식: {"record": {"rankings": [...]}}
            return json.loads(data).get('record', {}).get('rankings', [])
            
    except Exception as e:
        print(f"ERROR: JSONbin 랭킹 로드 실패: {e}")
        return []

def save_new_ranking_jsonbin(name, score_data):
    """새 기록을 JSONbin의 기존 랭킹에 통합하고, 전체 데이터를 PUT 요청으로 덮어씁니다."""
    
    # 1. 기존 데이터 로드
    current_data = load_rankings_jsonbin()
    
    # 2. 새 기록 생성
    new_record = {
        "RankCategory": "", 
        "RankValue": 0.0,
        "ID": name,
        "Levels": float(score_data.get('level', 0.0)),
        "Kills": float(score_data.get('kills', 0.0)),
        "Bosses": float(score_data.get('bosses', 0.0)),
        "DifficultyScore": float(score_data.get('difficulty_score', 0.0)),
        "SurvivalTime": float(score_data.get('survival_time', 0.0))
    }
    
    # 3. 항목별 랭킹 진입 확인 및 추가 로직
    records_to_add = []
    
    for category_key in RANK_CATEGORIES:
        category_score = new_record[category_key]
        
        # 해당 카테고리의 현재 랭킹 10개만 필터링
        filtered_rankings = [
            r for r in current_data 
            if r.get('RankCategory') == category_key
        ]
        
        # RankValue를 기준으로 정렬
        filtered_rankings.sort(key=lambda x: x.get('RankValue', 0.0), reverse=True)
        
        # 10위 안에 들었는지 확인
        if len(filtered_rankings) < 10 or category_score > filtered_rankings[9].get('RankValue', 0.0):
            
            # 랭킹에 들었으면 새 레코드를 생성하여 추가
            record_to_add = new_record.copy()
            record_to_add['RankCategory'] = category_key
            record_to_add['RankValue'] = category_score
            records_to_add.append(record_to_add)

    # 4. 랭킹에 든 기록이 있을 경우에만 서버에 PUT 요청
    if records_to_add:
        # 기존 데이터에 새 기록 추가
        for record in records_to_add:
            current_data.append(record)
        
        # 전체 데이터 정리 (각 카테고리당 상위 10개만 유지)
        final_rankings = []
        for category_key in RANK_CATEGORIES:
            category_list = [r for r in current_data if r.get('RankCategory') == category_key]
            category_list.sort(key=lambda x: x.get('RankValue', 0.0), reverse=True)
            final_rankings.extend(category_list[:10])
            
        # 5. JSONbin에 PUT 요청 (전체 덮어쓰기)
        data_to_save = {"rankings": final_rankings} # JSONbin이 요구하는 형식
        data_json = json.dumps(data_to_save).encode('utf-8')
        
        req = urllib.request.Request(
            config.JSONBIN_BIN_URL, 
            data=data_json, 
            headers={
                'Content-Type': 'application/json',
                'X-Master-Key': config.JSONBIN_API_KEY,
                'X-Bin-Versioning': 'false' 
            },
            method='PUT'
        )
        
        try:
            context = ssl._create_unverified_context() 
            with urllib.request.urlopen(req, context=context) as response:
                result = response.read().decode('utf-8')
                print(f"DEBUG: JSONbin PUT 응답: {result}")
                return {"success": True, "message": "랭킹 저장 완료"}
        except Exception as e:
            print(f"ERROR: JSONbin PUT 실패: {e}")
            return {"success": False, "message": f"저장 오류: {e}"}

    return {"success": True, "message": "10위권 밖 기록, 저장 안 함"}


# 🚩 main.py에서 사용할 수 있도록 함수 이름 변경
load_rankings_online = load_rankings_jsonbin 
save_new_ranking_online = save_new_ranking_jsonbin

# ... (기존 utils 함수 유지)
def get_wrapped_delta(val1, val2, map_dim):
    delta = val2 - val1
    if abs(delta) > map_dim / 2:
        if delta > 0: delta -= map_dim
        else: delta += map_dim
    return delta

def distance_sq_wrapped(x1, y1, x2, y2, map_w, map_h):
    dx = get_wrapped_delta(x1, x2, map_w)
    dy = get_wrapped_delta(y1, y2, map_h)
    return dx*dx + dy*dy