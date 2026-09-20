import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)

# 따뜻한 색 팔레트
WARM_COLORS = [
    "#E4572E", "#F3A712", "#A8C686", "#669BBC", "#C97B84",
    "#8C5E58", "#F6C28B", "#7D8CC4", "#D1603D", "#B5A886",
    "#DDA15E", "#BC6C25",
]


# ------------------------------------------------------------
# 데이터 불러오기
# ------------------------------------------------------------
@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자(예: 20250115) -> 진짜 날짜
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str).str.zfill(8), format="%Y%m%d", errors="coerce"
    )

    # 장르: 세로막대(|)로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre_main"] = (
        df["genre"].fillna("미분류").astype(str).str.split("|").str[0].str.strip()
    )
    df.loc[df["genre_main"] == "", "genre_main"] = "미분류"
    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결이나 주소를 확인해 주세요.")
    st.exception(e)
    st.stop()


# ------------------------------------------------------------
# '이 그래프로 알 수 있는 것' 입력칸 (그래프마다 재사용)
# ------------------------------------------------------------
# 앱 화면에서 바로 적을 수 있고, 아래 INSIGHTS에 미리 적어 두면 처음부터 채워져 있습니다.
INSIGHTS = {
    "genre": "",
}


def insight_box(key: str):
    text = st.text_input(
        "✏️ 이 그래프로 알 수 있는 것 (한 문장)",
        value=INSIGHTS.get(key, ""),
        key=f"insight_{key}",
        placeholder="여기에 한 문장을 적고 Enter를 누르세요.",
    )
    if text.strip():
        st.info(f"**이 그래프로 알 수 있는 것:** {text.strip()}")


# ------------------------------------------------------------
# 제목
# ------------------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    f"1년간 박스오피스 10위권에 든 영화 중 이 기간에 개봉한 {len(df)}편의 요약표를 그래프로 살펴봅니다."
)

# ------------------------------------------------------------
# 구역 1: 장르별 영화 편수 (도넛)
# ------------------------------------------------------------
st.divider()
st.header("① 장르별 영화 편수")
st.write("영화마다 첫 번째로 적힌 장르를 기준으로 묶었습니다. 조각에 마우스를 올려 보세요.")

genre_counts = (
    df["genre_main"].value_counts().rename_axis("장르").reset_index(name="편수")
)

fig1 = go.Figure(
    go.Pie(
        labels=genre_counts["장르"],
        values=genre_counts["편수"],
        hole=0.5,
        sort=False,
        marker=dict(colors=WARM_COLORS, line=dict(color="#FFFFFF", width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
    )
)
fig1.update_layout(
    height=500,
    margin=dict(t=20, b=20, l=20, r=20),
    legend_title_text="장르",
    annotations=[
        dict(
            text=f"총 {len(df)}편",
            x=0.5, y=0.5, font_size=22, showarrow=False,
        )
    ],
)
st.plotly_chart(fig1, use_container_width=True)

insight_box("genre")

# ------------------------------------------------------------
# 다음 구역이 들어올 자리
# ------------------------------------------------------------
# st.divider()
# st.header("② ...")
