import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="TWICE 歌曲聊天机器人", page_icon="🎵")

st.title("🎵 TWICE 歌曲聊天机器人")
st.markdown("你好！我是TWICE歌曲专家，可以和你聊聊TWICE的歌曲、风格、年份和成绩！")

twice_songs = {
    "Cheer Up": {
        "年份": 2016,
        "风格": "Bubblegum Pop, Dance",
        "成绩": "年榜第一，Melon年榜冠军，SBS歌谣大战大赏",
        "特色": "标志性的'Sana shy shy shy'成为韩国流行语，活泼可爱的校园风"
    },
    "TT": {
        "年份": 2016,
        "风格": "Dance Pop, Halloween Theme",
        "成绩": "连续13周音源榜前十，YouTube播放量破亿",
        "特色": "可爱的TT手势舞风靡全亚洲，万圣节主题造型"
    },
    "Knock Knock": {
        "年份": 2017,
        "风格": "Pop, Dance",
        "成绩": "实时All Kill，Melon周榜冠军",
        "特色": "轻快的敲门节奏，延续了TT的故事线"
    },
    "Signal": {
        "年份": 2017,
        "风格": "Dance Pop, Electronic",
        "成绩": "获得12个一位，MAMA最佳女团舞蹈表演",
        "特色": "外星人主题，独特的编舞手势"
    },
    "Likey": {
        "年份": 2017,
        "风格": "Dance Pop, Electronic",
        "成绩": "YouTube最快破亿K-pop女团MV",
        "特色": "在温哥华拍摄，展现少女对恋爱的期待"
    },
    "Heart Shaker": {
        "年份": 2017,
        "风格": "Pop Rock",
        "成绩": "实时All Kill，年末各大颁奖典礼表演曲目",
        "特色": "清爽的电吉他编曲，传递直白的告白心意"
    },
    "What is Love?": {
        "年份": 2018,
        "风格": "Dance Pop, Bubblegum Pop",
        "成绩": "Gaon榜双白金认证，YouTube播放量超6亿",
        "特色": "致敬多部电影经典场景，充满好奇心的少女情怀"
    },
    "Dance The Night Away": {
        "年份": 2018,
        "风格": "EDM, Pop",
        "成绩": "夏日音源强者，连续两周音乐节目一位",
        "特色": "夏日海滩派对氛围，清爽活力满分"
    },
    "Yes or Yes": {
        "年份": 2018,
        "风格": "Pop, Dance",
        "成绩": "首周销量破纪录，iTunes 17个国家和地区第一",
        "特色": "强势告白风格，只能选择'Yes'的俏皮设定"
    },
    "Fancy": {
        "年份": 2019,
        "风格": "Electropop, Dance",
        "成绩": "美国Billboard世界数字歌曲销售榜第一",
        "特色": "转型成熟风格的开端，梦幻电子音效"
    },
    "Feel Special": {
        "年份": 2019,
        "风格": "Dance Pop, R&B",
        "成绩": "Gaon榜白金认证，被誉为人歌合一的作品",
        "特色": "JYP为成员量身打造的治愈歌曲，歌词充满感恩"
    },
    "More & More": {
        "年份": 2020,
        "风格": "Tropical House, Dance",
        "成绩": "首周销量破33万，当时女团最高纪录",
        "特色": "热带丛林风格，编舞充满力量感"
    },
    "I Can't Stop Me": {
        "年份": 2020,
        "风格": "Synth-pop, Retro",
        "成绩": "进入Billboard Hot 100第83位，首次入榜",
        "特色": "80年代复古合成器风格，展现克制与欲望的矛盾"
    },
    "Alcohol-Free": {
        "年份": 2021,
        "风格": "Bossa Nova, Pop",
        "成绩": "Melon日榜第一，展现全新音乐尝试",
        "特色": "夏日鸡尾酒主题，轻快的巴萨诺瓦风格"
    },
    "Scientist": {
        "年份": 2021,
        "风格": "Pop, R&B",
        "成绩": "专辑首周销量破66万，自身最高纪录",
        "特色": "实验室主题，传达爱情不需要过度分析的讯息"
    },
    "Talk that Talk": {
        "年份": 2022,
        "风格": "Pop, Dance",
        "成绩": "Billboard 200第3位，创自身最高排名",
        "特色": "Y2K复古风格，庆祝出道7周年的粉丝颂"
    },
    "Set Me Free": {
        "年份": 2023,
        "风格": "Pop, Dance",
        "成绩": "Billboard 200第2位，创自身最高排名",
        "特色": "摆脱束缚追求自由，强烈的节奏和编舞"
    },
    "Moonlight Sunrise": {
        "年份": 2023,
        "风格": "R&B, Pop",
        "成绩": "Billboard Hot 100第84位",
        "特色": "全英文单曲，浪漫性感的R&B风格"
    },
    "One Spark": {
        "年份": 2024,
        "风格": "Pop Rock, Dance",
        "成绩": "专辑首周销量破百万",
        "特色": "出道9周年纪念曲，回顾与ONCE的旅程"
    }
}


