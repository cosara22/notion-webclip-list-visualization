import streamlit as st # Anaconda環境の方は別途インストールが推奨。conda install -c conda-forge streamlit 
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# import japanize_matplotlib # 日本語表示のため Python 3.12以降だと動かない
import matplotlib_fontja # 日本語表示のため
from janome.tokenizer import Tokenizer
import os
from dotenv import load_dotenv
from notion_client import Client
import plotly.express as px

# 環境変数のロード
load_dotenv()
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

# Notion APIクライアントを初期化
notion = Client(auth = NOTION_API_KEY)

# クエリを作成してデータを取得、データフレームに変換
query = notion.databases.query(database_id = DATABASE_ID)
df = pd.DataFrame(query["result"])

# データ加工用の関数定義
def extract_property_value(row,property_name, sub_property=None):
    prop = row["properties"].get(property_name,{})
    if sub_property and isinstance(prop, dict):
        return prop.get(sub_property,{}).get("name",None)
    return None

# Pltlyのダークテーマを設定
px.defaults.template = "plotly_dark"

# アプリケーションのタイトル設定とスタイル調整
st.title("WebClip List Visualization")
st.markdown(
    """
    <style>
    .big-font {
    font-size:20px !important;
    }
    </style>
    """,
    unsafe_allow_html = True,
)

# 2行2列のグリッドレイアウトを作成
grid = [[None,None], [None,None]]
font_path = 'fonts/ヒラギノ明朝 ProN.ttc' # フォントパスを指定

# データの可視化
# 単語クラウドの表示
titles = " ".join([row["properties"]["記事タイトル"]["title"][0]["plain_text"] 
                   for _, row in df.iterrows()]
                   )
wordcloud = WordCloud(
    width=400, 
    height=200, 
    background_color='black', 
    font_path=font_path
    ).generate(titles)
fig, ax =plt.subplots(figsize=(5, 3))
ax.imshow(wordcloud, interpolation="billinear")
ax.axis("off")
grid[0][0] = fig

""" # ステータス別の円グラフ
status_counts = df.apply(
    lambda row:
        extract_property_value(row, "ステータス", "status"), 
        axis=1
    ).value_counts()
fig = px.pie(
    values=status_counts.values, 
    names=status_counts.index, 
    title="<b>ステータス別分布</b>"
    )
grid[0][1] = fig """

# wiki分類別の分布
category_counts = df.apply(
    lambda row:
        ', '.join([x["name"]
            for x in row["properties"].get("wiki分類", {}).get("relation", []) 
            if x]
            ), 
        axis=1
    ).value_counts()
fig = px.bar(
    x=category_counts.index, 
    y=category_counts.values, 
    labels={'x': "<b>wiki分類</b>", 'y': "<b>件数</b>"}, title="<b>wiki分類別の件数</b>")
grid[1][0] = fig

""" # 小分類別の分布
category_counts = df.apply(
    lambda row:
        ', '.join([x["name"]
            for x in row["properties"].get("小分類", {}).get("multi_select", []) 
            if x]
            ), 
        axis=1
    ).value_counts()
fig = px.bar(
    x=category_counts.index, 
    y=category_counts.values, 
    labels={'x': "<b>小分類</b>", 'y': "<b>件数</b>"}, title="<b>小分類別の件数</b>")
grid[1][1] = fig """

# グラフの表示
for row in grid:
    cols = st.columns(2)
    with cols[0]:
        if row[0] is not None:
            # matplotlibの図の場合
            if isinstance(row[0], plt.figure):
                st.pyplot(row[0])
            # plotlyの図の場合
            else:
                st.plotly_chart(row[0], use_container_width=True)
    with cols[1]:
        if row[1] is not None:
            st.plotly_chart(row[1],use_container_width=True)