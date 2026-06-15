import streamlit as st
from datetime import datetime, timedelta
import database as db
import utils

# ===================== 页面基础配置 =====================
st.set_page_config(
    page_title="图书馆座位预约系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
db.init_db()

# ===================== 会话状态初始化 =====================
if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "selected_campus" not in st.session_state:
    st.session_state.selected_campus = None
if "booking_submitted" not in st.session_state:
    st.session_state.booking_submitted = False

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
# 1. 登录页面
if select_menu == "🔐 用户登录":
    st.title("🔐 用户登录")
    st.divider()
    
    with st.form("login_form"):
        student_id = st.text_input("请输入12位学号", max_chars=12, placeholder="请输入12位数字学号")
        user_name = st.text_input("请输入姓名")
        selected_campus = st.selectbox("选择校区", utils.get_campuses())
        login_btn = st.form_submit_button("立即登录")
        
        if login_btn:
            # 校验学号格式
            valid, msg = utils.validate_student_id(student_id)
            if not valid:
                st.error(f"❌ {msg}")
            else:
                # 校验姓名格式
                valid, msg = utils.validate_name(user_name)
                if not valid:
                    st.error(f"❌ {msg}")
                else:
                    # 查找已有用户
                    match_user = db.get_user(student_id)
                    
                    if match_user:
                        st.session_state.login_status = True
                        st.session_state.current_user = match_user
                        st.session_state.selected_campus = selected_campus
                        st.success(f"✅ 登录成功！欢迎你，{user_name}")
                        st.rerun()
                    else:
                        # 新用户，自动注册
                        db.add_user(student_id, user_name, selected_campus)
                        new_user = db.get_user(student_id)
                        
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
    
    # 显示用户信息卡片
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"👤 用户名：{user['name']}")
        with col2:
            st.info(f"📝 学号：{user['studentId']}")
        with col3:
            st.info(f"📍 当前校区：{campus}")
    
    # 显示预约提醒
    st.divider()
    st.subheader("📅 今日预约提醒")
    today = datetime.now().date().isoformat()
    bookings = db.get_user_bookings(user['studentId'])
    today_bookings = [b for b in bookings if b['date'] == today and b['status'] == 'active']
    
    if today_bookings:
        for booking in today_bookings:
            st.warning(f"座位：{booking['seatId']} | 区域：{booking['area']} | 时段：{booking['timeSlot']} ({utils.format_time_slot(booking['timeSlot'])})")
    else:
        st.info("今日暂无预约")
    
    st.divider()
    st.markdown("""
    ### 📖 系统说明
    - 支持寸金/湖光两大校区座位在线预约
    - 可查看对应校区座位实时占用状态
    - 支持预约、取消预约操作
    - 每人每天最多预约2个座位
    - 预约后30分钟内未签到将自动取消
    
    ### ⚠️ 注意事项
    - 请合理使用图书馆资源，文明就座
    - 如需取消预约，请提前操作
    - 多次违约将影响您的预约权限
    """)

# 3. 座位预约
elif select_menu == "🪑 座位预约" and st.session_state.login_status:
    st.title("🪑 座位预约")
    st.divider()
    
    campus = st.session_state.selected_campus
    areas = db.get_areas_by_campus(campus)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        choose_area = st.selectbox("选择区域", areas)
    with col2:
        # 限制日期范围
        min_date = datetime.now().date()
        max_date = min_date + timedelta(days=7)
        choose_date = st.date_input("选择预约日期", value=min_date, min_value=min_date, max_value=max_date)
    with col3:
        time_slot = st.selectbox("选择时段", utils.get_time_slots(), 
                                format_func=lambda x: f"{x} ({utils.format_time_slot(x)})")
    
    # 获取该区域座位
    seats = db.get_seats_by_area(campus, choose_area)
    
    if not seats:
        st.warning("当前区域暂无座位")
    else:
        # 座位可视化网格
        st.subheader("座位选择")
        max_row = max(s["row"] for s in seats)
        max_col = max(s["col"] for s in seats)
        
        selected_seat_id = None
        for row in range(1, max_row + 1):
            cols = st.columns(max_col)
            for col in range(1, max_col + 1):
                seat = next((s for s in seats if s["row"] == row and s["col"] == col), None)
                if seat:
                    is_available = seat["status"] == "available"
                    button_label = f"{seat['id'].split('-')[1]}"
                    button_key = f"seat_{seat['id']}"
                    
                    with cols[col - 1]:
                        if st.button(
                            button_label,
                            key=button_key,
                            type="primary" if is_available else "secondary",
                            disabled=not is_available,
                            use_container_width=True,
                            help=f"座位: {seat['id']} - {'空闲' if is_available else '已预约'}"
                        ):
                            selected_seat_id = seat["id"]
        
        # 显示选中的座位信息
        if selected_seat_id:
            st.success(f"已选择座位：{selected_seat_id}")
        
        st.divider()
        submit_btn = st.button("提交预约", type="primary", 
                             disabled=selected_seat_id is None or st.session_state.booking_submitted)
        
        if submit_btn:
            st.session_state.booking_submitted = True
            
            # 校验日期
            valid, msg = utils.validate_date(choose_date)
            if not valid:
                st.error(f"❌ {msg}")
                st.session_state.booking_submitted = False
            else:
                # 检查用户当天预约数量限制
                date_str = str(choose_date)
                booking_count = db.get_user_daily_booking_count(st.session_state.current_user["studentId"], date_str)
                if booking_count >= 2:
                    st.error("❌ 每人每天最多预约2个座位")
                    st.session_state.booking_submitted = False
                else:
                    # 检查座位状态
                    seat_info = db.get_seat_by_id(selected_seat_id)
                    if not seat_info or seat_info["status"] != "available":
                        st.error("❌ 当前座位已被预约，无法选择")
                        st.session_state.booking_submitted = False
                    else:
                        # 检查重复预约
                        exist_book = db.check_seat_booking(selected_seat_id, date_str, time_slot)
                        if exist_book:
                            st.error("❌ 该座位此时段已被他人预约")
                            st.session_state.booking_submitted = False
                        else:
                            # 新增预约记录
                            new_booking = {
                                "id": utils.generate_booking_id(),
                                "studentId": st.session_state.current_user["studentId"],
                                "name": st.session_state.current_user["name"],
                                "seatId": selected_seat_id,
                                "area": choose_area,
                                "campus": campus,
                                "timeSlot": time_slot,
                                "date": date_str,
                                "status": "active",
                                "createdAt": datetime.now().isoformat()
                            }
                            db.add_booking(new_booking)
                            
                            # 更新座位状态
                            db.update_seat_status(selected_seat_id, "booked")
                            
                            st.success("✅ 座位预约成功！可在「我的预约」中查看记录")
                            st.session_state.booking_submitted = False
                            st.rerun()

