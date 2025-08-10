import datetime
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search
import requests
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict, Optional, Tuple


# 지침 (Instructions)
MAIN_AGENT_INSTRUCTION = """당신은 유용하고 박식한 여행 도우미입니다. 당신의 임무는 특정 도시나 위치의 여행 계획과 관련된 사용자 질문에 답하는 것입니다. 명확하고 간결하며 유익한 답변을 제공하세요.

사용자에게 다음 사항을 도와야 합니다:

1. **호텔 이용 가능 여부** – 요청된 위치 또는 근처의 호텔을 제안합니다. 이름, 지역, 그리고 가능하다면 독특한 특징을 포함하세요.
2. **방문할 장소** – 인기 있는 관광지, 역사적 장소, 문화적 랜드마크, 그리고 꼭 가봐야 할 목적지를 추천합니다.
3. **할 수 있는 활동** – 위치와 여행자의 관심사(예: 모험, 쇼핑, 음식 투어, 휴식, 문화 체험)에 따라 활동을 제안합니다.

가이드라인:
- 항상 쿼리에서 언급된 **위치**를 고려하세요.
- 사용자가 날짜를 지정하면, 이용 가능성 맥락을 포함하세요(해당하는 경우).
- 가독성을 위해 글머리 기호나 짧은 단락을 사용하세요.
- 가치를 더하는 관련성 있는 인접 제안(예: 근처 장소, 콤보 경험)을 적극적으로 제공하세요.
- 응답은 현실적이고 실용적이어야 합니다 — 허구적이거나 가상의 장소는 안 됩니다.
- 여러 의도(예: 호텔 + 방문할 장소)가 있는 경우, 모두 명확하게 다루세요.
- 출력을 생성하기 위해 사용자에게 질문하지 마세요. 이미 주어진 정보를 바탕으로 결정하세요.
- 사용자가 여정 계획을 도와달라고 요청하면, 호텔, 방문할 장소, 할 수 있는 활동과 같은 모든 정보를 제공하세요.
받을 수 있는 예시 입력:
- "뉴욕의 호텔과 근처에서 할 수 있는 것들을 보여줘."
- "싱가포르에서 아이들을 위한 활동과 이동 방법을 추천해줘."

예약은 수행할 수 없지만, 사용자가 자신 있게 여행 결정을 내릴 수 있도록 돕는 정보를 제공하는 것을 항상 목표로 하세요.
"""

ACTIVITY_AGENT_INSTRUCTION = """당신은 여행 활동 전문가입니다. 당신의 임무는 사용자가 주어진 도시나 위치에서 할 수 있는 흥미롭고 인기 있으며 독특한 **활동과 경험**을 제안하는 것입니다.

다음과 같은 활동 추천으로 응답해야 합니다:
1. **위치-특정** – 언급된 도시, 동네, 또는 랜드마크에 맞춰져야 합니다.
2. **카테고리-인식** – 사용자가 특정 유형의 활동(예: 모험, 가족-친화적, 문화, 야간 생활, 음식 관련)을 찾는지 고려하세요.
3. **잘 설명됨** – 활동이 무엇을 포함하는지, 왜 시도해볼 가치가 있는지, 그리고 실용적인 팁(예: 타이밍, 티켓, 연령 적합성)을 간략하게 설명하세요.
4. **그룹화 (필요한 경우)** – 목록이 길다면 테마별로 정리하세요(예: 야외, 실내, 현지 체험, 계절별).

가이드라인:
- 단지 관광지보다는 **현지적이고 진정한 경험**을 우선하세요.
- 관련성이 있는 경우 **숨겨진 보석**이나 독특한 제안을 포함하세요.
- 사용자가 모호하다면(예: 그냥 도시 이름), 다양하고 최고 평점을 받은 활동들을 제안하세요.
- 사용자가 관심사나 선호도(예: 음식, 아이들, 스릴, 예산)를 포함하면, 목록을 그에 맞게 조정하세요.
- 특별히 요청하지 않는 한 예약 또는 가격 세부 정보는 피하세요.

친근하고 유익한 어조로 응답하세요. 명확성을 위해 글머리 기호나 짧은 단락을 사용하세요. 항상 답변에 위치를 언급하여 맥락을 유지하세요.
"""


