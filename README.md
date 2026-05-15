# Dashboard Hub

여러 대시보드와 업무용 웹페이지를 한 화면에서 이동할 수 있도록 만든 공유용 Streamlit 허브입니다.

현재 허브는 Google Sheets에 있는 링크 목록을 읽어 카드형 포털로 보여줍니다.

## 데이터 원본

Google Sheets에 아래 컬럼이 있으면 됩니다.

| 컬럼 | 설명 |
|---|---|
| `구분` | 카드 제목 |
| `설명` | 카드 설명 문구 |
| `url` 또는 `URL` | 클릭 시 이동할 주소 |

기본 연결 시트:

```text
https://docs.google.com/spreadsheets/d/1wbsGQ1s7r4-HS5PWdNHwVuaWP69H9iRrXuAt_np_mPY/edit?gid=0#gid=0
```

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8505
```

## Streamlit Cloud 배포

1. `dashboard-hub` 폴더를 별도 GitHub 저장소에 업로드합니다.
2. Streamlit Community Cloud에서 `New app`을 선택합니다.
3. 저장소를 연결하고 Main file path를 `app.py`로 지정합니다.
4. `App settings > Secrets`에 아래 값을 넣습니다.

```toml
DASHBOARD_HUB_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wbsGQ1s7r4-HS5PWdNHwVuaWP69H9iRrXuAt_np_mPY/edit?gid=0#gid=0"
```

선택적으로 비밀번호도 걸 수 있습니다.

```toml
DASHBOARD_HUB_PASSWORD = "공유용비밀번호"
```

## 운영 방법

- 새 대시보드를 추가할 때는 Google Sheets에 새 행을 추가하면 됩니다.
- 허브는 약 60초 캐시를 사용하므로, 시트 수정 후 조금 기다렸다가 새로고침하면 반영됩니다.
- 외부 공유 전에는 Google Sheets 파일 권한과 Streamlit 비밀번호 설정 여부를 함께 확인하는 것이 좋습니다.
