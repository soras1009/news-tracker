import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import requests
import time

# 페이지 설정
st.set_page_config(page_title="삼천리 보도자료 게재 현황", layout="wide")

# 구글 시트 연결
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"구글 시트 연결 초기화 오류: {e}")
    conn = None

SHEET_NAME = "2026년"

st.title("📰 보도자료 게재 현황 추적 시스템")

# 네이버 뉴스 자동 검색 함수
def search_naver_news(title):
    """제목으로 네이버 뉴스를 자동 검색하여 매체명 추출"""
    media_set = set()
    
    if not title or not title.strip():
        return media_set
    
    try:
        # 네이버 뉴스 검색 URL
        search_url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={title}"
        
        # User-Agent 헤더 추가 (차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 네이버 검색 요청
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 뉴스 기사 항목 찾기
        # 네이버 뉴스 검색 결과의 언론사명은 여러 패턴으로 나타남
        
        # 패턴 1: news_tit 클래스 근처의 정보원
        news_items = soup.find_all('div', class_='news_area')
        for item in news_items:
            # 언론사명 찾기
            press = item.find('a', class_='info press')
            if press:
                media_name = press.get_text().strip()
                if media_name:
                    media_set.add(media_name)
        
        # 패턴 2: API 뉴스 항목
        api_items = soup.find_all('div', class_='api_subject_bx')
        for item in api_items:
            press = item.find('a', class_='press')
            if press:
                media_name = press.get_text().strip()
                if media_name:
                    media_set.add(media_name)
        
        # 딜레이 추가 (네이버 차단 방지)
        time.sleep(0.5)
        
    except requests.exceptions.RequestException as e:
        st.warning(f"네이버 검색 중 오류 발생: {e}")
    except Exception as e:
        st.warning(f"매체 추출 중 오류 발생: {e}")
    
    return media_set

# 텍스트에서 매체명 추출하는 함수
def extract_media_from_text(text):
    """텍스트에서 (매체명 YYYY/MM/DD) 패턴 추출"""
    media_set = set()
    
    if not text or not text.strip():
        return media_set
    
    # 패턴: (매체명 YYYY/MM/DD)
    matches = re.findall(r'\(([^)]+)\s+\d{4}/\d{2}/\d{2}\)', text)
    for match in matches:
        media_name = match.strip()
        if media_name:
            media_set.add(media_name)
    
    return media_set

# 사이드바: 데이터 입력
with st.sidebar:
    st.header("📝 새 보도자료 등록")
    
    # 날짜 입력
    doc_date = st.date_input("배포 날짜", datetime.now())
    date_str = doc_date.strftime("%m/%d")  # 예: "01/23"
    
    # 제목 입력
    doc_title = st.text_input("보도자료 제목", placeholder="예: 삼천리EV 송지아 BYD 차량 후원")
    
    st.divider()
    
    # 텍스트 입력 (모니스 등에서 받은 텍스트)
    st.subheader("📋 게재 매체 텍스트")
    st.caption("모니스 등에서 받은 게재 매체 목록을 붙여넣으세요")
    
    media_text = st.text_area(
        "매체 텍스트 붙여넣기",
        height=300,
        placeholder="""예시:
삼천리EV 송지아... (한국경제 2026/01/06)
삼천리EV 송지아... (이투뉴스 2026/01/06)
삼천리EV 송지아... (에너지신문 2026/01/06)
...""",
        help="(매체명 YYYY/MM/DD) 형태의 텍스트를 붙여넣으면 자동으로 매체명을 추출합니다"
    )
    
    # 네이버 자동 검색 옵션
    auto_search_naver = st.checkbox(
        "네이버 뉴스 자동 검색",
        value=True,
        help="체크하면 제목으로 네이버를 자동 검색하여 추가 매체를 찾습니다"
    )
    
    # 제출 버튼
    submit = st.button("🚀 등록하기", type="primary")

