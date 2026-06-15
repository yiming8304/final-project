import re
from datetime import datetime, timedelta

def validate_student_id(student_id):
    """验证学号格式"""
    if not student_id:
        return False, "学号不能为空"
    if len(student_id) != 12 or not student_id.isdigit():
        return False, "学号必须为12位数字"
    return True, ""

def validate_name(name):
    """验证姓名格式"""
    if not name.strip():
        return False, "姓名不能为空"
    if len(name) > 50:
        return False, "姓名长度不能超过50个字符"
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s]+$', name):
        return False, "姓名只能包含中文、英文和空格"
    return True, ""

def validate_date(booking_date):
    """验证预约日期"""
    today = datetime.now().date()
    max_date = today + timedelta(days=7)
    
    if booking_date < today:
        return False, "预约日期不能早于今天"
    if booking_date > max_date:
        return False, "最多只能预约7天后的座位"
    return True, ""

def check_timeout(created_at_str, timeout_minutes=30):
    """检查是否超时"""
    try:
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
    except ValueError:
        created_at = datetime.fromisoformat(created_at_str)
    
    now = datetime.now()
    diff = (now - created_at).total_seconds() / 60
    return diff > timeout_minutes

def generate_booking_id():
    """生成预约ID"""
    return str(int(datetime.now().timestamp() * 1000))

def format_time_slot(time_slot):
    """格式化时段显示"""
    time_slot_mapping = {
        "上午": "08:00 - 12:00",
        "下午": "14:00 - 18:00",
        "晚上": "18:30 - 22:00",
        "全天": "08:00 - 22:00"
    }
    return time_slot_mapping.get(time_slot, time_slot)

def get_time_slots():
    """获取时段列表"""
    return ["上午", "下午", "晚上", "全天"]

def get_campuses():
    """获取校区列表"""
    return ["寸金校区", "湖光校区"]

def format_datetime(dt_str):
    """格式化日期时间显示"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        dt = datetime.fromisoformat(dt_str)
    return dt.strftime('%Y-%m-%d %H:%M:%S')
