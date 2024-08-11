import streamlit as st
import pydeck as pdk
import altair as alt
import numpy as np
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
import re

# Hide the deploy menu
# https://discuss.streamlit.io/t/hide-deploy-and-streamlit-mainmenu/52433
st.set_page_config(page_title="KMind中英词典")
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        header {display: hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

dict_tag_mapping = {
    "gre": "GRE",
    "toefl": "托福",
    "cet6": "六级",
    "ielts": "雅思",
    "ky": "考研",
    "cet4": "四级",
    "gk": "高考",
    "zk": "中考"
}

dict_exchange_mapping = {
    "p:": "过去式：",
    "d:": "过去分词：",
    "i:": "现在分词：",
    "3:": "第三人称单数：",
    "r:": "比较级：",
    "t:": "最高级：",
    "s:": "名词复数形式："
}

# 从Bing搜索图片
def fetch_thumbnail_url(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    search_url = f'https://www.bing.com/images/search?q={query}'
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to fetch search results")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    image_element = soup.find('img', class_='mimg')
    
    if image_element and image_element.has_attr('src'):
        return image_element['src']
    
    # Try to find the image URL in the data-murl attribute if src is not available
    image_element = soup.find('a', class_='iusc')
    if image_element and 'm' in image_element.attrs:
        m_url = image_element['m']
        match = re.search(r'"murl":"(.*?)"', m_url)
        if match:
            return match.group(1)
    
    return None

# 使用正则表达式匹配中文字符
def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_prefix(df, word):
    return df[df['word'].str.startswith(word, na=False)]

def search_suffix(df, word):
    return df[df['word'].str.endswith(word, na=False)]

def search_contain(df, word):
    return df[df['word'].str.contains(word, na=False)]

def search_match(df, word):
    return df[df['word'].str.lower() == word.lower()]

# LOAD DATA ONCE
@st.cache_resource
def load_data():
    path = "./data/kdict.csv"
    data = pd.read_csv(path)
    return data

data = load_data()

st.title("KMind中英词典")
st.subheader(":rainbow[超级联想思维英语学习]")
st.write("解锁单词学习的终极工具！KMind中英词典通过词汇的联想关联，构建同前缀/后缀/关键词单词之前的新桥梁，让学习英语更加有趣。提升词汇量，从未如此轻松有趣。")
st.caption("可以使用\"-\"符号来查询前缀与后缀，例如：-tion可以查询tion结尾的单词，like-可以查询like开头的单词。")
st.divider()

text_input = st.text_input("Hi, 请在这里输入中英文单词 💁‍♂️", "play")

if text_input:

    if contains_chinese(text_input):
        df = data[data['translation'].str.contains(text_input, na=False)]
    elif '-' not in text_input:
        df = search_contain(data, text_input)

        # 检查是否存在与text_input完全匹配的单词，如果有，则移动到首行
        if (df['word'] == text_input).any():
            matching_rows = df[df['word'] == text_input]
            non_matching_rows = df[df['word'] != text_input]
            df = pd.concat([matching_rows, non_matching_rows], ignore_index=True)
    else:
        if text_input.startswith("-"):
            df = search_suffix(data, text_input[1:])
        elif text_input.endswith("-"):
            df = search_prefix(data, text_input[:-1])

    # 如果结果太多，则只展示前10个单词
    num = len(df)
    msg = f"共找到 {num} 个相关单词"
    if len(df) > 10:
        msg += "，以下为前10个单词："
    st.caption(msg)
    df = df.head(10)

    for _, row in df.iterrows():

        word = row['word']
        st.subheader(word)
        image_url = fetch_thumbnail_url(word)
        if image_url is not None:
            st.image(image_url)
        st.caption(f"- 发音：[{row['phonetic']}]")
        st.caption(f"- 中译：{row['translation'].replace('\\n', '; ')}")
        st.caption(f"- 英译：{row['definition'].replace('\\n', '; ')}")

        translated_tags = '/'.join(dict_tag_mapping.get(tag, tag) for tag in row['tag'].split())
        st.caption(f"- 考纲：{translated_tags}")

        if not pd.isna(row['exchange']):
            exchange_str = row['exchange']
            for key, value in dict_exchange_mapping.items():
                exchange_str = exchange_str.replace(key, value)
            st.caption(f"- {'; '.join(exchange_str.split('/'))}")

        st.divider()


st.caption(":email: 173163933@qq.com ***(Wang Kang)***")