# 데이터 처리
if submit:
    if not doc_title:
        st.error("⚠️ 보도자료 제목을 입력해주세요.")
    elif not media_text and not auto_search_naver:
        st.error("⚠️ 매체 텍스트를 입력하거나 네이버 자동 검색을 활성화해주세요.")
    else:
        try:
            with st.spinner("데이터 분석 중..."):
                found_media = set()
                
                # 1. 텍스트에서 매체명 추출
                if media_text:
                    with st.spinner("텍스트 분석 중..."):
                        text_media = extract_media_from_text(media_text)
                        
                        if text_media:
                            found_media.update(text_media)
                            st.success(f"✅ 입력 텍스트에서 {len(text_media)}개 매체 발견!")
                        else:
                            st.warning("⚠️ 입력 텍스트에서 매체를 찾지 못했습니다.")
                
                # 2. 네이버 자동 검색
                naver_media = set()
                if auto_search_naver:
                    with st.spinner(f"🔍 네이버에서 '{doc_title}' 검색 중..."):
                        naver_media = search_naver_news(doc_title)
                        
                        if naver_media:
                            st.success(f"✅ 네이버 자동 검색에서 {len(naver_media)}개 매체 발견!")
                            
                            # 텍스트와 네이버 검색 결과 비교
                            if media_text and found_media:
                                text_only = found_media - naver_media
                                naver_only = naver_media - found_media
                                both = found_media & naver_media
                                
                                # 합치기
                                found_media.update(naver_media)
                                
                                # 비교 결과 표시
                                with st.expander("🔍 매체 추출 결과 비교"):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("텍스트 전용", len(text_only))
                                        if text_only:
                                            for m in sorted(text_only):
                                                st.caption(f"• {m}")
                                    with col2:
                                        st.metric("네이버 전용 (추가 발견)", len(naver_only))
                                        if naver_only:
                                            for m in sorted(naver_only):
                                                st.caption(f"• {m}")
                                    with col3:
                                        st.metric("중복 (확인됨)", len(both))
                            else:
                                # 네이버 검색 결과만 사용
                                found_media.update(naver_media)
                        else:
                            st.warning("⚠️ 네이버 검색에서 매체를 찾지 못했습니다.")
                
                if not found_media:
                    st.warning("⚠️ 매체 정보를 찾지 못했습니다. 텍스트 형식을 확인하거나 네이버 검색을 활성화해주세요.")
                else:
                    
                    # 기존 시트 데이터 읽기
                    try:
                        df = conn.read(worksheet=SHEET_NAME)
                        # 빈 값 처리
                        df = df.fillna("")
                        
                        # 완전히 빈 행 제거
                        df = df.loc[~(df == "").all(axis=1)]
                        
                        if df.empty or len(df.columns) < 2:
                            # 빈 시트인 경우 초기 구조 생성
                            df = pd.DataFrame(columns=["구분", "매체명"])
                    except Exception as e:
                        st.warning(f"시트를 처음 만듭니다: {e}")
                        df = pd.DataFrame(columns=["구분", "매체명"])
                    
                    # 날짜 컬럼이 없으면 추가
                    if date_str not in df.columns:
                        df[date_str] = ""
                    
                    # 제목 행 처리
                    title_row_idx = None
                    if len(df) > 0 and "구분" in df.columns:
                        title_mask = df["구분"] == "제목"
                        if title_mask.any():
                            title_row_idx = df[title_mask].index[0]
                            df.loc[title_row_idx, date_str] = doc_title
                        else:
                            # 제목 행 추가
                            title_data = {"구분": "제목", "매체명": ""}
                            for col in df.columns:
                                if col not in ["구분", "매체명"]:
                                    title_data[col] = ""
                            title_data[date_str] = doc_title
                            title_row = pd.DataFrame([title_data])
                            df = pd.concat([title_row, df], ignore_index=True)
                            title_row_idx = 0
                    else:
                        # 완전히 새로운 시트
                        title_data = {"구분": "제목", "매체명": "", date_str: doc_title}
                        df = pd.DataFrame([title_data])
                        title_row_idx = 0
                    
                    # 각 매체에 대해 O 표시
                    for media in found_media:
                        # 매체가 시트에 없으면 추가
                        media_exists = False
                        if "매체명" in df.columns:
                            media_mask = (df["매체명"] == media) & (df["구분"] != "제목")
                            if media_mask.any():
                                # 기존 매체에 O 표시
                                media_idx = df[media_mask].index[0]
                                df.loc[media_idx, date_str] = "O"
                                media_exists = True
                        
                        if not media_exists:
                            # 새 매체 추가
                            new_data = {"구분": "", "매체명": media}
                            for col in df.columns:
                                if col not in ["구분", "매체명"]:
                                    new_data[col] = ""
                            new_data[date_str] = "O"
                            new_row = pd.DataFrame([new_data])
                            df = pd.concat([df, new_row], ignore_index=True)
                    
                    # 구글 시트에 업데이트
                    conn.update(worksheet=SHEET_NAME, data=df)
                    
                    st.success(f"✅ 등록 완료! {len(found_media)}개 매체가 {date_str} 컬럼에 표시되었습니다.")
                    st.balloons()
                    
                    # 발견된 매체 목록 표시
                    with st.expander("📋 등록된 매체 목록"):
                        for media in sorted(found_media):
                            st.write(f"- {media}")
                    
        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {e}")
            import traceback
            st.code(traceback.format_exc())

# 메인 화면: 현황 표시
st.divider()
st.subheader("📊 2026년 보도자료 게재 현황")

