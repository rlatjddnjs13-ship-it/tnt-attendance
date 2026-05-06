import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# 1. 구글 시트 연결 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# 2. 스프레드시트 열기
try:
    spreadsheet = client.open("출석부")
    sheet = spreadsheet.get_worksheet(0) 
except Exception as e:
    st.error(f"시트를 찾을 수 없습니다: {e}")

st.title("✅ T.N.T 출석 시스템")

name = st.text_input("이름을 입력하세요:")

if st.button("출석 체크"):
    if name:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 💡 [핵심 수정] 
            # 단순히 append_row를 쓰지 않고, 현재 데이터가 몇 줄인지 파악해서 
            # 그 다음 줄(next_row)에 강제로 데이터를 넣습니다.
            all_values = sheet.get_all_values()
            next_row = len(all_values) + 1
            
            # 특정 줄에 데이터를 리스트 형태로 넣습니다.
            sheet.insert_row([now, name], index=next_row, value_input_option='USER_ENTERED')
            
            st.success(f"🎊 {name}님, {next_row}번째 줄에 출석 완료! ({now})")
            st.balloons() 
        except Exception as e:
            st.error(f"기록 중 오류가 발생했습니다: {e}")
    else:
        st.error("이름을 입력해 주세요.")