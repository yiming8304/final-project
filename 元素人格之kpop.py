import streamlit as st
import math
import pandas as pd

# 页面基础配置
st.set_page_config(page_title="五系动物人格匹配器", page_icon="🐾", layout="centered")

# ---------------------- 动物主题配色方案 ----------------------
animal_themes = {
    "cat": {
        "name": "猫系",
        "emoji": "🐱",
        "primary": "#8B5CF6",      # 紫色
        "secondary": "#A78BFA",    # 浅紫
        "bg_gradient": "linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)",
        "card_bg": "rgba(139, 92, 246, 0.1)",
        "text_color": "#4C1D95"
    },
    "fox": {
        "name": "狐系",
        "emoji": "🦊",
        "primary": "#F97316",      # 橙红色
        "secondary": "#FB923C",    # 浅橙色
        "bg_gradient": "linear-gradient(135deg, #F97316 0%, #EF4444 100%)",
        "card_bg": "rgba(249, 115, 22, 0.1)",
        "text_color": "#9A3412"
    },
    "deer": {
        "name": "鹿系",
        "emoji": "🦌",
        "primary": "#22C55E",      # 绿色
        "secondary": "#4ADE80",    # 浅绿
        "bg_gradient": "linear-gradient(135deg, #22C55E 0%, #10B981 100%)",
        "card_bg": "rgba(34, 197, 94, 0.1)",
        "text_color": "#14532D"
    },
    "dog": {
        "name": "犬系",
        "emoji": "🐶",
        "primary": "#EAB308",      # 金黄色
        "secondary": "#FACC15",    # 浅金黄
        "bg_gradient": "linear-gradient(135deg, #EAB308 0%, #CA8A04 100%)",
        "card_bg": "rgba(234, 179, 8, 0.1)",
        "text_color": "#854D0E"
    },
    "rabbit": {
        "name": "兔系",
        "emoji": "🐰",
        "primary": "#EC4899",      # 粉色
        "secondary": "#F472B6",    # 浅粉
        "bg_gradient": "linear-gradient(135deg, #EC4899 0%, #DB2777 100%)",
        "card_bg": "rgba(236, 72, 153, 0.1)",
        "text_color": "#831843"
    },
    "tiger": {
        "name": "虎系",
        "emoji": "🐯",
        "primary": "#F59E0B",      # 橙色
        "secondary": "#FBBF24",    # 浅橙
        "bg_gradient": "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
        "card_bg": "rgba(245, 158, 11, 0.1)",
        "text_color": "#92400E"
    }
}

# ---------------------- KPOP偶像数据 ----------------------
kpop_idols = {
    "cat": {
        "description": "灵动、神秘、奶凶",
        "idols": [
            {"name": "Jennie", "chinese_name": "珍妮", "group": "BLACKPINK"},
            {"name": "Haerin", "chinese_name": "海潾", "group": "NewJeans"},
            {"name": "Ningning", "chinese_name": "宁宁", "group": "aespa"}
        ]
    },
    "fox": {
        "description": "妩媚、锐利、放电",
        "idols": [
            {"name": "Yeji", "chinese_name": "礼志", "group": "ITZY"},
            {"name": "Tzuyu", "chinese_name": "周子瑜", "group": "TWICE"},
            {"name": "Gaeul", "chinese_name": "秋天", "group": "IVE"},
            {"name": "Kim Min-ju", "chinese_name": "金玟周", "group": "前 IZ*ONE / 演员"}
        ]
    },
    "deer": {
        "description": "清纯、大眼、温顺",
        "idols": [
            {"name": "YoonA", "chinese_name": "林允儿", "group": "少女时代"},
            {"name": "Sullyoon", "chinese_name": "薛仑娥", "group": "NMIXX"},
            {"name": "Leeseo", "chinese_name": "李瑞", "group": "IVE"},
            {"name": "IU", "chinese_name": "李知恩", "group": "Solo歌手"}
        ]
    },
    "dog": {
        "description": "阳光、亲厚、治愈",
        "idols": [
            {"name": "An Yu-jin", "chinese_name": "安宥真", "group": "IVE"},
            {"name": "Yuqi", "chinese_name": "宋雨琦", "group": "(G)I-DLE"},
            {"name": "Minji", "chinese_name": "敏姬", "group": "NewJeans"},
            {"name": "Seulgi", "chinese_name": "姜涩琪", "group": "Red Velvet"}
        ]
    },
    "rabbit": {
        "description": "软萌、精致、乖巧",
        "idols": [
            {"name": "Nayeon", "chinese_name": "林娜琏", "group": "TWICE"},
            {"name": "Wonyoung", "chinese_name": "张员瑛", "group": "IVE"},
            {"name": "Suzy", "chinese_name": "裴秀智", "group": "前 Miss A / 演员"},
            {"name": "Yuna", "chinese_name": "裕那", "group": "ITZY"}
        ]
    },
    "tiger": {
        "description": "英气、霸气、浓颜",
        "idols": [
            {"name": "Nana", "chinese_name": "林珍娜", "group": "After School"},
            {"name": "Jisu", "chinese_name": "崔智寿", "group": "STAYC"},
            {"name": "Jihyo", "chinese_name": "朴志效", "group": "TWICE"},
            {"name": "Jiho", "chinese_name": "金祉呼", "group": "前 OH MY GIRL"}
        ]
    }
}

