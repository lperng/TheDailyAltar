import streamlit as st
import os
import re

# --- Helper functions ---
def parse_toc_from_readme(readme_path="README.md"):
    """Parse the README.md to get a mapping of sections to days with full titles."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    sections = []
    section = None
    for line in lines:
        section_match = re.match(r"^#### (第[一二三四五六]部：.+)", line)
        day_match = re.match(r"^\* (第\d+天 .+)", line)
        if section_match:
            section = {'title': section_match.group(1), 'days': []}
            sections.append(section)
        elif day_match and section:
            section['days'].append(day_match.group(1))
    return sections

def get_works_file_for_section(section_idx):
    # Map section index to works file (0-based)
    return f"works{section_idx}.md"

def extract_day_content(md_path, day_title):
    def normalize(s):
        return re.sub(r'\s+', '', s)
    m = re.match(r'(第\d+天)\s*([^：:]{2,})', day_title)
    if not m:
        return "找不到該天的內容。"
    day_num = m.group(1)
    title_prefix = m.group(2)[:4]  # first 4 chars after day number
    # Try all works files in order
    for works_file in ["works0.md", "works1.md", "works2.md"]:
        try:
            with open(works_file, 'r', encoding='utf-8') as f:
                content = f.read()
            headings = list(re.finditer(r'^##\s*(第\d+天\s*[^\n]+)$', content, re.MULTILINE))
            match_idx = None
            for idx, h in enumerate(headings):
                heading = h.group(1)
                if day_num in heading and title_prefix in heading:
                    match_idx = idx
                    break
            if match_idx is not None:
                start = headings[match_idx].end()
                end = headings[match_idx + 1].start() if match_idx + 1 < len(headings) else len(content)
                return content[start:end].strip()
        except FileNotFoundError:
            continue
    return "找不到該天的內容。"

def render_styled_content(md):
    # Split into blocks: headers and non-headers
    pattern = r'(^### .+$|^#### .+$)'
    blocks = re.split(pattern, md, flags=re.MULTILINE)
    for block in blocks:
        if not block.strip():
            continue
        if block.startswith('### '):
            st.markdown(f'<div class="section-header">{block[4:].strip()}</div>', unsafe_allow_html=True)
        elif block.startswith('#### '):
            st.markdown(f'<div class="subsection-header">{block[5:].strip()}</div>', unsafe_allow_html=True)
        else:
            st.markdown(block, unsafe_allow_html=False)

# --- Main App ---
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #22223B;
        background: #F2E9E4;
        padding: 0.5em 1em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    .day-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #FFFFFF;
        background: #4A4E69;
        padding: 0.3em 0.8em;
        border-radius: 8px;
        margin-bottom: 0.7em;
    }
    .section-header {
        font-size: 1.2em;
        color: #22223B;
        background: #9A8C98;
        padding: 0.2em 0.7em;
        border-radius: 6px;
        margin: 2em 0 1em 0;
    }
    .subsection-header {
        font-size: 1.1em;
        color: #FFFFFF;
        background: #C9ADA7;
        padding: 0.15em 0.6em;
        border-radius: 5px;
        margin: 1.5em 0 1em 0;
    }
    blockquote {
        background: #F2E9E4;
        color: #4A4E69;
        border-left: 5px solid #4A4E69;
        margin: 1em 0;
        padding: 0.7em 1em;
        border-radius: 6px;
        font-style: italic;
    }
    ul, ol {
        margin-left: 2em;
        margin-bottom: 1em;
    }
    li {
        margin-bottom: 0.3em;
        font-size: 1.05em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">每日的祭壇：職場門徒的信仰實踐</div>', unsafe_allow_html=True)

# Add sidebar header for book name and tag line
st.sidebar.markdown(
    """
    <div style='font-size:1.3em; font-weight:bold; color:#4A4E69; margin-bottom:0.2em;'>每日的祭壇：職場門徒的信仰實踐</div>
    <div style='font-size:1em; color:#9A8C98; margin-bottom:1.2em;'>30天重塑工作觀，活出職場真光彩</div>
    """,
    unsafe_allow_html=True
)

sections = parse_toc_from_readme()
section_titles = [s['title'] for s in sections]

selected_section_title = st.sidebar.selectbox("選擇部份：", section_titles)
section_idx = section_titles.index(selected_section_title)
day_titles = sections[section_idx]['days']

# --- Day navigation with session state ---
if 'day_idx' not in st.session_state or st.session_state.get('last_section_idx') != section_idx:
    st.session_state.day_idx = 0
    st.session_state.last_section_idx = section_idx

def on_day_select():
    st.session_state.day_idx = day_titles.index(st.session_state.day_selectbox)

selected_day_title = st.sidebar.selectbox(
    "選擇天數：",
    day_titles,
    index=st.session_state.day_idx,
    key='day_selectbox',
    on_change=on_day_select
)

works_file = get_works_file_for_section(section_idx)

day_content = extract_day_content(works_file, selected_day_title)

# --- Navigation buttons at the very top of the main area ---
colA, colB, colC = st.columns([1,2,1])
with colA:
    if st.button('⬅️ 上一天', key='main_prev_day'):
        if st.session_state.day_idx > 0:
            st.session_state.day_idx -= 1
with colC:
    if st.button('下一天 ➡️', key='main_next_day'):
        if st.session_state.day_idx < len(day_titles) - 1:
            st.session_state.day_idx += 1

# Render the day title
st.markdown(f'<div class="day-title">{selected_day_title}</div>', unsafe_allow_html=True)

render_styled_content(day_content) 