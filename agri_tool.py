import os
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import fitz
import requests
import io
import urllib.parse
import seaborn as sns
import re
import markdown
import json
import time
from openai import OpenAI

# ==========================================
# 🚀 导师特制：全自动云端中文字体修复补丁
# ==========================================
@st.cache_resource
def setup_chinese_font():
    font_path = "SimHei.ttf"
    # 如果云端没有这个字体，自动去稳定CDN下载
    if not os.path.exists(font_path):
        try:
            font_url = "https://cdn.jsdelivr.net/gh/StellarCN/scp_zh@master/fonts/SimHei.ttf"
            urllib.request.urlretrieve(font_url, font_path)
        except:
            pass # 容错处理
    
    # 强制让 Matplotlib 加载并使用这个中文字体
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.sans-serif'] = fm.FontProperties(fname=font_path).get_name()
    else:
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

setup_chinese_font() # 运行补丁

# ==========================================
# 页面基础设置与 UI 注入
# ==========================================
st.set_page_config(page_title="破土者 GroundBreaker", layout="wide", initial_sidebar_state="expanded")

# ⚡ 终极暴力穿透 CSS (精准修复 Tab 丢失问题)
st.markdown("""
<style>
    /* 隐藏顶部和底部冗余元素 */
    [data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    
    /* 整体暗色背景基调 */
    .stApp { background: linear-gradient(135deg, #0F1217 0%, #1A1F26 100%); color: #E8EAED; font-family: "Helvetica Neue", Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: rgba(20, 24, 29, 0.95); border-right: 1px solid #2A313C; min-width: 220px !important; max-width: 220px !important; }
    .block-container { max-width: 95% !important; padding-top: 2rem !important; }
    
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 600 !important; }
    p, label, .stMarkdown, .stText { color: #E8EAED !important; }
    
    /* 💥 痛点 1：只精准隐藏滚动箭头，绝对不隐藏选项卡本身！ */
    button[aria-label="Scroll right"], button[aria-label="Scroll left"],
    div[data-testid="stTabs"] button[kind="icon"] {
        display: none !important; 
        width: 0 !important;
        height: 0 !important;
    }
    
    /* 强力恢复选项卡（登录/注册/微信）的显示和点击功能 */
    button[data-baseweb="tab"], button[role="tab"] {
        display: inline-flex !important; 
        pointer-events: auto !important;
        visibility: visible !important;
    }

    /* 💥 痛点 2 & 5：强制所有输入框（登录/注册/聊天栏）为 白底黑字！绝对清晰！ */
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    input[type="text"], input[type="password"], input[type="number"],
    [data-testid="stChatInput"], [data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* 输入框边框加上专属品牌色 */
    div[data-baseweb="input"] { border: 2px solid #C87A5D !important; border-radius: 6px !important; }
    [data-testid="stChatInput"] { border: 2px solid #C87A5D !important; border-radius: 8px !important; }

    /* 占位符文字改成灰色，方便看清 */
    input::placeholder, textarea::placeholder { 
        color: #666666 !important; 
        -webkit-text-fill-color: #666666 !important; 
        font-weight: 400 !important;
    }

    /* 强制聊天框右侧发送按钮醒目化 */
    [data-testid="stChatInputSubmit"] {
        background-color: #C87A5D !important;
        border-radius: 6px !important;
    }
    [data-testid="stChatInputSubmit"] svg { fill: #FFFFFF !important; color: #FFFFFF !important; }

    /* 💥 痛点 3：上传文件框（Upload、200MB等）字体绝对提纯显眼 */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1A1F26 !important;
        border: 2px dashed #C87A5D !important;
    }
    /* 穿透所有小字并强制白色 */
    [data-testid="stFileUploadDropzone"] span, 
    [data-testid="stFileUploadDropzone"] small, 
    [data-testid="stFileUploadDropzone"] div {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 下拉选择框（X轴、Y轴、图表选择）字迹清晰化 */
    div[data-baseweb="select"] { background-color: #FFFFFF !important; border: 2px solid #C87A5D !important; border-radius: 6px !important; }
    div[data-baseweb="select"] span { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: bold !important; }
    ul[role="listbox"], div[data-baseweb="popover"] { background-color: #FFFFFF !important; border: 1px solid #C87A5D !important; }
    li[role="option"] { color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 500 !important;}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] { background-color: #C87A5D !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;}

    /* 图表生成后右上角的“全屏放大”按钮显眼化 */
    button[title="View fullscreen"] {
        background-color: #C87A5D !important; border-radius: 4px !important; border: 1px solid #FFFFFF !important;
        opacity: 1 !important; visibility: visible !important;
    }
    button[title="View fullscreen"] svg { fill: #FFFFFF !important; stroke: #FFFFFF !important; }

    /* Toast 验证码弹窗高亮清晰 */
    [data-testid="stToast"] { background-color: #1A1F26 !important; border: 2px solid #C87A5D !important; border-radius: 8px !important; }
    [data-testid="stToast"] div, [data-testid="stToast"] span { color: #FFFFFF !important; font-weight: bold !important; font-size: 15px !important; }

    /* 按钮样式 */
    .stDownloadButton > button, .stButton > button {
        background-color: #C87A5D !important; color: white !important; border: none !important;
        border-radius: 8px !important; box-shadow: 0 4px 12px rgba(200, 122, 93, 0.4) !important; transition: all 0.3s ease;
    }
    .stDownloadButton > button p, .stButton > button p { color: #FFFFFF !important; font-weight: bold !important; }
    .stDownloadButton > button:hover, .stButton > button:hover { background-color: #B26A4F !important; transform: translateY(-1px); }

    /* 选项卡 Tabs 美化 */
    button[data-baseweb="tab"] p { color: #88929E !important; font-size: 16px !important; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #C87A5D !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #C87A5D !important; }

    hr { border-top-color: #2A313C !important; }
</style>
""", unsafe_allow_html=True)