def apply_theme(theme_key):
    theme = animal_themes[theme_key]
    st.markdown(f"""
    <style>
    .stButton>button {{
        background: {theme['bg_gradient']};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        opacity: 0.9;
    }}
    .result-card {{
        background: {theme['card_bg']};
        border: 2px solid {theme['primary']};
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
    }}
    .theme-title {{
        color: {theme['primary']};
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

def display_kpop_idols(theme_key):
    theme = animal_themes[theme_key]
    idol_data = kpop_idols[theme_key]
    
    st.subheader(f"🎤 你的同系KPOP偶像")
    st.markdown(f"<p style='color:{theme['primary']}; font-weight:bold;'>{theme['emoji']} {theme['name']}特征：{idol_data['description']}</p>", unsafe_allow_html=True)
    
    # 创建偶像展示卡片
    for idol in idol_data['idols']:
        st.markdown(f"""
        <div style="background: {theme['card_bg']}; border-left: 4px solid {theme['primary']}; 
                    padding: 12px 16px; margin: 8px 0; border-radius: 8px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <strong style="color: {theme['primary']}; font-size: 16px;">{idol['name']}</strong>
                    <span style="color: #666; margin-left: 8px;">({idol['chinese_name']})</span>
                </div>
                <div style="background: {theme['primary']}; color: white; padding: 4px 12px; 
                            border-radius: 12px; font-size: 12px; font-weight: bold;">
                    {idol['group']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.title("🐾 五系动物人格匹配器")
st.markdown("### 请根据你的真实情况,为5项特质打分(0-10分,分数越高越符合）")

name = st.text_input("输入你的代号：", "kpop")

# ---------------------- 1. 特质滑块（5个维度，对应6种动物的核心特质） ----------------------
# 维度设计：每个维度对应一种动物的核心标签，同时覆盖其他动物的特质（共6种动物）
independent = st.slider("🔹 独立高冷（不依赖他人，有自己的节奏）", 0, 10, 5)
cunning = st.slider("🔸 机敏聪慧（反应快，擅长观察和变通）", 0, 10, 5)
gentle = st.slider("🔹 温柔治愈（性格软，共情力强，安静温和）", 0, 10, 5)
loyal = st.slider("🔸 忠诚热情（重感情，开朗外向，行动力强）", 0, 10, 5)
shy = st.slider("🔹 软萌胆小（害羞敏感，慢热，喜欢安静）", 0, 10, 5)

# 用户坐标：5维向量
user = [independent, cunning, gentle, loyal, shy]

# ---------------------- 2. 6种动物的标准锚点（5维坐标，保证区分度） ----------------------
# 锚点逻辑：核心特质拉满，其他特质对应动物性格，避免混淆
cat_type   = [10, 7, 6, 3, 4]  # 🐱 猫系：独立拉满，机敏+温柔，低忠诚+胆小
fox_type   = [7, 10, 4, 6, 3]  # 🦊 狐系：机敏拉满，独立+忠诚，低温柔+胆小
deer_type  = [5, 6, 10, 5, 7]  # 🦌 鹿系：温柔拉满，胆小，中等其他
dog_type   = [3, 5, 7, 10, 4]  # 🐶 犬系：忠诚拉满，温柔，低独立+机敏+胆小
rabbit_type = [4, 6, 8, 5, 10] # 🐰 兔系：胆小软萌拉满，温柔，中等其他
tiger_type = [8, 7, 4, 8, 2]   # 🐯 虎系：独立+忠诚，勇敢自信，低温柔+胆小

# ---------------------- 3. 计算欧氏距离 + 匹配逻辑 ----------------------
if st.button("开始匹配我的动物系！", type="primary"):
    # 计算用户到5个锚点的5维欧氏距离
    dist_cat = math.sqrt(
        (user[0] - cat_type[0])**2 +
        (user[1] - cat_type[1])**2 +
        (user[2] - cat_type[2])**2 +
        (user[3] - cat_type[3])**2 +
        (user[4] - cat_type[4])**2
    )
    dist_fox = math.sqrt(
        (user[0] - fox_type[0])**2 +
        (user[1] - fox_type[1])**2 +
        (user[2] - fox_type[2])**2 +
        (user[3] - fox_type[3])**2 +
        (user[4] - fox_type[4])**2
    )
    dist_deer = math.sqrt(
        (user[0] - deer_type[0])**2 +
        (user[1] - deer_type[1])**2 +
        (user[2] - deer_type[2])**2 +
        (user[3] - deer_type[3])**2 +
        (user[4] - deer_type[4])**2
    )
    dist_dog = math.sqrt(
        (user[0] - dog_type[0])**2 +
        (user[1] - dog_type[1])**2 +
        (user[2] - dog_type[2])**2 +
        (user[3] - dog_type[3])**2 +
        (user[4] - dog_type[4])**2
    )
    dist_rabbit = math.sqrt(
        (user[0] - rabbit_type[0])**2 +
        (user[1] - rabbit_type[1])**2 +
        (user[2] - rabbit_type[2])**2 +
        (user[3] - rabbit_type[3])**2 +
        (user[4] - rabbit_type[4])**2
    )
    dist_tiger = math.sqrt(
        (user[0] - tiger_type[0])**2 +
        (user[1] - tiger_type[1])**2 +
        (user[2] - tiger_type[2])**2 +
        (user[3] - tiger_type[3])**2 +
        (user[4] - tiger_type[4])**2
    )

    # 找到最小距离，确定匹配类型
    min_dist = min(dist_cat, dist_fox, dist_deer, dist_dog, dist_rabbit, dist_tiger)

    # ---------------------- 4. 结果展示（适配校园/小学场景，性格+科普） ----------------------
    if min_dist == dist_cat:
        apply_theme("cat")
        theme = animal_themes["cat"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🐱 你是【猫系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 猫系特质</strong>：独立高冷，有自己的小世界，不喜欢被束缚</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：慢热、傲娇、观察力强、有主见、外冷内热</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：喜欢独处，有自己的学习节奏，是班级里的「独行小天才」</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("cat")
    elif min_dist == dist_fox:
        apply_theme("fox")
        theme = animal_themes["fox"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🦊 你是【狐系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 狐系特质</strong>：机敏聪慧，反应超快，擅长观察和变通</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：机灵、社交力强、有谋略、好奇心旺盛、适应力强</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：班级里的「小机灵鬼」，擅长解决问题，人缘超好</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("fox")
    elif min_dist == dist_deer:
        apply_theme("deer")
        theme = animal_themes["deer"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🦌 你是【鹿系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 鹿系特质</strong>：温柔治愈，共情力拉满，安静又善良</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：温柔、善良、有同理心、安静、气质干净</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：班级里的「暖心小天使」，同学有困难都会主动帮忙</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("deer")
    elif min_dist == dist_dog:
        apply_theme("dog")
        theme = animal_themes["dog"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🐶 你是【犬系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 犬系特质</strong>：忠诚热情，开朗外向，永远充满活力</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：忠诚、开朗、热情、行动力强、重感情</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：班级里的「活力担当」，班级活动的积极分子，朋友超多</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("dog")
    elif min_dist == dist_tiger:
        apply_theme("tiger")
        theme = animal_themes["tiger"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🐯 你是【虎系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 虎系特质</strong>：勇敢自信，独立果断，有领导力</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：勇敢、自信、独立、果断、有领导力、责任感强</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：班级里的「小领袖」，做事有担当，同学们的主心骨</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("tiger")
    else:
        apply_theme("rabbit")
        theme = animal_themes["rabbit"]
        st.balloons()
        st.markdown(f"""
        <div class="result-card">
            <h2 class="theme-title">🐰 你是【兔系】人格！</h2>
            <p><strong style="color:{theme['primary']};">✨ 兔系特质</strong>：软萌胆小，害羞敏感，慢热又可爱</p>
            <p><strong style="color:{theme['primary']};">💡 性格标签</strong>：软萌、害羞、敏感、慢热、可爱、细心</p>
            <p><strong style="color:{theme['primary']};">🎒 校园表现</strong>：班级里的「软萌小可爱」，安静认真，做事细心</p>
        </div>
        """, unsafe_allow_html=True)
        display_kpop_idols("rabbit")

    # ---------------------- 5. 特质得分可视化（直观展示，适配教学） ----------------------
    st.subheader("📊 你的5项特质得分分布")
    df = pd.DataFrame({
        "特质": ["独立高冷", "机敏聪慧", "温柔治愈", "忠诚热情", "软萌胆小"],
        "分数": [independent, cunning, gentle, loyal, shy]
    })
    st.bar_chart(df.set_index("特质"))

    # ---------------------- 6. 拓展：同系好友匹配（班级互动功能） ----------------------
    st.markdown(f"<h3 style='color:{theme['primary']};'>👯 找你的同系小伙伴！</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: {theme['card_bg']}; border: 2px solid {theme['primary']}; border-radius: 12px; padding: 16px;">
        <p style="color: {theme['primary']}; font-weight: bold;">{theme['emoji']} {theme['name']}适合和谁做朋友？</p>
        <ul style="color: {theme['text_color']}; margin-top: 10px; list-style-type: none; padding-left: 0;">
            <li style="padding: 4px 0;">🐱 猫系适合和：狐系、鹿系做朋友（同频不打扰）</li>
            <li style="padding: 4px 0;">🦊 狐系适合和：猫系、犬系做朋友（互补又合拍）</li>
            <li style="padding: 4px 0;">🦌 鹿系适合和：兔系、犬系做朋友（温柔互相治愈）</li>
            <li style="padding: 4px 0;">🐶 犬系适合和：狐系、鹿系做朋友（热情带动氛围）</li>
            <li style="padding: 4px 0;">🐰 兔系适合和：鹿系、猫系做朋友（安静互相陪伴）</li>
            <li style="padding: 4px 0;">🐯 虎系适合和：犬系、狐系做朋友（互补又有共同目标）</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)