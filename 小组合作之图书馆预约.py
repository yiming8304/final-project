import streamlit as st
import json
import os
from datetime import datetime

# ===================== 页面基础配置 =====================
st.set_page_config(
    page_title="图书馆座位预约系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== 数据路径与工具函数 =====================
DATA_DIR = 'data'
SEATS_FILE = os.path.join(DATA_DIR, 'seats.json')
BOOKINGS_FILE = os.path.join(DATA_DIR, 'bookings.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def ensure_data_dir():
    """确保数据文件夹存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def read_json_file(file_path, default_value):
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def write_json_file(file_path, data):
    """写入JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_data():
    """初始化基础数据（座位、用户、预约表）"""
    ensure_data_dir()
    
    # 初始化座位数据（按校区划分）
    if not os.path.exists(SEATS_FILE):
        initial_seats = []
        
        # 寸金校区座位
        for area in ['A区', 'B区']:
            for row in range(1, 3):
                for col in range(1, 5):
                    seat_id = f"寸金-{area[0]}{(row-1)*4 + col}"
                    initial_seats.append({
                        'id': seat_id,
                        'area': area,
                        'campus': '寸金校区',
                        'row': row,
                        'col': col,
                        'status': 'available'
                    })
        
        # 湖光校区座位
        for area in ['C区', 'D区']:
            for row in range(1, 3):
                for col in range(1, 5):
                    seat_id = f"湖光-{area[0]}{(row-1)*4 + col}"
                    initial_seats.append({
                        'id': seat_id,
                        'area': area,
                        'campus': '湖光校区',
                        'row': row,
                        'col': col,
                        'status': 'available'
                    })
        
        write_json_file(SEATS_FILE, initial_seats)
    
    # 初始化预约表
    if not os.path.exists(BOOKINGS_FILE):
        write_json_file(BOOKINGS_FILE, [])
    
    # 用户表现在不做固定初始化，改为动态登录，这里只创建空文件
    if not os.path.exists(USERS_FILE):
        write_json_file(USERS_FILE, [])

# 初始化数据
init_data()

# ===================== 会话状态初始化 =====================
if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "selected_campus" not in st.session_state:
    st.session_state.selected_campus = None

# ===================== 侧边栏导航 =====================
with st.sidebar:
    st.title("📚 图书馆预约系统")
    st.divider()
    
    if not st.session_state.login_status:
        menu = ["🔐 用户登录"]
    else:
        menu = ["🏠 首页", "🪑 座位预约", "📋 我的预约", "📊 座位状态查看", "🚪 退出登录"]
        
    select_menu = st.radio("功能菜单", menu)

# ===================== 页面主体逻辑 =====================
# 1. 登录页面（学号改为任意12位数字）
if select_menu == "🔐 用户登录":
    st.title("🔐 用户登录")
    st.divider()
    
    with st.form("login_form"):
        student_id = st.text_input("请输入12位学号", max_chars=12, placeholder="请输入12位数字学号")
        user_name = st.text_input("请输入姓名")
        selected_campus = st.selectbox("选择校区", ["寸金校区", "湖光校区"])
        login_btn = st.form_submit_button("立即登录")
        
        if login_btn:
            # 校验学号格式
            if len(student_id) != 12 or not student_id.isdigit():
                st.error("❌ 学号必须为12位数字，请重新输入")
            elif not user_name.strip():
                st.error("❌ 姓名不能为空，请重新输入")
            else:
                users = read_json_file(USERS_FILE, [])
                # 查找已有用户
                match_user = next(
                    (u for u in users if u["studentId"] == student_id),
                    None
                )
                
                if match_user:
                    # 已有用户，直接登录
                    st.session_state.login_status = True
                    st.session_state.current_user = match_user
                    st.session_state.selected_campus = selected_campus
                    st.success(f"✅ 登录成功！欢迎你，{user_name}")
                    st.rerun()
                else:
                    # 新用户，自动注册
                    new_user = {
                        "studentId": student_id,
                        "name": user_name,
                        "campus": selected_campus
                    }
                    users.append(new_user)
                    write_json_file(USERS_FILE, users)
                    
                    st.session_state.login_status = True
                    st.session_state.current_user = new_user
                    st.session_state.selected_campus = selected_campus
                    st.success(f"✅ 新用户注册并登录成功！欢迎你，{user_name}")
                    st.rerun()

# 2. 首页
elif select_menu == "🏠 首页" and st.session_state.login_status:
    st.title("🏠 图书馆座位预约系统 - 首页")
    st.divider()
    user = st.session_state.current_user
    campus = st.session_state.selected_campus
    st.info(f"👋 欢迎你，{user['name']}（学号：{user['studentId']}）\n📍 当前校区：{campus}")
    
    st.markdown("""
    ### 系统说明
    1. 支持寸金/湖光两大校区座位在线预约
    2. 可查看对应校区座位实时占用状态
    3. 支持预约、取消预约操作
    4. 请合理使用图书馆资源，文明就座
    """)

# 3. 座位预约（已修复 None.split 报错，添加可视化）
elif select_menu == "🪑 座位预约" and st.session_state.login_status:
    st.title("🪑 座位预约")
    st.divider()
    
    campus = st.session_state.selected_campus
    seats = read_json_file(SEATS_FILE, [])
    
    # 补全旧数据 campus 字段
    for seat in seats:
        if "campus" not in seat:
            seat["campus"] = "寸金校区"
    write_json_file(SEATS_FILE, seats)
    
    # 筛选当前校区座位
    campus_seats = [s for s in seats if s["campus"] == campus]
    areas = list(set(s["area"] for s in campus_seats))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        choose_area = st.selectbox("选择区域", areas)
    with col2:
        choose_date = st.date_input("选择预约日期", datetime.now())
    with col3:
        time_slot = st.selectbox("选择时段", ["上午", "下午", "晚上", "全天"])
    
    # 筛选当前区域座位
    area_seats = [s for s in campus_seats if s["area"] == choose_area]
    
    # 可视化座位网格
    st.subheader("座位选择（绿色可预约，灰色已预约）")
    st.markdown("---")
    
    if not area_seats:
        st.info("当前区域暂无座位，请更换其他区域！")
        real_seat_id = None
    else:
        # 计算网格大小
        max_row = max(s["row"] for s in area_seats)
        max_col = max(s["col"] for s in area_seats)
        
        # 使用会话状态存储选中的座位
        if "selected_seat" not in st.session_state:
            st.session_state.selected_seat = None
        
        # 显示座位网格
        for row in range(1, max_row + 1):
            cols = st.columns(max_col)
            for col in range(1, max_col + 1):
                seat = next((s for s in area_seats if s["row"] == row and s["col"] == col), None)
                if seat:
                    is_available = seat["status"] == "available"
                    seat_label = seat["id"].split("-")[1]  # 提取座位编号如 "A1"
                    button_key = f"seat_{seat['id']}"
                    
                    with cols[col - 1]:
                        if st.button(
                            seat_label,
                            key=button_key,
                            type="primary" if is_available else "secondary",
                            disabled=not is_available,
                            use_container_width=True,
                            help=f"座位: {seat['id']}\n状态: {'空闲' if is_available else '已预约'}"
                        ):
                            st.session_state.selected_seat = seat["id"]
        
        # 显示选中状态
        real_seat_id = st.session_state.selected_seat
        if real_seat_id:
            st.success(f"✅ 已选择座位：{real_seat_id}")
        else:
            st.info("请点击上方座位网格选择座位（绿色按钮为可预约座位）")
    
    st.divider()
    if st.button("提交预约", type="primary", disabled=real_seat_id is None):
        # 二次校验是否选中座位
        if real_seat_id is None:
            st.error("❌ 请先选择有效座位！")
        else:
            bookings = read_json_file(BOOKINGS_FILE, [])
            seat_info = next((s for s in seats if s["id"] == real_seat_id), None)
            
            # 校验座位状态
            if not seat_info or seat_info["status"] == "booked":
                st.error("❌ 当前座位已被预约，无法选择")
            else:
                # 校验重复预约
                exist_book = next(
                    (b for b in bookings 
                     if b["seatId"] == real_seat_id 
                     and b["date"] == str(choose_date) 
                     and b["timeSlot"] == time_slot
                     and b["status"] == "active"),
                    None
                )
                if exist_book:
                    st.error("❌ 该座位此时段已被他人预约")
                else:
                    # 新增预约记录
                    new_booking = {
                        "id": str(int(datetime.now().timestamp() * 1000)),
                        "studentId": st.session_state.current_user["studentId"],
                        "name": st.session_state.current_user["name"],
                        "seatId": real_seat_id,
                        "area": choose_area,
                        "campus": campus,
                        "timeSlot": time_slot,
                        "date": str(choose_date),
                        "status": "active",
                        "createdAt": datetime.now().isoformat()
                    }
                    bookings.append(new_booking)
                    write_json_file(BOOKINGS_FILE, bookings)
                    
                    # 更新座位状态
                    seat_info["status"] = "booked"
                    write_json_file(SEATS_FILE, seats)
                    
                    st.success("✅ 座位预约成功！可在「我的预约」中查看记录")
                    st.rerun()

# 4. 我的预约
elif select_menu == "📋 我的预约" and st.session_state.login_status:
    st.title("📋 我的预约记录")
    st.divider()
    
    student_id = st.session_state.current_user["studentId"]
    bookings = read_json_file(BOOKINGS_FILE, [])
    my_bookings = [b for b in bookings if b["studentId"] == student_id]
    
    if not my_bookings:
        st.info("暂无预约记录")
    else:
        for book in my_bookings:
            with st.expander(f"预约单号：{book['id']} | 座位：{book['seatId']} | 校区：{book['campus']}"):
                st.write(f"区域：{book['area']}")
                st.write(f"日期：{book['date']}")
                st.write(f"时段：{book['timeSlot']}")
                st.write(f"状态：{'正常预约' if book['status'] == 'active' else '已取消'}")
                st.write(f"创建时间：{book['createdAt']}")
                
                if book["status"] == "active":
                    if st.button(f"取消该预约", key=book["id"]):
                        book_idx = bookings.index(book)
                        bookings[book_idx]["status"] = "cancelled"
                        write_json_file(BOOKINGS_FILE, bookings)
                        
                        # 恢复座位状态
                        seats = read_json_file(SEATS_FILE, [])
                        seat = next((s for s in seats if s["id"] == book["seatId"]), None)
                        if seat:
                            seat["status"] = "available"
                            write_json_file(SEATS_FILE, seats)
                        
                        st.success("✅ 预约已取消")
                        st.rerun()

# 5. 座位状态查看
elif select_menu == "📊 座位状态查看" and st.session_state.login_status:
    st.title("📊 全场座位状态")
    st.divider()
    
    campus = st.session_state.selected_campus
    seats = read_json_file(SEATS_FILE, [])
    
    # 补全旧数据
    for seat in seats:
        if "campus" not in seat:
            seat["campus"] = "寸金校区"
    write_json_file(SEATS_FILE, seats)
    
    campus_seats = [s for s in seats if s["campus"] == campus]
    areas = list(set(s["area"] for s in campus_seats))
    view_area = st.selectbox("选择查看区域", areas)
    
    filter_seats = [s for s in campus_seats if s["area"] == view_area]
    st.dataframe(filter_seats, use_container_width=True)
    
    # 统计数据
    total = len(filter_seats)
    free = len([s for s in filter_seats if s["status"] == "available"])
    used = total - free
    st.metric(label=f"{campus} - {view_area} 统计", value=f"总计{total}座 | 空闲{free}座 | 已预约{used}座")

# 6. 退出登录
elif select_menu == "🚪 退出登录" and st.session_state.login_status:
    st.title("🚪 退出登录")
    st.divider()
    st.warning("确定要退出当前账号吗？")
    if st.button("确认退出"):
        st.session_state.login_status = False
        st.session_state.current_user = None
        st.session_state.selected_campus = None
        st.success("✅ 已退出登录")
        st.success("📚 今日学习辛苦啦，欢迎下次再来图书馆努力学习！")
        st.rerun()

# 未登录拦截
else:
    st.warning("⚠️ 请先在侧边栏完成登录，再使用系统功能")