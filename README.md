# 📰 삼천리 보도자료 게재 현황 추적 시스템

보도자료 배포 후 각 매체의 게재 현황을 추적하고 시각화하는 Streamlit 대시보드입니다.

## 🎯 주요 기능

- ✅ HTML에서 자동으로 매체명 추출
- ✅ 구글 시트에 날짜별 매트릭스 형태로 저장
- ✅ 매체별 게재율 통계
- ✅ 시각화 차트 제공

## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 구글 시트 설정
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 다운로드
3. `.streamlit/secrets.toml` 파일 생성 (이미 완료됨)
4. 구글 시트에 서비스 계정 이메일 추가:
   ```
   pr-sheet-access@pr-dashboard-485514.iam.gserviceaccount.com
   ```
   - 권한: **편집자**

### 3. 앱 실행
```bash
streamlit run pr_tracker_app.py
```

## 📊 사용 방법

### 보도자료 등록
1. 왼쪽 사이드바에서 **배포 날짜** 입력
2. **보도자료 제목** 입력
3. 모니스에서 받은 **HTML 전체**를 복사하여 붙여넣기
4. **등록하기** 버튼 클릭

### 현황 확인
- 메인 화면에서 매체별 게재 현황 확인
- 날짜별 컬럼에 'O' 표시로 게재 여부 확인
- 매체별 게재율 통계 및 차트 확인

## 📁 파일 구조

```
.
├── pr_tracker_app.py          # 메인 Streamlit 앱
├── requirements.txt           # Python 패키지 목록
├── .streamlit/
│   └── secrets.toml          # 구글 시트 연결 정보
└── README.md                 # 이 파일
```

## 🔧 구글 시트 구조

| 구분 | 매체명 | 1/23 | 1/24 | 1/25 | ... |
|------|--------|------|------|------|-----|
| 제목 |        | 보도자료 제목 1 | 보도자료 제목 2 | ... | ... |
|      | 가스신문 | O | | O | ... |
|      | 이투뉴스 | O | O | | ... |
|      | 조선일보 | O | | O | ... |

- **첫 행**: 보도자료 제목
- **이후 행**: 매체별 게재 현황 (O 표시)
- **날짜 컬럼**: 자동 생성

## 🛠️ HTML 형식

시스템이 인식하는 HTML 패턴:
```html
<span>(매체명 YYYY/MM/DD)</span>
```

예시:
```html
<span>(가스신문 2026/01/23)</span>
<span>(이투뉴스 2026/01/23)</span>
```

## ⚙️ 설정 파일

`.streamlit/secrets.toml` 구조:
```toml
[connections.gsheets]
spreadsheet = "구글 시트 ID"
type = "service_account"
project_id = "프로젝트 ID"
private_key = "비밀키"
client_email = "서비스 계정 이메일"
# ... 기타 인증 정보
```

## 📝 참고사항

- 구글 시트 URL: https://docs.google.com/spreadsheets/d/16PhsJzo4askm-8iT0tMuBjsLpTEegCRDFFl4AUng6Hg/edit
- 워크시트 이름: "2026년"
- HTML은 전체를 복사하여 붙여넣어야 합니다

## 🐛 트러블슈팅

### "권한이 없습니다" 오류
→ 구글 시트에 서비스 계정 이메일이 편집자 권한으로 추가되었는지 확인

### "매체를 찾을 수 없습니다" 오류
→ HTML 형식이 올바른지 확인 (매체명 YYYY/MM/DD 패턴)

### 시트 연결 오류
→ `.streamlit/secrets.toml` 파일이 올바르게 생성되었는지 확인

## 📧 문의

문제가 발생하면 GitHub 이슈를 등록해주세요.
