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
    "treemap": "",
    "hist": "",
    "scatter": "",
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
# 구역 2: 장르 안의 영화별 총 관객 (트리맵)
# ------------------------------------------------------------
st.divider()
st.header("② 장르 안의 영화별 총 관객")
st.write("큰 칸은 장르, 그 안의 작은 칸은 영화입니다. 칸이 클수록 총 관객이 많습니다. 칸에 마우스를 올려 보세요.")

tm = df.dropna(subset=["total_audi"]).copy()
tm = tm[tm["total_audi"] > 0]

# 장르마다 같은 색을 쓰기 위한 색 지정 (편수가 많은 장르부터 색을 배정)
genre_color = {
    g: WARM_COLORS[i % len(WARM_COLORS)] for i, g in enumerate(genre_counts["장르"])
}

genre_totals = tm.groupby("genre_main")["total_audi"].sum()

ids = [f"g:{g}" for g in genre_totals.index] + [f"m:{c}" for c in tm["movieCd"]]
labels = list(genre_totals.index) + tm["movieNm"].tolist()
parents = [""] * len(genre_totals) + [f"g:{g}" for g in tm["genre_main"]]
values = genre_totals.tolist() + tm["total_audi"].tolist()
colors = [genre_color[g] for g in genre_totals.index] + [
    genre_color[g] for g in tm["genre_main"]
]

fig2 = go.Figure(
    go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=1)),
        textinfo="label",
        hovertemplate="<b>%{label}</b><br>총 관객: %{value:,}명<extra></extra>",
    )
)
fig2.update_layout(height=650, margin=dict(t=20, b=20, l=20, r=20))
st.plotly_chart(fig2, use_container_width=True)

insight_box("treemap")

# ------------------------------------------------------------
# 구역 3: 총 관객 히스토그램
# ------------------------------------------------------------
st.divider()
st.header("③ 총 관객의 분포")
st.write("영화를 총 관객 10만 명 단위 구간으로 나누어, 각 구간에 영화가 몇 편 있는지 세었습니다.")

BIN = 100_000  # 구간 하나의 너비 (10만 명)

aud = df["total_audi"].dropna()
aud = aud[aud >= 0]

bin_idx = (aud // BIN).astype(int)
hist = bin_idx.value_counts().reindex(range(bin_idx.max() + 1), fill_value=0)

lo = hist.index * BIN // 10_000          # 구간 시작 (만 명)
hi = (hist.index + 1) * BIN // 10_000    # 구간 끝 (만 명)
range_text = [f"{a}~{b}만 명" for a, b in zip(lo, hi)]

fig3 = go.Figure(
    go.Bar(
        x=(lo + hi) / 2,
        y=hist.values,
        width=(hi - lo),
        marker=dict(color="#E4572E", line=dict(color="#FFFFFF", width=1)),
        customdata=range_text,
        hovertemplate="<b>%{customdata}</b><br>영화 %{y}편<extra></extra>",
    )
)
fig3.update_layout(
    height=450,
    bargap=0,
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="총 관객 (만 명)",
    yaxis_title="영화 편수",
)
st.plotly_chart(fig3, use_container_width=True)

# 대부분의 영화가 몰린 구간 / 관객이 가장 많은 영화
peak_bin = hist.idxmax()
peak_count = int(hist.max())
peak_share = peak_count / len(aud) * 100
top_movie = df.loc[df["total_audi"].idxmax()]

st.success(
    f"📌 대부분의 영화는 **{range_text[peak_bin]}** 구간에 몰려 있습니다. "
    f"({peak_count}편, 전체의 {peak_share:.1f}%)\n\n"
    f"🏆 총 관객이 가장 많은 영화는 **{top_movie['movieNm']}**입니다. "
    f"({int(top_movie['total_audi']):,}명)"
)

insight_box("hist")

# ------------------------------------------------------------
# 구역 4: 첫 관측일 스크린 수와 총 관객 (산점도)
# ------------------------------------------------------------
st.divider()
st.header("④ 스크린 수와 총 관객의 관계")
st.write(
    "점 하나가 영화 한 편입니다. 가로는 첫 관측일 스크린 수, 세로는 총 관객이고, "
    "점 색은 장르를 뜻합니다. 점에 마우스를 올려 보세요."
)

sc = df.dropna(subset=["first_scrn", "total_audi"])

use_log = st.checkbox("총 관객 축을 로그 눈금으로 보기 (관객 수 차이가 큰 영화를 함께 보기 좋습니다)")

fig4 = go.Figure()
for g in genre_counts["장르"]:  # 편수가 많은 장르부터 (도넛 그래프와 같은 색)
    part = sc[sc["genre_main"] == g]
    if part.empty:
        continue
    fig4.add_trace(
        go.Scatter(
            x=part["first_scrn"],
            y=part["total_audi"],
            mode="markers",
            name=g,
            marker=dict(
                color=genre_color[g],
                size=9,
                opacity=0.85,
                line=dict(color="#FFFFFF", width=0.5),
            ),
            customdata=part[["movieNm", "genre_main"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "장르: %{customdata[1]}<br>"
                "첫 관측일 스크린 수: %{x:,}개<br>"
                "총 관객: %{y:,}명<extra></extra>"
            ),
        )
    )
fig4.update_layout(
    height=600,
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis_title="첫 관측일 스크린 수 (개)",
    yaxis_title="총 관객 (명)",
    legend_title_text="장르",
)
fig4.update_yaxes(type="log" if use_log else "linear")
st.plotly_chart(fig4, use_container_width=True)

insight_box("scatter")

# ------------------------------------------------------------
# 다음 구역이 들어올 자리
# ------------------------------------------------------------
# st.divider()
# st.header("⑤ ...")