# 4. 我的预约
elif select_menu == "📋 我的预约" and st.session_state.login_status:
    st.title("📋 我的预约记录")
    st.divider()
    
    student_id = st.session_state.current_user["studentId"]
    bookings = db.get_user_bookings(student_id)
    
    # 搜索和筛选
    col1, col2 = st.columns(2)
    with col1:
        search_keyword = st.text_input("搜索座位号或区域")
    with col2:
        status_filter = st.selectbox("状态筛选", ["全部", "正常预约", "已取消", "已超时"])
    
    # 过滤预约
    filtered_bookings = bookings
    if search_keyword:
        filtered_bookings = [b for b in filtered_bookings 
                            if search_keyword in b["seatId"] or search_keyword in b["area"]]
    
    status_map = {"全部": None, "正常预约": "active", "已取消": "cancelled", "已超时": "timeout"}
    if status_filter != "全部":
        filtered_bookings = [b for b in filtered_bookings if b["status"] == status_map[status_filter]]
    
    # 分页处理
    page_size = 5
    total_bookings = len(filtered_bookings)
    total_pages = (total_bookings + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
    else:
        page = 1
    
    start = (page - 1) * page_size
    end = start + page_size
    page_bookings = filtered_bookings[start:end]
    
    if not filtered_bookings:
        st.info("暂无预约记录")
    else:
        for book in page_bookings:
            status_text = {"active": "正常预约", "cancelled": "已取消", "timeout": "已超时"}[book["status"]]
            with st.expander(f"预约单号：{book['id']} | 座位：{book['seatId']} | {status_text}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**区域**：{book['area']}")
                    st.write(f"**校区**：{book['campus']}")
                with col2:
                    st.write(f"**日期**：{book['date']}")
                    st.write(f"**时段**：{book['timeSlot']} ({utils.format_time_slot(book['timeSlot'])})")
                with col3:
                    st.write(f"**状态**：{status_text}")
                    st.write(f"**创建时间**：{utils.format_datetime(book['createdAt'])}")
                
                if book["status"] == "active":
                    if st.button(f"取消该预约", key=book["id"]):
                        db.update_booking_status(book["id"], "cancelled")
                        db.update_seat_status(book["seatId"], "available")
                        st.success("✅ 预约已取消")
                        st.rerun()
        
        # 分页信息
        if total_pages > 1:
            st.write(f"显示第 {start + 1}-{min(end, total_bookings)} 条，共 {total_bookings} 条记录")

# 5. 座位状态查看
elif select_menu == "📊 座位状态查看" and st.session_state.login_status:
    st.title("📊 全场座位状态")
    st.divider()
    
    campus = st.session_state.selected_campus
    areas = db.get_areas_by_campus(campus)
    
    view_area = st.selectbox("选择查看区域", areas)
    seats = db.get_seats_by_area(campus, view_area)
    
    # 显示座位状态表格
    st.dataframe(seats, use_container_width=True, hide_index=True)
    
    # 统计数据
    stats = db.get_campus_area_stats(campus, view_area)
    total = stats.get('available', 0) + stats.get('booked', 0)
    free = stats.get('available', 0)
    used = stats.get('booked', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总座位数", total)
    with col2:
        st.metric("空闲座位", free, delta_color="normal")
    with col3:
        st.metric("已预约", used, delta_color="inverse")
    
    # 座位占用率
    if total > 0:
        occupancy_rate = (used / total) * 100
        st.progress(int(occupancy_rate))
        st.write(f"座位占用率：{occupancy_rate:.1f}%")

# 6. 退出登录
elif select_menu == "🚪 退出登录" and st.session_state.login_status:
    st.title("🚪 退出登录")
    st.divider()
    st.warning("确定要退出当前账号吗？")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("确认退出", type="primary"):
            st.session_state.login_status = False
            st.session_state.current_user = None
            st.session_state.selected_campus = None
            st.success("✅ 已退出登录")
            st.rerun()
    with col2:
        if st.button("返回首页"):
            st.rerun()

# 未登录拦截
else:
    st.warning("⚠️ 请先在侧边栏完成登录，再使用系统功能")
