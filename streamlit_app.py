import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import platform
linux = platform.system() == 'Linux'

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
    #search_url = f'https://www.bing.com/images/search?q={query}&qft=+filterui:photo-clipart&form=IRFLTR&first=1'
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
    pattern = re.compile(f'^({word})', re.IGNORECASE)
    return df[df['word'].str.contains(pattern, na=False)]

def search_suffix(df, word):
    pattern = re.compile(f'({word})$', re.IGNORECASE)
    return df[df['word'].str.contains(pattern, na=False)]

def search_contain(df, word):
    return df[df['word'].str.contains(word, case=False, na=False)]

def search_match(df, word):
    return df[df['word'].str.lower() == word.lower()]

# 使用正则进行模糊匹配
def search_fusion(df, word):
    _df = df[df['word'].str.len() == len(word)]
    pattern = re.compile(f'^{word.replace('*', '.*')}$')
    return _df[_df['word'].str.contains(pattern, regex=True, na=False)]

# 替换函数，忽略大小写
def replace_ignore_case(word, text_input, replacement):
    # 使用正则表达式进行忽略大小写的替换
    pattern = re.compile(re.escape(text_input), re.IGNORECASE)
    return pattern.sub(replacement, word)

# 对句子中的关键词进行高亮
def highlight_text(text, keyword, prefix=':blue[', suffix=']'):
    # 将两个字符串转换为小写
    _text = text.lower()
    _keyword = keyword.lower()

    # 找到子字符串的起始位置
    start_idx = _text.find(_keyword)
    if start_idx == -1:
        return text
    
    # 计算子字符串的结束位置
    end_idx = start_idx + len(_keyword)

    # 在子字符串前后加上符号
    output = text[:start_idx] + prefix + text[start_idx:end_idx] + ']' + text[end_idx:]
    return output

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
st.markdown("● **:red[前缀查询法]: trans-** 可以查询到transformation, transition, tranfer, transistor等。")
st.markdown("● **:orange[后缀查询法]: -tion** 可以查询到information, formation, transformation等。")
st.markdown("● **:green[模糊匹配法]: \*ight** 可以查询搜索到might, right, night, light等。")
st.divider()

text_input = st.text_input("Hi, 请在这里输入中英文单词 💁‍♂️", "play")

if text_input:

    is_chinese = contains_chinese(text_input)
    if is_chinese:
        df = data[data['translation'].str.contains(text_input, na=False)]
    elif '*' in text_input:
        df = search_fusion(data, text_input)
    elif '-' not in text_input:
        df = search_contain(data, text_input)
    else:
        if text_input.startswith("-"):
            text_input = text_input[1:]
            df = search_suffix(data, text_input)
        elif text_input.endswith("-"):
            text_input = text_input[:-1]
            df = search_prefix(data, text_input)

    # 根据词频的高低排序
    df = df.sort_values(by='frq', ascending=True)
    
    # 检查是否存在与text_input完全匹配的单词，如果有，则移动到首行
    if is_chinese is False:
        match_rows = df['word'].str.lower() == text_input.lower()
        if match_rows.any():
            matches = df[match_rows]
            unmatches = df[df['word'].str.lower() != text_input.lower()]
            df = pd.concat([matches, unmatches], ignore_index=True)

    # 如果结果太多，则只展示前10个单词
    num = len(df)
    msg = f"共找到 {num} 个相关单词"
    if len(df) > 10:
        msg += "，以下为前10个单词："
    st.caption(msg)
    df = df.head(10)

    for _, row in df.iterrows():

        word = row['word']
        
        # Show the word
        word_display = word
        word_tranlation = row['translation'].replace('\\n', '; ')
        if is_chinese:
            word_tranlation = highlight_text(word_tranlation, text_input)
        else:
            word_display = highlight_text(word, text_input)
        st.title(word_display)

        if linux:
            # 使用 espeak 生成语音并保存为 wav 文件
            subprocess.run(['espeak', word, '--stdout'], stdout=open('audio.wav', 'wb'))

            # 使用 Streamlit 播放 hello.wav 文件
            st.audio('audio.wav', format='audio/wav')

        # Search & show image
        image_url = fetch_thumbnail_url(word)
        if image_url is not None:
            st.image(image_url)
        
        st.write(f"[{row['phonetic']}]")
        st.write(f"{word_tranlation}")
        st.write(f"{row['definition'].replace('\\n', '; ')}")
        #st.caption(f"- 词频：[{row['frq']}]")

        translated_tags = '/'.join(dict_tag_mapping.get(tag, tag) for tag in row['tag'].split())
        st.caption(f"{translated_tags}")

        if not pd.isna(row['exchange']):
            exchange_str = row['exchange']
            for key, value in dict_exchange_mapping.items():
                exchange_str = exchange_str.replace(key, value)
            st.caption(f"{'; '.join(exchange_str.split('/'))}")

        st.divider()


st.caption(":email: 173163933@qq.com ***(Wang Kang)***")