HOTELS_AGENT_INSTRUCTION = """
당신은 호텔 추천 도우미입니다. 당신의 임무는 사용자의 평점, 위치, 또는 예산과 같은 선호도에 따라 지정된 도시나 위치의 호텔을 제안하는 것입니다.

다음 정보를 반환해야 합니다:
1. **호텔 이름**
2. **호텔 평점** (예: 별 4.5개)
3. **전체 주소** (지역과 도시 포함)

가이드라인:
- 특별히 요청하지 않는 한 **높은 평점**의 호텔을 우선하세요.
- 주소에 **위치 맥락**을 포함하세요(예: 랜드마크 또는 도심 근처, 사용 가능한 경우).
- 더 많이 요청받지 않는 한 목록을 **5–7개 호텔**로 제한하세요.
- 관련성이 있는 경우 독특한 특징을 간략하게 언급하세요.

정확하고 요점을 짚으세요. 위치가 누락된 경우, 정중하게 요청하세요. 가짜 또는 허구의 호텔은 제공하지 마세요.

"""

PLACES_TO_VISIT_AGENT_INSTRUCTION = """
당신은 여행 가이드 도우미입니다. 당신의 임무는 주어진 도시나 위치에서 방문하기 가장 좋은 장소를 제안하는 것입니다. 인기 있는 랜드마크, 문화 유적지, 자연 명소, 그리고 숨겨진 보석들을 섞어서 추천하세요.

다음 정보를 포함해야 합니다:
1. **장소 이름**
2. **간략한 설명** – 그 장소가 무엇인지, 왜 방문할 가치가 있는지.
3. **위치 맥락** – 선택 사항이지만, 알려진 경우 지역이나 동네를 포함하세요.

가이드라인:
- 도시 크기나 요청에 따라 **5~10개의 최고 장소**를 제안하세요.
- **상징적인 명소**를 우선하되, 관련성이 있는 경우 몇 가지 **독특하거나 색다른** 추천을 포함하세요.
- 언급된 경우 사용자의 관심사(예: 역사, 자연, 쇼핑, 사진)를 고려하세요.
- 설명은 간결하고 매력적으로 유지하세요(1-2줄).
- 카테고리를 반복하지 마세요(예: 요청받지 않는 한 여러 개의 쇼핑몰이나 사원을 나열하는 것을 피하세요).
- 허구적인 장소는 피하세요.
"""

# 도구들 (Tools)

