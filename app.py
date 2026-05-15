from __future__ import annotations

import hmac
import os
import re
import urllib.parse
from html import escape

import pandas as pd
import streamlit as st

DEFAULT_LINK_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1wbsGQ1s7r4-HS5PWdNHwVuaWP69H9iRrXuAt_np_mPY/edit?gid=0#gid=0"
)
SHEET_SECRET_KEY = "DASHBOARD_HUB_SHEET_URL"
PASSWORD_SECRET_KEY = "DASHBOARD_HUB_PASSWORD"

st.set_page_config(page_title="Dashboard Hub", layout="wide")


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700;800;900&display=swap');

        :root {
            --bg: #111827;
            --panel: #202842;
            --panel2: #263252;
            --panel3: #2b3760;
            --text: #f4f7ff;
            --muted: #aab6d4;
            --teal: #2db6c2;
            --cyan: #54a8e6;
            --ink: #1b2340;
            --indigo: #2f3d78;
            --indigo2: #37498e;
            --amber: #e5c15a;
        }

        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans KR', 'Segoe UI', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 4%, rgba(36, 198, 208, 0.15), transparent 30rem),
                radial-gradient(circle at 92% 8%, rgba(74, 184, 255, 0.12), transparent 32rem),
                var(--bg);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(16, 24, 39, 0.72);
            backdrop-filter: blur(14px);
        }

        .block-container {
            max-width: 1540px;
            padding-top: 1.6rem;
            padding-bottom: 3.5rem;
        }

        .hero {
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-left: 5px solid var(--teal);
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent 40%),
                linear-gradient(120deg, rgba(28, 37, 56, 0.96), rgba(25, 34, 52, 0.86));
            padding: 1.5rem 1.7rem;
            margin-bottom: 1.4rem;
            box-shadow: 0 22px 55px rgba(0, 0, 0, 0.24);
        }

        .kicker {
            color: var(--teal);
            font-size: 0.8rem;
            font-weight: 900;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .title {
            color: var(--text);
            font-size: clamp(2rem, 5vw, 4.15rem);
            font-weight: 900;
            letter-spacing: -0.06em;
            line-height: 1.05;
            margin-top: 0.38rem;
        }

        .subtitle {
            color: var(--muted);
            font-size: 1rem;
            margin-top: 0.75rem;
        }

        .hub-card {
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            min-height: 300px;
            padding: 1.15rem 1.05rem 1.05rem 1.05rem;
            text-decoration: none !important;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.05), transparent 42%),
                linear-gradient(145deg, rgba(78, 102, 168, 0.20), rgba(34, 46, 82, 0.08) 58%, rgba(17, 24, 39, 0.10)),
                var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 18px;
            color: var(--text) !important;
            transition: transform 160ms ease, border-color 160ms ease, background 160ms ease, box-shadow 160ms ease;
            box-shadow:
                0 18px 38px rgba(0, 0, 0, 0.20),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .hub-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.07), transparent 28%);
            pointer-events: none;
        }

        .hub-card::after {
            content: "";
            position: absolute;
            left: 1rem;
            right: 1rem;
            top: 0;
            height: 3px;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(45, 182, 194, 0.85), rgba(84, 168, 230, 0.45), transparent 90%);
            opacity: 0.9;
            pointer-events: none;
        }

        .hub-card:hover {
            transform: translateY(-4px);
            border-color: rgba(84, 168, 230, 0.42);
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.07), transparent 42%),
                linear-gradient(145deg, rgba(84, 168, 230, 0.20), rgba(47, 61, 120, 0.12) 58%, rgba(17, 24, 39, 0.12)),
                var(--panel2);
            box-shadow:
                0 24px 46px rgba(0, 0, 0, 0.24),
                inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }

        .card-title {
            position: relative;
            z-index: 1;
            color: var(--text);
            font-size: 1.62rem;
            font-weight: 850;
            letter-spacing: -0.03em;
            line-height: 1.22;
            margin: 0.35rem 0 1rem 0;
            word-break: keep-all;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 4.1rem;
            text-align: center;
        }

        .card-body {
            position: relative;
            z-index: 1;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 1rem;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.995), rgba(246, 248, 255, 0.97));
            border-radius: 14px;
            padding: 1rem 1rem 0.95rem 1rem;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.92),
                0 10px 22px rgba(9, 15, 32, 0.16);
        }

        .card-description {
            color: #151922;
            font-size: 1rem;
            line-height: 1.36;
            font-weight: 600;
            letter-spacing: -0.02em;
            word-break: keep-all;
            overflow-wrap: anywhere;
            display: -webkit-box;
            -webkit-line-clamp: 5;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55);
        }

        .card-cta {
            display: inline-block;
            color: #f5f7ff;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.10), transparent 34%),
                linear-gradient(135deg, var(--indigo2), var(--indigo));
            padding: 0.82rem 0.9rem;
            border-radius: 999px;
            font-size: 0.98rem;
            font-weight: 850;
            align-self: center;
            min-width: 100%;
            text-align: center;
            border: 1px solid rgba(31, 42, 86, 0.45);
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.14),
                0 10px 18px rgba(33, 44, 91, 0.22);
            text-shadow: 0 1px 0 rgba(17, 24, 39, 0.26);
        }

        .soft-note {
            color: var(--muted);
            background: rgba(28, 37, 56, 0.72);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.85rem 1rem;
            margin: 0.3rem 0 1.15rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret_or_env(key: str) -> str | None:
    if key in os.environ:
        return os.environ[key].strip() or None
    try:
        value = st.secrets[key]
        return str(value).strip() or None
    except Exception:
        return None


def get_sheet_url() -> str:
    return get_secret_or_env(SHEET_SECRET_KEY) or DEFAULT_LINK_SHEET_URL


def extract_sheet_parts(sheet_url: str) -> tuple[str | None, str | None]:
    sheet_id_match = re.search(r"/d/([^/]+)", sheet_url)
    gid_match = re.search(r"[?#&]gid=(\d+)", sheet_url)
    sheet_id = sheet_id_match.group(1) if sheet_id_match else None
    gid = gid_match.group(1) if gid_match else "0"
    return sheet_id, gid


@st.cache_data(ttl=60)
def load_links(sheet_url: str) -> pd.DataFrame:
    sheet_id, gid = extract_sheet_parts(sheet_url)
    if not sheet_id:
        raise ValueError("유효한 Google Sheets URL이 아닙니다.")
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={urllib.parse.quote(gid or '0')}"
    df = pd.read_csv(csv_url)
    df.columns = [str(column).strip() for column in df.columns]

    title_col = next((column for column in df.columns if column.strip().lower() == "구분"), None)
    desc_col = next((column for column in df.columns if column.strip() == "설명"), None)
    url_col = next((column for column in df.columns if column.strip().lower() == "url"), None)
    if not title_col or not url_col:
        raise ValueError("시트에는 `구분`과 `url` 컬럼이 필요합니다.")

    selected_columns = [title_col, url_col]
    if desc_col:
        selected_columns.insert(1, desc_col)
    rename_map = {title_col: "구분", url_col: "url"}
    if desc_col:
        rename_map[desc_col] = "설명"
    links = df[selected_columns].rename(columns=rename_map)
    links = links.dropna(subset=["구분", "url"])
    links["구분"] = links["구분"].astype(str).str.strip()
    if "설명" in links.columns:
        links["설명"] = links["설명"].fillna("").astype(str).str.strip()
    else:
        links["설명"] = ""
    links["url"] = links["url"].astype(str).str.strip()
    links = links[(links["구분"] != "") & (links["url"] != "")]
    return links.reset_index(drop=True)


def check_password() -> bool:
    password = get_secret_or_env(PASSWORD_SECRET_KEY)
    if not password:
        return True
    if st.session_state.get("hub_password_ok"):
        return True

    render_hero("Protected Dashboard Hub", "부문 웹서비스 허브에 접근하려면 비밀번호를 입력해주세요.")
    entered = st.text_input("비밀번호", type="password")
    if st.button("입장", type="primary"):
        if hmac.compare_digest(entered, password):
            st.session_state["hub_password_ok"] = True
            st.rerun()
        else:
            st.error("비밀번호가 맞지 않습니다.")
    return False


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="kicker">DASHBOARD HUB</div>
            <div class="title">{escape(title)}</div>
            <div class="subtitle">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_card_title(raw_title: str) -> str:
    title = str(raw_title).strip()
    if title == "공공조달 사업 통합 검색":
        title = "공공조달 사업\n통합 검색"
    return escape(title).replace("\n", "<br>")


def render_cards(links: pd.DataFrame) -> None:
    if links.empty:
        st.info("표시할 링크가 없습니다. Google Sheets에 `구분`, `url` 값을 추가해주세요.")
        return

    records = links.to_dict("records")
    for start in range(0, len(records), 5):
        row_columns = st.columns(5)
        row_records = records[start : start + 5]
        for index, row in enumerate(row_records):
            title = format_card_title(row["구분"])
            description = escape(str(row.get("설명", "")))
            url = escape(str(row["url"]), quote=True)
            with row_columns[index]:
                st.markdown(
                    f"""
                    <a class="hub-card" href="{url}" target="_blank" rel="noopener noreferrer">
                        <div class="card-title">{title}</div>
                        <div class="card-body">
                            <div class="card-description">{description}</div>
                            <div class="card-cta">바로가기</div>
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
        if start + 5 < len(records):
            st.markdown("<div style='height: 1.35rem;'></div>", unsafe_allow_html=True)


def main() -> None:
    inject_css()
    if not check_password():
        return

    render_hero("대시보드 허브", "조달시장 대시보드, 지자체 히스토리 등 시장과 고객관련 주요 대시보드를 한곳에서 이동합니다")
    sheet_url = get_sheet_url()
    try:
        links = load_links(sheet_url)
    except Exception as exc:
        st.error(f"링크 시트를 불러오지 못했습니다: {exc}")
        st.stop()

    st.markdown(f"<div class='soft-note'>총 <b>{len(links)}</b>개 서비스가 연결되어 있습니다.</div>", unsafe_allow_html=True)
    render_cards(links)


if __name__ == "__main__":
    main()
