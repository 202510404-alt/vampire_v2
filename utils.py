import math
import json
import asyncio
import config

# 1. 환경 감지 및 통신 모듈 설정
IS_WEB = False
try:
    from pyodide.http import pyfetch # type: ignore
    IS_WEB = True
except ImportError:
    import urllib.request
    IS_WEB = False

# ----------------------------------------------------
# 2. Supabase 통신 함수 (400 에러 상세 디버깅 포함)
# ----------------------------------------------------
async def _fetch_supabase(endpoint_with_query, method, data=None):
    url = f"{config.SUPABASE_URL}/rest/v1/{endpoint_with_query}"
    
    # Supabase 필수 헤더
    headers = {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    if IS_WEB:
        try:
            await asyncio.sleep(0.01) # 멈춤 방지
            body_json = json.dumps(data) if data else None
            response = await pyfetch(url, method=method, headers=headers, body=body_json)
            if response.status in [200, 201]:
                return await response.string()
            return None
        except: return None
    else:
        try:
            # 로컬(VSC)용 urllib 방식
            req_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as res:
                return res.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            # 🚩 400 에러 원인을 더 자세히 찍어줍니다 (컬럼명 오타 확인용)
            err_body = e.read().decode('utf-8')
            print(f"LOCAL DB ERROR: {e.code} {err_body}")
            return None
        except Exception as e:
            print(f"LOCAL DB ERROR: {e}")
            return None

# ----------------------------------------------------
# 3. 랭킹 로드 (UI 데이터 포맷 변환)
# ----------------------------------------------------
async def load_rankings_online():
    # 전체 데이터를 가져와서 UI 형식에 맞게 변환
    data_str = await _fetch_supabase("rankings?select=*", 'GET')
    
    formatted_list = []
    if data_str:
        try:
            raw_list = json.loads(data_str)
            for row in raw_list:
                # 메인 UI가 인식하는 카테고리별로 데이터 뻥튀기
                for cat in ["Levels", "Kills", "Bosses", "DifficultyScore", "SurvivalTime"]:
                    # DB 컬럼명과 UI 키 연결
                    db_col = cat.lower().replace("score", "_score").replace("time", "_time")
                    formatted_list.append({
                        "ID": row.get("name", "익명"),
                        "RankCategory": cat,
                        "RankValue": float(row.get(db_col, 0)),
                        "Levels": row.get("levels", 0),
                        "Kills": row.get("kills", 0)
                    })
        except Exception as e:
            print(f"파싱 에러: {e}")
    return formatted_list

# ----------------------------------------------------
# 4. 랭킹 저장
# ----------------------------------------------------
async def save_new_ranking_online(name, score_data):
    new_row = {
        "name": str(name),
        "levels": int(score_data.get('levels', 0)),
        "kills": int(score_data.get('kills', 0)),
        "bosses": int(score_data.get('bosses', 0)),
        "difficulty_score": float(score_data.get('difficulty_score', 0.0)),
        "survival_time": float(score_data.get('survival_time', 0.0))
    }
    
    res = await _fetch_supabase("rankings", 'POST', data=new_row)
    if res:
        print("Supabase DB에 저장 성공!")
        return True
    return False

# ----------------------------------------------------
# 5. 🚩 거리 계산 유틸리티 (이게 빠져서 튕겼던 거임!!)
# ----------------------------------------------------
def get_wrapped_delta(val1, val2, map_dim):
    """무한 루프 맵에서 두 좌표 사이의 최단 거리를 계산합니다."""
    delta = val2 - val1
    if abs(delta) > map_dim / 2:
        if delta > 0: delta -= map_dim
        else: delta += map_dim
    return delta

def distance_sq_wrapped(x1, y1, x2, y2, map_w, map_h):
    """무한 루프 맵에서 두 좌표 사이의 거리의 제곱을 계산합니다."""
    dx = get_wrapped_delta(x1, x2, map_w)
    dy = get_wrapped_delta(y1, y2, map_h)
    return dx*dx + dy*dy