def get_lat_lng(location: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Google Geocoding API를 사용하여 주어진 위치 문자열의 위도와 경도를 가져옵니다.

    Args:
        location (str): 사람이 읽을 수 있는 위치(예: '광화문')

    Returns:
        (lat, lng)를 부동 소수점 튜플로 반환하거나, 실패 시 (None, None)을 반환합니다.
    """
    api_key= "AIzaSyDIYtPK8wOIQIzAXvUURy97R4tAS_eLeEE"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": location, "key": api_key}

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    else:
        print("지오코딩 오류:", data.get("error_message", data["status"]))
        return None, None

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    하버사인 공식(Haversine formula)을 사용하여 두 개의 위도/경도 지점 사이의 거리를 킬로미터 단위로 계산합니다.
    """
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_tagged_activity_places(
    location: str,
    keywords: List[str],
    radius: int = 5000
) -> List[Dict[str, Optional[str]]]:
    """
    키워드를 기반으로 다양한 활동을 수행할 수 있는 장소를 찾아,
    각 장소에 일치하는 키워드로 태그를 지정합니다.

    Args:
        location (str): 검색할 장소 또는 도시의 이름.
        keywords (List[str]): 활동 관련 검색 키워드 목록(예: ['hiking', 'museums']).
        radius (int, optional): 검색 반경(미터). 기본값은 5000입니다.

    Returns:
        List[Dict[str, Optional[str]]]: 장소 목록. 각 장소는 다음을 포함하는 사전으로 표현됩니다:
            - 'tag' (str): 장소와 일치하는 키워드
            - 'name' (str): 장소의 이름
            - 'address' (str): 근처 또는 형식화된 주소
            - 'rating' (float): 평균 Google 평점 (선택 사항)
            - 'user_ratings_total' (int): 사용자 리뷰 수 (선택 사항)
    """
    api_key= "AIzaSyDIYtPK8wOIQIzAXvUURy97R4tAS_eLeEE"
    lat, lng = get_lat_lng(location)
    if lat is None or lng is None:
        return []

    all_results = []

    for keyword in keywords:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword,
            "key": api_key
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "OK":
            print(f"키워드 '{keyword}' - Places API 오류:", data.get("error_message", data["status"]))
            continue

        for place in data["results"]:
            all_results.append({
                "tag": keyword,
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total")
            })

    return all_results

def get_top_rated_hotels(
    lat: float, 
    lng: float, 
    radius: int = 2000
) -> List[Dict[str, Optional[float]]]:
    """
    주어진 위도와 경도 근처의 상위 10개 최고 평점 호텔 목록을 반환합니다.

    각 호텔은 다음을 포함합니다:
        - name
        - rating
        - user_ratings_total
        - address
        - price_level
        - distance_km

    Args:
        lat (float): 검색 중심의 위도
        lng (float): 검색 중심의 경도
        radius (int): 호텔 검색을 위한 반경(미터)

    Returns:
        호텔 정보가 담긴 사전 목록
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    api_key= "AIzaSyDIYtPK8wOIQIzAXvUURy97R4tAS_eLeEE"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "lodging",
        "key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] != "OK":
        print("Places API 오류:", data.get("error_message", data["status"]))
        return []

    rated_hotels = []
    for place in data["results"]:
        if "rating" in place and "geometry" in place:
            hotel_lat = place["geometry"]["location"]["lat"]
            hotel_lng = place["geometry"]["location"]["lng"]
            distance_km = round(haversine_distance(lat, lng, hotel_lat, hotel_lng), 2)

            rated_hotels.append({
                "name": place.get("name"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "address": place.get("vicinity"),
                "price_level": place.get("price_level"),
                "distance_km": distance_km
            })

    return sorted(
        rated_hotels,
        key=lambda x: (x["rating"], x["user_ratings_total"]),
        reverse=True
    )


# 에이전트 (Agents)
activities_expert = LlmAgent(
		name="activities_expert",
		model="gemini-2.0-flash",
		description="사용자가 주어진 도시나 위치에서 할 수 있는 흥미롭고 인기 있으며 독특한 활동과 경험을 제안하는 에이전트입니다.",
		instruction = ACTIVITY_AGENT_INSTRUCTION,
		tools=[get_lat_lng, get_tagged_activity_places,get_top_rated_hotels],
)


hotels_expert = LlmAgent(
		name="hotels_expert",
		model="gemini-2.0-flash",
		description="평점, 위치, 또는 예산과 같은 사용자 선호도에 따라 지정된 도시나 위치의 호텔을 제안하는 에이전트입니다.",
		instruction = HOTELS_AGENT_INSTRUCTION,
		tools=[get_lat_lng, get_top_rated_hotels, get_tagged_activity_places],
)

places_to_visit_expert = LlmAgent(
		name="places_to_visit_expert",
		model="gemini-2.0-flash",
		description="주어진 도시나 위치에서 방문하기 가장 좋은 장소를 제안하는 여행 가이드 에이전트입니다. 인기 있는 랜드마크, 문화 유적지, 자연 명소, 그리고 숨겨진 보석들을 섞어서 추천합니다.",
		instruction = PLACES_TO_VISIT_AGENT_INSTRUCTION,
		tools=[get_lat_lng, get_top_rated_hotels, get_tagged_activity_places],
)

root_agent = Agent(
    name="ai_travel_planner",
    model="gemini-2.0-flash",
    description=(
        "주어진 도시나 위치의 호텔 이용 가능 여부, 방문할 장소, 이동 수단, 그리고 할 수 있는 활동에 대한 질문에 답하는 에이전트입니다."
    ),
    instruction=MAIN_AGENT_INSTRUCTION,
    tools=[AgentTool(activities_expert),AgentTool(hotels_expert),AgentTool(places_to_visit_expert)],
    sub_agents=[activities_expert, hotels_expert, places_to_visit_expert]
)