try:
    # 구글 시트에서 데이터 읽기
    if conn is None:
        st.error("구글 시트 연결이 초기화되지 않았습니다. Secrets 설정을 확인해주세요.")
    else:
        df = conn.read(worksheet=SHEET_NAME)
    
        if not df.empty and len(df.columns) >= 2:
        # 데이터 표시
        st.dataframe(
            df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        # 통계 정보
        date_columns = [col for col in df.columns if col not in ["구분", "매체명"]]
        if date_columns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 보도자료 수", len(date_columns))
            
            with col2:
                total_media = len(df[df["매체명"].notna() & (df["매체명"] != "")])
                st.metric("등록된 매체 수", total_media)
            
            with col3:
                # 총 게재 건수 (O의 개수)
                total_coverage = 0
                for col in date_columns:
                    if col in df.columns:
                        total_coverage += (df[col] == "O").sum()
                st.metric("총 게재 건수", total_coverage)
        
        # 매체별 게재율
        st.divider()
        st.subheader("📈 매체별 게재 성과")
        
        if date_columns:
            # 매체별 게재 횟수 계산
            media_stats = []
            for idx, row in df.iterrows():
                if row["매체명"] and row["구분"] != "제목":
                    media_name = row["매체명"]
                    coverage_count = sum([1 for col in date_columns if col in row and row[col] == "O"])
                    coverage_rate = (coverage_count / len(date_columns) * 100) if len(date_columns) > 0 else 0
                    media_stats.append({
                        "매체명": media_name,
                        "게재 건수": coverage_count,
                        "게재율": f"{coverage_rate:.1f}%"
                    })
            
            if media_stats:
                stats_df = pd.DataFrame(media_stats)
                stats_df = stats_df.sort_values("게재 건수", ascending=False).reset_index(drop=True)
                
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.dataframe(stats_df, hide_index=True, height=400)
                
                with col2:
                    # 상위 10개 매체 차트
                    if len(stats_df) > 0:
                        import plotly.express as px
                        top_10 = stats_df.head(10)
                        fig = px.bar(
                            top_10,
                            x="게재 건수",
                            y="매체명",
                            orientation='h',
                            title="상위 10개 매체 게재 현황",
                            color="게재 건수",
                            color_continuous_scale="Blues"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 아직 등록된 데이터가 없습니다. 왼쪽 사이드바에서 첫 보도자료를 등록해보세요!")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(f"상세 오류: {str(e)}")
    st.info("구글 시트 권한을 확인해주세요.")
    
    # 디버깅 정보
    with st.expander("🔍 디버깅 정보"):
        st.write(f"오류 타입: {type(e).__name__}")
        st.write(f"오류 내용: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# 사용 안내
with st.expander("ℹ️ 사용 방법"):
    st.markdown("""
    ### 📖 사용 가이드
    
    #### 1. 구글 시트 권한 설정 (최초 1회)
       - 시트에 `pr-sheet-access@pr-dashboard-485514.iam.gserviceaccount.com` 이메일 추가
       - 권한: 편집자
    
    #### 2. 보도자료 등록
       **방법 A: 텍스트 + 네이버 자동 검색 (권장 ⭐)**
       - 배포 날짜 입력
       - 보도자료 제목 입력
       - 모니스 등에서 받은 매체 목록 텍스트 붙여넣기
       - "네이버 뉴스 자동 검색" 체크 (기본 활성화)
       - "등록하기" 버튼 클릭
       - ✨ 네이버에서 자동으로 추가 매체를 찾아줍니다!
       
       **방법 B: 텍스트만 사용**
       - 날짜, 제목 입력
       - 매체 목록 텍스트 붙여넣기
       - "네이버 뉴스 자동 검색" 체크 해제
       - 등록하기
       
       **방법 C: 네이버 자동 검색만 사용**
       - 날짜, 제목만 입력
       - "네이버 뉴스 자동 검색" 체크
       - 등록하기
       - 🔍 네이버에서 자동으로 모든 매체를 찾아줍니다!
    
    #### 3. 현황 확인
       - 메인 화면에서 매체별 게재 현황 확인
       - 날짜별로 O 표시된 매체 확인
       - 매체별 게재율 통계 확인
    
    ### 💡 팁
    - 텍스트 형식: `기사 제목... (매체명 YYYY/MM/DD)`
    - 네이버 자동 검색으로 누락된 매체도 찾습니다
    - 둘 다 사용하면 가장 정확합니다
    - **완전 무료입니다!** 별도 API 비용 없음
    
    ### 📋 텍스트 형식 예시
    ```
    삼천리EV 송지아... (한국경제 2026/01/06)
    삼천리EV 송지아... (이투뉴스 2026/01/06)
    삼천리EV 송지아... (에너지신문 2026/01/06)
    ```
    
    ### 🔍 네이버 자동 검색 작동 방식
    1. 입력한 제목으로 네이버 뉴스 검색
    2. 검색 결과에서 매체명 자동 추출
    3. 입력 텍스트와 합쳐서 등록
    4. 누락된 매체 자동 발견!
    """)



