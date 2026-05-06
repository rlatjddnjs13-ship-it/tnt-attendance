import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from streamlit_js_eval import get_geolocation
import math

# ---------------------------------------------------------
# 1. 학교 위치 설정 (명지대 제5공학관 좌표 적용)
# ---------------------------------------------------------
TARGET_LAT = 37.221989  # 위도
TARGET_LON = 127.187619 # 경도
ALLOWED_DISTANCE = 0.2  # 허용 거리 200m (0.2km)

# 두 지점 사이의 거리를 계산하는 함수 (하버사인 공식)
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371 # 지구 반지름(km)
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ---------------------------------------------------------
# 2. 구글 시트 연결 (Secrets 방식)
# ---------------------------------------------------------
def login_google_sheet():
    try:
        # Streamlit Settings -> Secrets에 넣은 정보를 가져옵니다.
        creds_info = dict(st.secrets)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        # 구글 시트 파일 이름이 "출석부"여야 합니다.
        return client.open("출석부").get_worksheet(0)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        st.info("Streamlit Settings -> Secrets에 creds.json 내용을 넣었는지 확인하세요.")
        return None

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.set_page_config(page_title="TNT 출석 체크", page_icon="📍")
st.title("📍 T.N.T GPS 출석 시스템")

sheet = login_google_sheet()

if sheet:
    st.info("정확한 출석을 위해 GPS 정보가 필요합니다. 브라우저 상단의 '위치 권한 허용'을 눌러주세요.")
    
    # GPS 정보 가져오기
    loc = get_geolocation()

    if loc:
        curr_lat = loc['coords']['latitude']
        curr_lon = loc['coords']['longitude']
        
        # 학교와의 거리 계산
        dist = get_distance(curr_lat, curr_lon, TARGET_LAT, TARGET_LON)
        dist_m = dist * 1000 # m 단위로 변환
        
        st.write(f"📡 현재 위치 확인됨")
        
        if dist <= ALLOWED_DISTANCE:
            st.success(f"✅ 출석 가능 지역입니다! (목적지까지 약 {dist_m:.0f}m)")
            
            name = st.text_input("본인의 이름을 입력하세요:")
            
            if st.button("출석 완료 버튼 누르기"):
                if name:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # 시트에 [시간, 이름, 위도, 경도, 거리] 순으로 기록
                    try:
                        sheet.append_row([now, name, curr_lat, curr_lon, f"{dist_m:.0f}m"])
                        st.success(f"🎊 {name}님, 출석이 정상적으로 기록되었습니다!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"기록 중 오류 발생: {e}")
                else:
                    st.warning("이름을 입력해 주세요.")
        else:
            st.error(f"❌ 출석 불가 지역입니다.")
            st.warning(f"현재 지정된 위치에서 약 {dist:.2f}km 떨어져 있습니다. 제5공학관 근처로 이동해 주세요.")
    else:
        st.warning("위치 정보를 불러오는 중입니다... 잠시만 기다려주시거나 페이지를 새로고침 해주세요.")