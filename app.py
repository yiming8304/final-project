# streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

# 页面配置
st.set_page_config(page_title="TWICE 全方位粉丝助手", layout="wide")

# 数据加载（缓存）
@st.cache_data
def load_members():
    try:
        df = pd.read_csv("twice_members.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("twice_members.csv", encoding="gbk")
    df["birthday"] = pd.to_datetime(df["birthday"])
    df["birth_month"] = df["birthday"].dt.month
    df["birth_year"] = df["birthday"].dt.year
    df["age"] = (datetime.now().year - df["birth_year"]).astype(str)
    return df

@st.cache_data
def load_songs():
    try:
        df = pd.read_csv("twice_songs.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("twice_songs.csv", encoding="gbk")
    return df

# 加载数据
members_df = load_members()
songs_df = load_songs()

# 侧边栏
with st.sidebar:
    st.markdown("🍭 **TWICE 粉丝站**")
    st.divider()
    
    # 成员筛选区
    st.subheader("👤 成员筛选")
    
    selected_roles = st.multiselect(
        "队内担当",
        members_df["role"].unique(),
        default=members_df["role"].unique()
    )
    
    year_range = st.slider(
        "出生年份范围",
        min_value=members_df["birth_year"].min(),
        max_value=members_df["birth_year"].max(),
        value=(members_df["birth_year"].min(), members_df["birth_year"].max())
    )
    
    selected_nationalities = st.multiselect(
        "国籍",
        members_df["nationality"].unique(),
        default=members_df["nationality"].unique()
    )
    
    selected_mbtis = st.multiselect(
        "MBTI 性格类型",
        members_df["mbti"].unique(),
        default=members_df["mbti"].unique()
    )
    
    st.divider()
    
    # 歌曲筛选区
    st.subheader("🎵 歌曲筛选")
    
    song_year_range = st.slider(
        "发行年份范围",
        min_value=songs_df["year"].min(),
        max_value=songs_df["year"].max(),
        value=(songs_df["year"].min(), songs_df["year"].max())
    )
    
    title_filter = st.radio(
        "歌曲类型",
        ["全部歌曲", "仅看主打曲"]
    )
    
    min_views = st.number_input(
        "最低 YouTube 播放量（亿）",
        min_value=0.0,
        max_value=25.0,
        value=0.0,
        step=0.1
    )

# 应用筛选器
filtered_members = members_df[
    (members_df["role"].isin(selected_roles)) &
    (members_df["birth_year"] >= year_range[0]) &
    (members_df["birth_year"] <= year_range[1]) &
    (members_df["nationality"].isin(selected_nationalities)) &
    (members_df["mbti"].isin(selected_mbtis))
]

filtered_songs = songs_df[
    (songs_df["year"] >= song_year_range[0]) &
    (songs_df["year"] <= song_year_range[1]) &
    (songs_df["views"] >= min_views * 100000000)
]

if title_filter == "仅看主打曲":
    filtered_songs = filtered_songs[filtered_songs["title_yn"] == "是"]

# Tab 式布局
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 首页概览", "👤 成员档案", "🎵 歌曲数据库", "🎲 随机推荐", "📊 数据分析报告"])

with tab1:
    st.title("🏠 TWICE 全方位粉丝助手")
    st.markdown("欢迎来到 TWICE 粉丝助手！在这里你可以了解关于 TWICE 的一切。")
    
    # 核心指标卡
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 成员总数", len(filtered_members))
    
    with col2:
        st.metric("🎵 歌曲总数", len(filtered_songs))
    
    with col3:
        title_count = filtered_songs[filtered_songs["title_yn"] == "是"].shape[0]
        st.metric("⭐ 主打曲数量", title_count)
    
    with col4:
        total_views = filtered_songs["views"].sum() / 100000000
        st.metric("📺 总播放量（亿次）", f"{total_views:.1f}")
    
    # 中间两列布局
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 各成员出生月份分布")
        month_data = filtered_members.groupby(["birth_month", "nationality"]).size().unstack(fill_value=0)
        fig_month = px.line(month_data, x=month_data.index, y=month_data.columns, 
                          labels={"value": "人数", "birth_month": "月份", "nationality": "国籍"},
                          markers=True)
        fig_month.update_layout(height=350)
        st.plotly_chart(fig_month, width='stretch')
    
    with col_right:
        st.subheader("🎨 各成员代表色分布")
        fig_color = px.bar(filtered_members, x="name", y=[1]*len(filtered_members), 
                          color="color", color_discrete_map=dict(zip(filtered_members["name"], filtered_members["color"])),
                          labels={"y": "", "name": "成员名"},
                          hover_data=["color"])
        fig_color.update_layout(height=350, yaxis_visible=False)
        st.plotly_chart(fig_color, width='stretch')
    
    # 身高箱线图
    st.subheader("📏 各成员身高分布（按角色分组）")
    fig_height = px.box(filtered_members, x="role", y="cm", color="role",
                       labels={"cm": "身高 (cm)", "role": "队内担当"})
    fig_height.update_layout(height=350)
    st.plotly_chart(fig_height, width='stretch')

with tab2:
    st.title("👤 成员档案")
    
    # 搜索框
    search_name = st.text_input("🔍 搜索成员姓名", "")
    
    # 筛选成员
    search_df = filtered_members.copy()
    if search_name:
        search_df = search_df[search_df["name"].str.contains(search_name, case=False)]
    
    # 成员卡片
    for _, member in search_df.iterrows():
        with st.expander(f"📌 {member['name']}", expanded=True):
            col_info, col_avatar = st.columns([2, 1])
            
            with col_avatar:
                # 头像占位（首字母+代表色背景）
                initial = member["name"][0]
                st.markdown(f"""
                <div style="width: 120px; height: 120px; border-radius: 50%; background-color: {member['color']}; 
                            display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                    <span style="font-size: 48px; color: white; font-weight: bold;">{initial}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 代表色色块
                st.markdown(f"""
                <div style="margin-top: 10px; padding: 8px; background-color: {member['color']}; 
                            border-radius: 8px; text-align: center;">
                    <span style="color: white; font-weight: bold;">代表色</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_info:
                st.markdown("### 基本信息")
                info_data = pd.DataFrame({
                    "项目": ["姓名", "生日", "年龄", "血型", "身高", "国籍", "MBTI"],
                    "内容": [
                        member["name"],
                        member["birthday"].strftime("%Y-%m-%d"),
                        member["age"],
                        member["blood_type"],
                        f"{member['cm']} cm",
                        member["nationality"],
                        member["mbti"]
                    ]
                })
                st.table(info_data)
                
                # 队内担当标签
                st.markdown(f"### 队内担当")
                st.markdown(f"<span style='background-color: {member['color']}; color: white; padding: 4px 12px; border-radius: 12px;'>{member['role']}</span>", 
                           unsafe_allow_html=True)
    
    # 身高对比条形图
    st.subheader("📊 成员身高对比")
    sorted_df = filtered_members.sort_values("cm", ascending=False)
    fig_height_bar = px.bar(sorted_df, x="cm", y="name", orientation="h",
                           color="color", color_discrete_map=dict(zip(sorted_df["name"], sorted_df["color"])),
                           labels={"cm": "身高 (cm)", "name": "成员名"})
    fig_height_bar.update_layout(height=400)
    st.plotly_chart(fig_height_bar, width='stretch')

with tab3:
    st.title("🎵 歌曲数据库")
    
    # 统计摘要
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎶 总歌曲数", len(filtered_songs))
    
    with col2:
        avg_views = filtered_songs["views"].mean() / 100000000
        st.metric("📊 平均播放量（亿次）", f"{avg_views:.2f}")
    
    with col3:
        max_view_song = filtered_songs.loc[filtered_songs["views"].idxmax(), "song"]
        st.metric("🏆 最高播放量歌曲", max_view_song)
    
    # 数据表格
    display_songs = filtered_songs.copy()
    display_songs["views"] = display_songs["views"] / 100000000
    display_songs["likes"] = display_songs["likes"] / 10000
    
    def make_clickable(song):
        return f'<a href="https://www.youtube.com/search?q={song}+TWICE" target="_blank">🔗 试听</a>'
    
    display_songs["试听链接"] = display_songs["song"].apply(make_clickable)
    
    st.subheader("📋 歌曲列表")
    st.dataframe(display_songs[["song", "year", "title_yn", "album", "views", "likes", "试听链接"]], 
                 width='stretch',
                 column_config={
                     "views": st.column_config.NumberColumn("播放量（亿）", format="%.2f"),
                     "likes": st.column_config.NumberColumn("点赞数（万）", format="%.0f")
                 },
                 hide_index=True)
    
    # 图表区域
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📈 每年发行歌曲数量")
        year_counts = filtered_songs.groupby("year").size()
        fig_year = px.area(year_counts, x=year_counts.index, y=year_counts.values,
                          labels={"y": "歌曲数量", "year": "年份"})
        fig_year.update_layout(height=300)
        st.plotly_chart(fig_year, width='stretch')
    
    with col_chart2:
        st.subheader("📊 主打曲 vs 非主打曲播放量对比")
        title_compare = filtered_songs.groupby("title_yn")["views"].mean() / 100000000
        fig_title = px.bar(title_compare, x=title_compare.index, y=title_compare.values,
                          labels={"y": "平均播放量（亿次）", "title_yn": "类型"},
                          color=title_compare.index)
        fig_title.update_layout(height=300)
        st.plotly_chart(fig_title, width='stretch')
    
    # Top 10 高播放量歌曲
    st.subheader("🏆 Top 10 高播放量歌曲")
    top10 = filtered_songs.sort_values("views", ascending=False).head(10)
    top10["views"] = top10["views"] / 100000000
    fig_top10 = px.bar(top10, x="views", y="song", orientation="h",
                       labels={"views": "播放量（亿次）", "song": "歌曲名"},
                       color="views", color_continuous_scale="Blues")
    fig_top10.update_layout(height=400)
    st.plotly_chart(fig_top10, width='stretch')

with tab4:
    st.title("🎲 随机推荐")
    
    # 趣味冷知识
    fun_facts = {
        "林娜琏": "娜琏是团队中的'兔子担当'，因为她的门牙很可爱！",
        "俞定延": "定延喜欢打篮球，曾经是学校篮球队的成员。",
        "平井桃Momo": "Momo 的舞蹈实力超强，被称为'舞蹈机器'！",
        "凑崎纱夏Sana": "Sana 的日语非常流利，经常在日本节目中担任翻译。",
        "朴志效": "志效是团队的队长，也是成员们公认的'妈妈担当'。",
        "名井南Mina": "Mina 喜欢芭蕾舞，她的优雅气质来源于多年的芭蕾训练。",
        "金多贤": "多贤是团队的'表情包担当'，表情非常丰富！",
        "孙彩瑛": "彩瑛擅长说唱和创作，很多歌曲都有她参与作词。",
        "周子瑜": "子瑜是团队中年龄最小的成员，但身高却是最高的！"
    }
    
    # 推荐理由
    reasons = [
        "这首歌的副歌部分特别洗脑！",
        "舞台表演非常精彩，一定要看现场版！",
        "歌词很有深意，值得细细品味。",
        "旋律轻快，非常适合夏天听！",
        "成员们的和声太好听了！",
        "编舞非常有创意，充满力量感！"
    ]
    
    # 粉丝挑战题目
    quiz_questions = [
        {
            "question": "TWICE 的出道日期是哪一天？",
            "options": ["2015年10月20日", "2015年10月21日", "2015年10月22日", "2015年10月23日"],
            "answer": "2015年10月20日"
        },
        {
            "question": "TWICE 成员中谁是日本籍？",
            "options": ["娜琏、定延、志效", "Momo、Sana、Mina", "多贤、彩瑛、子瑜", "以上都不是"],
            "answer": "Momo、Sana、Mina"
        },
        {
            "question": "哪首歌让 TWICE 获得了第一个音乐节目一位？",
            "options": ["OOH-AHH하게", "Cheer Up", "TT", "Knock Knock"],
            "answer": "Cheer Up"
        },
        {
            "question": "TWICE 的官方粉丝名是什么？",
            "options": ["ONCE", "TWICE", "Candy", "JYP"],
            "answer": "ONCE"
        },
        {
            "question": "以下哪首不是 TWICE 的主打曲？",
            "options": ["Fancy", "Stuck in My Head", "Feel Special", "More & More"],
            "answer": "Stuck in My Head"
        }
    ]
    
    if st.button("✨ 今天推荐什么？", type="primary", width='stretch'):
        choice = random.randint(1, 3)
        
        if choice == 1:
            # 随机成员小百科
            member = random.choice(filtered_members.to_dict("records"))
            st.markdown(f"""
            <div style="border: 2px solid {member['color']}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: {member['color']};">👤 {member['name']} 小百科</h3>
                <div style="display: flex; align-items: center; margin: 15px 0;">
                    <div style="width: 80px; height: 80px; border-radius: 50%; background-color: {member['color']}; 
                                display: flex; align-items: center; justify-content: center; margin-right: 20px;">
                        <span style="font-size: 32px; color: white; font-weight: bold;">{member['name'][0]}</span>
                    </div>
                    <div>
                        <p><strong>担当：</strong>{member['role']}</p>
                        <p><strong>生日：</strong>{member['birthday'].strftime('%Y年%m月%d日')}</p>
                        <p><strong>国籍：</strong>{member['nationality']}</p>
                        <p><strong>MBTI：</strong>{member['mbti']}</p>
                    </div>
                </div>
                <div style="background-color: #f0f0f0; padding: 12px; border-radius: 8px;">
                    <p>💡 <strong>趣味冷知识：</strong>{fun_facts[member['name']]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif choice == 2:
            # 随机歌曲推荐
            song = random.choice(filtered_songs.to_dict("records"))
            reason = random.choice(reasons)
            st.markdown(f"""
            <div style="border: 2px solid #FF69B4; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: #FF69B4;">🎵 {song['song']}</h3>
                <p><strong>发行年份：</strong>{song['year']}</p>
                <p><strong>专辑：</strong>{song['album']}</p>
                <p><strong>类型：</strong>{'主打曲' if song['title_yn'] == '是' else '非主打曲'}</p>
                <p><strong>播放量：</strong>{song['views']/100000000:.1f}亿次</p>
                <div style="background-color: #fff0f5; padding: 12px; border-radius: 8px; margin-top: 15px;">
                    <p>🌟 <strong>推荐理由：</strong>{reason}</p>
                </div>
                <a href="https://www.youtube.com/search?q={song['song']}+TWICE" target="_blank" 
                   style="display: inline-block; margin-top: 15px; padding: 8px 20px; background-color: #FF69B4; 
                          color: white; border-radius: 8px; text-decoration: none;">
                    🎬 去 YouTube 试听
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # 随机粉丝挑战
            quiz = random.choice(quiz_questions)
            
            if "quiz_answer" not in st.session_state:
                st.session_state.quiz_answer = None
            
            st.markdown(f"""
            <div style="border: 2px solid #4169E1; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: #4169E1;">❓ {quiz['question']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for i, option in enumerate(quiz["options"]):
                st.button(f"{i+1}. {option}", key=f"quiz_option_{i}")
            
            if st.button("📝 显示答案", key="show_answer"):
                st.session_state.quiz_answer = quiz["answer"]
            
            if st.session_state.quiz_answer:
                st.markdown(f"""
                <div style="border: 2px solid #32CD32; border-radius: 12px; padding: 20px; margin-top: 15px; 
                            background-color: #f0fff0;">
                    <h4 style="color: #32CD32;">✅ 正确答案：{quiz['answer']}</h4>
                </div>
                """, unsafe_allow_html=True)

with tab5:
    st.title("📊 数据分析报告")
    
    # 分析结论
    st.subheader("📈 核心分析结论")
    
    # 1. 最常见的 MBTI 类型
    mbti_counts = members_df["mbti"].value_counts()
    top_mbti = mbti_counts.idxmax()
    top_mbti_ratio = (mbti_counts.max() / len(members_df)) * 100
    
    with st.info("**👥 MBTI 类型分布分析**"):
        st.write(f"团队中最常见的 MBTI 类型是 **{top_mbti}**，占比约 **{top_mbti_ratio:.1f}%**。")
    
    # 2. 哪一年发行的歌曲平均播放量最高
    year_views = songs_df.groupby("year")["views"].mean()
    best_year = year_views.idxmax()
    best_year_views = year_views.max() / 100000000
    
    with st.success("**🎵 年度播放量分析**"):
        st.write(f"**{best_year}年**发行的歌曲平均播放量最高，达到 **{best_year_views:.1f}亿次**。")
    
    # 3. 主打曲与非主打曲播放量对比
    title_avg = songs_df[songs_df["title_yn"] == "是"]["views"].mean()
    non_title_avg = songs_df[songs_df["title_yn"] == "否"]["views"].mean()
    ratio = title_avg / non_title_avg
    
    with st.info("**⭐ 主打曲 vs 非主打曲**"):
        st.write(f"主打曲的平均播放量是非主打曲的 **{ratio:.1f}倍**。")
    
    # 4. 身高最高和最矮的成员
    tallest = members_df.sort_values("cm", ascending=False).head(3)["name"].tolist()
    shortest = members_df.sort_values("cm", ascending=True).head(3)["name"].tolist()
    
    with st.success("**📏 身高分布分析**"):
        st.write(f"身高最高的三名成员：**{', '.join(tallest)}**")
        st.write(f"身高最矮的三名成员：**{', '.join(shortest)}**")
    
    # 高级图表
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 成员 MBTI 分布")
        mbti_data = members_df["mbti"].value_counts().reset_index()
        mbti_data.columns = ["mbti", "count"]
        fig_radar = px.pie(mbti_data, values="count", names="mbti", 
                          title="MBTI 类型分布")
        fig_radar.update_layout(height=400)
        st.plotly_chart(fig_radar, width='stretch')
    
    with col_chart2:
        st.subheader("📈 历年主打曲 vs 非主打曲数量")
        year_title = songs_df.groupby(["year", "title_yn"]).size().unstack(fill_value=0)
        fig_stack = px.bar(year_title, x=year_title.index, y=["是", "否"], 
                          barmode="stack", labels={"value": "歌曲数量", "year": "年份"},
                          title="主打曲(是) vs 非主打曲(否)")
        fig_stack.update_layout(height=400)
        st.plotly_chart(fig_stack, width='stretch')

# 底部版权信息
st.divider()
st.markdown("© 2025 ONCE 粉丝制作 · 数据仅供参考", unsafe_allow_html=True)