def build_system_prompt(songs):
    songs_text = ""
    for name, info in songs.items():
        songs_text += f"- {name} (年份: {info['年份']}, 风格: {info['风格']}, 成绩: {info['成绩']}, 特色: {info['特色']})\n"

    return f"""# 角色设定
你是一位精通 K-pop 女团 TWICE（트와이스 / トゥワイス）的热情粉丝向导与百科助手。
你熟悉 TWICE 的所有成员、出道历程、专辑、代表曲、小分队、粉丝文化与趣闻，
并能结合本次对话上下文进行多轮连贯回答。

# TWICE 基本资料
- 团名：TWICE（트와이스 / トゥワイス），寓意"用音乐和舞台给观众双倍感动"
- 所属公司：JYP Entertainment
- 出道：2015年10月20日通过生存节目《SIXTEEN》选拔，以迷你一辑《The Story Begins》出道，主打《Like OOH-AHH》
- 日本出道：2017年6月28日《#TWICE》，美国首支英文单曲《The Feels》(2021)
- 粉丝名：ONCE（只要 ONCE 给一次爱，TWICE 会回以两倍的爱）
- 应援色：杏黄 + 霓虹洋红；应援棒 Candy Bong
- 小分队：MISAMO（Mina、Sana、Momo）— 2023年日本出道

# 九名成员
1. 娜琏 Nayeon(임나연) — 1995.09.22 韩国首尔 — Lead Vocal / Center，首位 Solo(2022《IM NAYEON》)
2. 定延 Jeongyeon(유정연) — 1996.11.01 韩国水原 — Lead Vocal，中性魅力
3. Momo(平井桃/ひらい もも) — 1996.11.09 日本京都 — Main Dancer / Sub Rapper，"舞蹈机器"
4. Sana(凑崎纱夏/みなとざき さな) — 1996.12.29 日本大阪 — Sub Vocal，经典"Shy Shy Shy~"
5. 志效 Jihyo(박지효) — 1997.02.01 韩国九里 — Leader / Main Vocal，练习生最长(10年)
6. Mina(名井南/みょうい みな) — 1997.03.24 美籍日裔德州→神户 — Main Dancer / Sub Vocal，芭蕾背景
7. 多贤 Dahyun(김다현) — 1998.05.28 韩国城南 — Lead Rapper / Sub Vocal，活泼搞笑担当
8. 彩瑛 Chaeyoung(손채영) — 1999.04.23 韩国首尔 — Main Rapper / Sub Vocal，参与作词作曲，艺术感强
9. 子瑜 Tzuyu(周子瑜/Chou Tzu-yu) — 1999.06.14 台湾台南 — Lead Dancer / Sub Vocal / Maknae(忙内)

# 代表韩语主打曲
Like OOH-AHH、Cheer Up（"焗烤～"梗）、TT、Knock Knock、Signal、Likey、What is Love?、Dance The Night Away、Yes or Yes、FANCY、Feel Special、I CAN'T STOP ME、SCIENTIST、SET ME FREE、Talk that Talk、Moonlight Sunrise、I GOT YOU、Strategy 等

# 日本代表作
One More Time、Candy Pop、Wake Me Up、BDZ、Fake & True、Hare Hare、DIVE 等

# 歌曲详细数据库（请优先使用此数据回答歌曲相关问题）
{songs_text}
# 应答规范
- 用热情、亲切、带一点 K-pop 粉丝感的语气回答，可适当用 🎤💖✨ 等 emoji 点缀
- 结合对话上文理解追问题（如用户先问成员数，再问"日本人有哪些？"要直接答）
- 回答歌曲相关问题时，请优先参考上面提供的"歌曲详细数据库"中的信息
- 不知道的细节诚实说"这个我不太确定哦～"，禁止编造年月日或虚构奖项
- 用户用中文问 → 中文答；英文问 → 英文答；可夹杂韩文艺名/日文假名辅助说明
- 若用户只是打招呼，简单介绍自己并邀请问 TWICE 相关问题
"""


with st.sidebar:
    st.header("⚙️ DeepSeek API 配置")
    api_key = st.text_input(
        "请输入 DeepSeek API Key",
        type="password",
        help="在 https://platform.deepseek.com 获取 API Key",
        value=st.session_state.get("api_key", "")
    )
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API Key 已保存")

    model_name = st.selectbox(
        "选择模型",
        ["deepseek-v4-flash", "deepseek-v4-pro"],
        index=0,
        help="v4-flash: 快速高效，适合日常对话；v4-pro: 强推理能力，适合复杂任务"
    )

    st.divider()
    st.caption("提示：API Key 仅保存在当前会话中，不会被存储到任何地方。")

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = build_system_prompt(twice_songs)

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = "你好！我是TWICE歌曲专家🎵\n\n我可以帮你了解：\n- TWICE的热门歌曲\n- 歌曲的发行年份\n- 音乐风格\n- 获奖成绩\n- 歌曲特色\n\n试着问我：'推荐一首夏日歌曲' 或 'Tell me about Fancy'"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入你想了解的TWICE歌曲..."):
    if not st.session_state.get("api_key"):
        st.warning("⚠️ 请先在左侧边栏输入你的 DeepSeek API Key！")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = OpenAI(
        api_key=st.session_state.api_key,
        base_url="https://api.deepseek.com"
    )

    api_messages = [{"role": "system", "content": st.session_state.system_prompt}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=model_name,
                messages=api_messages,
                stream=True,
                temperature=0.7
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})
    except Exception as e:
        st.error(f"❌ 调用 API 时出错：{str(e)}")
        st.session_state.messages.pop()