# ⚠️ 读取云端 API Key 
API_KEY = st.secrets["DEEPSEEK_API_KEY"] 
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# ==========================================
# 🔐 模块 0：商业级用户注册与登录系统
# ==========================================
USER_DB_FILE = "hetu_users.json"

if not os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, "w") as f:
        json.dump({"admin": "123456"}, f) 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    with col2:
        st.markdown("""
        <div style='text-align: center; margin-top: 6vh; margin-bottom: 4vh;'>
            <h1 style='font-size: 3.8rem; display: flex; justify-content: center; align-items: center; gap: 8px; margin: 0; font-weight: 900;'>
                <span style='font-size: 3.2rem;'>⚡</span>破土者
            </h1>
            <div style='font-size: 1.4rem; letter-spacing: 0.6rem; color: #C87A5D; margin-top: 8px; margin-bottom: 18px; font-weight: 500;'>
                GroundBreaker
            </div>
            <div style='width: 60px; height: 3px; background-color: #555; margin: 0 auto 25px auto; border-radius: 2px;'></div>
            <div style='display: flex; justify-content: center; align-items: center; width: 100%; margin: 0 auto;'>
                <p style='color: #88929E; font-size: 1.15rem; letter-spacing: 2px; font-style: italic; white-space: nowrap; margin: 0;'>
                    “溯源厚土脉络，于方寸数据间洞见智慧生长”
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📱 验证码注册", "🔑 密码登录", "💬 微信扫码"])
        
        with tab1:
            st.caption("新用户请验证手机号进行注册")
            reg_phone = st.text_input("输入 11 位手机号")
            c_a, c_b = st.columns([2, 1])
            with c_a: 
                reg_code = st.text_input("短信验证码")
            with c_b: 
                st.write("") 
                if st.button("获取验证码", use_container_width=True):
                    if len(reg_phone) == 11:
                        st.toast(f"📱 【破土者科技】您的验证码是 8888，5分钟内有效。")
                    else:
                        st.error("请输入正确的手机号")
                        
            reg_pwd = st.text_input("设置专属登录密码", type="password")
            
            if st.button("立即注册并进入", use_container_width=True, type="primary"):
                if reg_code == "8888" and reg_pwd:
                    with open(USER_DB_FILE, "r") as f: db = json.load(f)
                    if reg_phone in db:
                        st.warning("该手机号已注册，请直接使用密码登录。")
                    else:
                        db[reg_phone] = reg_pwd
                        with open(USER_DB_FILE, "w") as f: json.dump(db, f)
                        st.session_state.logged_in = True
                        st.session_state.current_user = reg_phone
                        st.success("注册成功！欢迎加入破土者。")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.error("验证码错误或密码为空！(测试验证码请输入 8888)")

        with tab2:
            with st.form("pwd_login"):
                u_name = st.text_input("手机号/用户名")
                pwd = st.text_input("密码", type="password")
                if st.form_submit_button("安全登录", use_container_width=True):
                    with open(USER_DB_FILE, "r") as f: db = json.load(f)
                    if u_name in db and db[u_name] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_name
                        st.success("登录成功！正在唤醒引擎...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("账号或密码错误，请检查！")
                    
        with tab3:
            st.write("")
            st.info("💡 **企业资质保护**：微信扫码通道需接入微信开放平台企业资质后方可生成真实动态二维码。当前环境请使用密码或手机号。")
            
    st.stop() 

# ==========================================
# 🔓 以下为主程序代码 (仅登录后可见)
# ==========================================

st.sidebar.markdown(f"### 👤 欢迎, {st.session_state.current_user}\n<span style='color: #C87A5D; font-size: 13px;'>💎 PRO 旗舰版用户</span>", unsafe_allow_html=True)

st.sidebar.header("🧭 功能导航")
menu = st.sidebar.radio("请选择模块", ["📄 1. 文献快速解析", "📊 2. 实验数据作图", "🔭 3. 研究盲点洞察"])

# 登出按钮
st.sidebar.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 登出系统", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# 模块 1：文献解析
# ==========================================
if menu == "📄 1. 文献快速解析":
    st.header("💬 智能文献对话")
    uploaded_pdf = st.file_uploader("📥 请上传文献 (PDF格式)", type="pdf")
    if uploaded_pdf is not None:
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_pdf.name:
            with st.spinner("📚 正在研读文献中..."):
                doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
                st.session_state.pdf_text = "".join([doc.load_page(i).get_text() for i in range(min(4, len(doc)))]).encode('utf-8', 'ignore').decode('utf-8')
                st.session_state.current_file = uploaded_pdf.name
                st.session_state.messages = [{"role": "assistant", "content": "🎉 文献已成功载入！你可以直接提问，或点击生成总结。"}]
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑‍🌾"): st.markdown(msg["content"])
        
        st.write("") 
        c1, c2, c3 = st.columns([2, 2, 1])
        d_txt, a_pmt = None, None
        
        with c1:
            if st.button("🐣 生成小白版总结", use_container_width=True): 
                d_txt = "帮我生成小白版总结！"
                a_pmt = "你是一位在B站拥有百万粉丝的农学知识区UP主，也是一个脱口秀段子手。请用最受中国年轻人欢迎的互联网语境再加上脱口秀段子手的风格解读这篇文献：1.核心故事 2.用的绝招 3.还有啥坑没填。【最高红线】：绝对禁止任何与恋爱、两性、婚姻、犯罪或违禁品相关的拟人化比喻！【风格要求】：请用单口喜剧的节奏，多使用中国本土的“高级梗”。例如：把植物和微生物的互动比作“甲方乙方”、“打工人抱大腿”、“发送微信验证码”；把基因或物质比作“叠buff”、“开物理外挂”、“充值氪金”或“卡BUG”。语言要犀利、爆笑且充满当代年轻人的共鸣。"
        
        with c2:
            if st.button("🔬 生成专家版总结", use_container_width=True): 
                d_txt = "帮我生成专家版总结！"
                a_pmt = "你是一位顶刊（如Nature/Cell子刊）的资深审稿人兼心狠手辣的课题组老板。请为你的博士生进行这篇文献的硬核拆解，严禁平铺直叙的废话！必须包含以下四大模块：1. 【发刊护城河】：一句话说清这篇论文凭什么能发（核心创新点或绝杀机制）。2. 【硬核技术栈】：不要报流水账，直接提炼他们用了什么最值钱、最值得我们实验室复刻的实验技术或数据分析流。3. 【审稿人的凝视】：用Reviewer #2的毒辣眼光，指出这篇论文的致命软肋（如逻辑跳跃、样本局限、田间转化难度）。4.【直接引用语料（神级功能）】：请为用户生成3句可以直接Copy到他们自己论文中的中英文引用句（分别对应：引言做背景、讨论做机制对比、展望做未解之谜）。5. 【课题“借鉴”指南（最高价值）】：如果我们想把它的核心思路“平移”到我们自己的农学物种上，请给出1-2个极具可行性的、能发SCI的延伸课题思路。"
        
        with c3:
            chat_hist = "\n\n".join([f"{'AI' if m['role']=='assistant' else '我'}:\n{m['content']}" for m in st.session_state.messages])
            st.download_button("📥 导出记录", data=chat_hist.encode('utf-8'), file_name="对话记录.txt", use_container_width=True)
        
        u_in = st.chat_input("输入问题检索文献细节 💬")
        if d_txt or u_in:
            f_disp, f_api = d_txt if d_txt else u_in, a_pmt if a_pmt else u_in
            st.session_state.messages.append({"role": "user", "content": f_disp, "api_content": f_api})
            with st.chat_message("user", avatar="🧑‍🌾"): st.markdown(f_disp)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("脑暴中..."):
                    try:
                        m_api = [{"role": "system", "content": f"请根据文献回答。\n{st.session_state.pdf_text[:6000]}"}]
                        for m in st.session_state.messages[-5:-1]: m_api.append({"role": m["role"], "content": m.get("api_content", m["content"])})
                        m_api.append({"role": "user", "content": f_api})
                        ans = client.chat.completions.create(model="deepseek-chat", messages=m_api).choices[0].message.content
                        st.markdown(ans); st.session_state.messages.append({"role": "assistant", "content": ans})
                    except Exception as e: st.error(f"服务异常：{e}")

# ==========================================
# 模块 2：实验数据作图
# ==========================================
elif menu == "📊 2. 实验数据作图":
    st.header("🎨 数据可视化中心")
    if "show_plot" not in st.session_state: st.session_state.show_plot = False
    if "ai_mods" not in st.session_state: st.session_state.ai_mods = []
    up_f = st.file_uploader("📂 上传数据表 (.csv 或 .xlsx)", type=["csv", "xlsx", "xls"])
    if up_f is not None:
        df = pd.read_csv(up_f) if up_f.name.endswith('.csv') else pd.read_excel(up_f)
        c_opts = ["1. 箱线散点图 (Box + Swarm)", "2. 散点回归图 (Scatter + Regression)", "3. 显著性柱状图 (Barplot + Letters)", "4. 组学火山图 (Volcano Plot)", "5. 相关性热图 (Correlation Heatmap)", "6. 小提琴图 (Violin Plot)", "7. 生长曲线折线图 (Lineplot + Error)", "8. 核密度分布图 (KDE Density)", "9. 物种/成分饼图 (Pie Chart)", "10. PCA 主成分分析图 (PCA Scatter)"]
        c_typ = st.selectbox("📌 选择图表模板", c_opts)
        cols = df.columns.tolist()
        with st.form("chart_params_form"):
            x_col, y_col, sig_col, logfc_col, pval_col, hue_col, cat_col, val_col = [None]*8
            fc_th, p_th = 1.0, 0.05
            if c_typ.startswith(("1", "2", "6", "7")): c1, c2 = st.columns(2); x_col, y_col = c1.selectbox("X 轴", cols, index=0), c2.selectbox("Y 轴", cols, index=1 if len(cols)>1 else 0)
            elif c_typ.startswith("3"): c1, c2, c3 = st.columns(3); x_col, y_col, sig_col = c1.selectbox("X 轴", cols, index=0), c2.selectbox("Y 轴", cols, index=1 if len(cols)>1 else 0), c3.selectbox("显著性标记列", ["无"] + cols)
            elif c_typ.startswith("4"): c1, c2, c3, c4 = st.columns(4); logfc_col, pval_col, fc_th, p_th = c1.selectbox("Log2FC", cols), c2.selectbox("P-value", cols), c3.slider("FC 阈值", 0.0, 5.0, 1.0, 0.1), c4.number_input("P 阈值", value=0.05)
            elif c_typ.startswith("8"): c1, c2 = st.columns(2); val_col, hue_col = c1.selectbox("数值列", cols), c2.selectbox("分组列", ["无"] + cols)
            elif c_typ.startswith("9"): c1, c2 = st.columns(2); cat_col, val_col = c1.selectbox("分类列", cols, index=0), c2.selectbox("数值列", cols, index=1 if len(cols)>1 else 0)
            elif c_typ.startswith("10"): hue_col = st.selectbox("分组标记列", cols)
            sub = st.form_submit_button("✨ 一键生成图表", use_container_width=True)
        
        if sub: st.session_state.show_plot, st.session_state.ai_mods = True, []
        
        if st.session_state.show_plot:
            st.divider()
            fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
            sns.set_theme(style="ticks", font_scale=1.1, rc={"axes.facecolor": "#FCFBF8", "figure.facecolor": "#FCFBF8"})
            try:
                if c_typ.startswith("1"): sns.boxplot(data=df, x=x_col, y=y_col, ax=ax, color="white", showfliers=False); sns.swarmplot(data=df, x=x_col, y=y_col, ax=ax, alpha=0.7, size=6, palette="Set2", hue=x_col, legend=False)
                elif c_typ.startswith("2"): sns.regplot(data=df, x=x_col, y=y_col, ax=ax, scatter_kws={'alpha':0.6}, line_kws={'color':'red'})
                elif c_typ.startswith("3"):
                    sns.barplot(data=df, x=x_col, y=y_col, ax=ax, errorbar="sd", capsize=0.1, edgecolor="black", linewidth=1.5, palette="Pastel1")
                    if sig_col != "无":
                        g = df.groupby(x_col); m, s, l = g[y_col].mean(), g[y_col].std().fillna(0), g[sig_col].first()
                        for i, lbl in enumerate([t.get_text() for t in ax.get_xticklabels()]):
                            if lbl in m: ax.text(i, m[lbl] + s[lbl] + (ax.get_ylim()[1]*0.02), str(l[lbl]), ha='center', va='bottom', fontweight='bold')
                elif c_typ.startswith("4"):
                    df['-Log10(P)'] = -np.log10(df[pval_col] + 1e-300); df['Status'] = np.select([(df[pval_col] < p_th) & (df[logfc_col] > fc_th), (df[pval_col] < p_th) & (df[logfc_col] < -fc_th)], ['Up', 'Down'], default='Not Sig')
                    sns.scatterplot(data=df, x=logfc_col, y='-Log10(P)', hue='Status', palette={'Up':'#E64B35', 'Down':'#4DBBD5', 'Not Sig':'#CCCCCC'}, ax=ax); ax.axhline(-np.log10(p_th), color='grey', ls='--'); ax.axvline(fc_th, color='grey', ls='--'); ax.axvline(-fc_th, color='grey', ls='--')
                elif c_typ.startswith("5"): sns.heatmap(df.select_dtypes(include=[np.number]).corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
                elif c_typ.startswith("6"): sns.violinplot(data=df, x=x_col, y=y_col, ax=ax, inner="quartile", palette="muted")
                elif c_typ.startswith("7"): sns.lineplot(data=df, x=x_col, y=y_col, ax=ax, marker="o", errorbar="sd", linewidth=2)
                elif c_typ.startswith("8"): sns.kdeplot(data=df, x=val_col, fill=True, ax=ax, color="#2E86C1", alpha=0.5) if hue_col == "无" else sns.kdeplot(data=df, x=val_col, hue=hue_col, fill=True, ax=ax, alpha=0.5, palette="Set2")
                elif c_typ.startswith("9"): p_d = df.groupby(cat_col)[val_col].sum(); ax.pie(p_d, labels=p_d.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3")); ax.axis('equal')
                elif c_typ.startswith("10"):
                    from sklearn.decomposition import PCA; from sklearn.preprocessing import StandardScaler
                    n_df = df.select_dtypes(include=[np.number]).dropna(); sc = StandardScaler().fit_transform(n_df); pca = PCA(n_components=2)
                    d_pca = pd.DataFrame(data=pca.fit_transform(sc), columns=['PC1', 'PC2']); d_pca['Group'] = df[hue_col].values[:len(d_pca)]
                    sns.scatterplot(data=d_pca, x='PC1', y='PC2', hue='Group', palette="bright", s=80, ax=ax); ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontweight='bold'); ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontweight='bold')
                
                if not c_typ.startswith(("5", "9")): sns.despine(); ax.set_xlabel(x_col if 'x_col' in locals() and x_col else "", fontweight='bold'); ax.set_ylabel(y_col if 'y_col' in locals() and y_col else "", fontweight='bold')
                for m_c in st.session_state.ai_mods:
                    try: exec(m_c, {"ax": ax, "fig": fig, "plt": plt, "sns": sns, "np": np, "pd": pd, "__builtins__": {}}, {"ax": ax, "fig": fig, "plt": plt, "sns": sns, "np": np, "pd": pd, "__builtins__": {}})
                    except: pass
                plt.tight_layout(); st.pyplot(fig)
                
                ai_cmd = st.chat_input("🪄 调图指令 (例如：把X轴标签旋转45度)")
                if ai_cmd:
                    res = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": f"你是Matplotlib专家。已有 `fig` 和 `ax`。指令：'{ai_cmd}'。只返回Python代码，不解释。"}])
                    llm_code = res.choices[0].message.content.replace("```python", "").replace("```", "").strip()
                    if not any(w in llm_code for w in ["import", "os", "sys", "subprocess", "eval", "exec", "open"]): st.session_state.ai_mods.append(llm_code); st.rerun() 
                
                def get_buf(f, fmt): b = io.BytesIO(); f.savefig(b, format=fmt, dpi=300, bbox_inches="tight"); b.seek(0); return b
                d1, d2, d3 = st.columns(3)
                d1.download_button("📥 下载 PDF", get_buf(fig, "pdf"), "plot.pdf", "application/pdf")
                d2.download_button("📥 下载 SVG", get_buf(fig, "svg"), "plot.svg", "image/svg+xml")
                d3.download_button("📥 下载 PNG", get_buf(fig, "png"), "plot.png", "image/png")
            except Exception as e: st.error("⚠️ 数据处理异常，请检查数据匹配。")

# ==========================================
# 模块 3：研究盲点与创新洞察
# ==========================================
elif menu == "🔭 3. 研究盲点洞察":
    st.header("🔭 学术前沿与课题洞察引擎")
    
    @st.cache_data(show_spinner=False)
    def load_local_db():
        files = ["my_master_library.xlsx", "my_master_library.xls", "my_master_library.csv"]
        for f in files:
            if os.path.exists(f):
                try:
                    if f.endswith('.csv'): return pd.read_csv(f)
                    else: return pd.read_excel(f)
                except: continue
        return pd.DataFrame()

    db_df = load_local_db()
    
    st.markdown("""
    > **💡 架构师提示**：系统已接入实时 PubMed 国际数据链路。
    > （后台存在专属文献库，系统将自动进行**全领域数据双轨融合**，突破闭源壁垒！）
    """)
    
    research_topic = st.text_input("🎯 请输入研究主题 (支持中文，如：双孢蘑菇、拟南芥栽培)", "双孢蘑菇")
    
    report_ready = False
    final_report = ""
    plot_data = []
    
    if st.button("🚀 开始深度洞察", type="primary"):
        with st.status("🤖 正在执行 AI 双轨学术工作流...", expanded=True) as status:
            try:
                context_data = ""
                if not db_df.empty:
                    st.write("📁 正在唤醒后台专属私有文献库...")
                    title_col = next((c for c in db_df.columns if any(k in c.lower() for k in ['title', '标题', '题名'])), None)
                    abs_col = next((c for c in db_df.columns if any(k in c.lower() for k in ['abstract', '摘要'])), None)
                    
                    if title_col and abs_col:
                        matched = db_df[db_df[abs_col].str.contains(research_topic, na=False) | db_df[title_col].str.contains(research_topic, na=False)]
                        if not matched.empty:
                            context_data += "【来自本地专属精选库】\n"
                            for i, row in matched.head(15).iterrows(): context_data += f"[本地精选] 标题: {row[title_col]}\n摘要: {row[abs_col]}\n\n"
                            st.write(f"✅ 从专属库中提炼到 {len(matched.head(15))} 篇高价值本地文献。")

                st.write("🌐 正在抓取 PubMed 国际前沿数据...")
                trans_prompt = f"将 '{research_topic}' 翻译为最严谨的生物学/农学英文检索词（若为物种须含拉丁学名）。只返回英文。"
                eng_query = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": trans_prompt}]).choices[0].message.content.strip()
                
                safe_kw = urllib.parse.quote(eng_query)
                search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={safe_kw}&retmode=json&retmax=20&sort=pub+date"
                search_res = requests.get(search_url, timeout=15).json()
                id_list = search_res.get('esearchresult', {}).get('idlist', [])
                if id_list:
                    ids_str = ",".join(id_list)
                    fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids_str}&rettype=abstract&retmode=text"
                    abstracts_data = requests.get(fetch_url, timeout=15).text
                    context_data += "【来自PubMed最新发表】\n" + abstracts_data
                    st.write(f"✅ 从 PubMed 成功提取到 {len(id_list)} 篇最新 SCI 论文。")
                
                if not context_data.strip(): raise ValueError("双轨数据库均未能检索到文献，请尝试更换关键词。")

                st.write("🧠 首席科学家正在进行盲点探测与图谱推演...")
                analysis_prompt = f"""
                你是一位顶级的农学与生物学首席科学家。请阅读以下关于 "{research_topic}" 的文献数据，为科研工作者输出战略提案报告。
                ⚠️ 严格指令：
                1. 绝不允许输出“报告人：”、“日期：”等废话。
                2. 必须包含：1.红海预警 2.蓝海前沿 3.盲点课题推荐 4.核心参考文献
                3. 参考文献必须附带原文章的超链接或来源说明。

                【生成画图数据】
                在报告最末尾，另起一行严格按以下格式输出5个热门和5个冷门数据，用于画图：
                ---DATA_START---
                热门,基因编辑,95
                冷门,太空诱变,30
                ---DATA_END---
                
                文献数据如下：
                {context_data[:15000]}
                """
                
                res_analysis = client.chat.completions.create(model="deepseek-chat", messages=[{"role": "user", "content": analysis_prompt}])
                raw_report = res_analysis.choices[0].message.content
                match = re.search(r'---DATA_START---\n(.*?)\n---DATA_END---', raw_report, re.DOTALL)
                if match:
                    data_str = match.group(1).strip()
                    for line in data_str.split('\n'):
                        parts = line.split(',')
                        if len(parts) == 3: plot_data.append({"Category": parts[0].strip(), "Topic": parts[1].strip(), "Heat": int(parts[2].strip())})
                    final_report = raw_report.replace(match.group(0), "").strip()
                else: final_report = raw_report
                    
                status.update(label="✨ 洞察完成！", state="complete")
                report_ready = True
            except Exception as e:
                status.update(label="执行失败", state="error")
                st.error(f"处理失败，可能原因：{e}")
                st.stop()

    if report_ready:
        st.divider()
        st.subheader("🔥 研究热度矩阵图谱")
        if plot_data:
            df_plot = pd.DataFrame(plot_data)
            # Y轴扰动范围拉开，气泡错落有致
            df_plot['Y_Jitter'] = np.random.uniform(0.2, 0.8, size=len(df_plot))
            
            # 画布变大！改成 14x7 的宽银幕比例
            fig_bubble, ax_bubble = plt.subplots(figsize=(14, 7), dpi=200)
            fig_bubble.patch.set_facecolor('#FCFBF8'); ax_bubble.set_facecolor('#FCFBF8')
            
            palette = {"热门": "#C87A5D", "冷门": "#4B7C9C"}
            # 气泡基础大小再放大一点，填满画面
            sns.scatterplot(data=df_plot, x="Heat", y="Y_Jitter", hue="Category", 
                            size="Heat", sizes=(2000, 8000), alpha=0.6, 
                            palette=palette, ax=ax_bubble, legend=False)
            
            for _, row in df_plot.iterrows():
                t_color = "#FFFFFF" if row["Heat"] > 60 else "#333333"
                # 去掉了可能引起冲突的 fontfamily 参数，直接用全局字体
                ax_bubble.text(row["Heat"], row["Y_Jitter"], row["Topic"], 
                               ha='center', va='center', fontsize=11, fontweight='bold', 
                               color=t_color)
            
            ax_bubble.set_xlim(-5, 105)
            ax_bubble.set_ylim(0, 1)
            
            ax_bubble.axvspan(-5, 50, color='#4B7C9C', alpha=0.08)
            ax_bubble.axvspan(50, 105, color='#C87A5D', alpha=0.08)
            # 背景文字移到角落
            ax_bubble.text(2, 0.92, "🌊 蓝海潜力区 (Low Heat)", color="#4B7C9C", fontweight="bold", fontsize=12, alpha=0.8)
            ax_bubble.text(78, 0.92, "🔥 红海内卷区 (High Heat)", color="#C87A5D", fontweight="bold", fontsize=12, alpha=0.8)

            ax_bubble.set_xlabel("研究热度指数 (Heat Index) → 越靠右代表研究越卷", fontweight='bold', fontsize=12)
            ax_bubble.set_yticks([]); ax_bubble.set_ylabel("")
            sns.despine(left=True, bottom=False)
            plt.tight_layout()
            st.pyplot(fig_bubble)
            st.caption("👆 **解码**：气泡落入左侧蓝色区域代表目前关注度低，是绝佳的创新切入点！")
        else: st.warning("⚠️ 大模型未能成功输出图谱数据，已为您跳过渲染。")
        
        st.success("📝 **AI 战略洞察报告** (下方可一键导出为 Word 文档)")
        st.markdown(final_report)
        st.markdown("---")
        html_content = markdown.markdown(final_report)
        word_doc = f"<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'><head><meta charset='utf-8'><title>学术洞察报告</title></head><body>{html_content}</body></html>"
        st.download_button(label="💾 一键导出为 Word 文档 (.doc)", data=word_doc.encode('utf-8'), file_name=f"{research_topic}_学术洞察报告.doc", mime="application/msword", type="primary")
