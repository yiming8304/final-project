import sqlite3
import os
from contextlib import contextmanager

DB_PATH = 'library.db'

@contextmanager
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """初始化数据库表"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 创建座位表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seats (
                id TEXT PRIMARY KEY,
                area TEXT NOT NULL,
                campus TEXT NOT NULL,
                row INTEGER NOT NULL,
                col INTEGER NOT NULL,
                status TEXT DEFAULT 'available' CHECK(status IN ('available', 'booked'))
            )
        ''')
        
        # 创建预约表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                studentId TEXT NOT NULL,
                name TEXT NOT NULL,
                seatId TEXT NOT NULL,
                area TEXT NOT NULL,
                campus TEXT NOT NULL,
                timeSlot TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'cancelled', 'timeout')),
                createdAt TEXT NOT NULL,
                FOREIGN KEY(seatId) REFERENCES seats(id)
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                studentId TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                campus TEXT NOT NULL
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_studentId ON bookings(studentId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_seatId ON bookings(seatId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(date)')
        
        conn.commit()
        
        # 初始化座位数据（如果为空）
        cursor.execute('SELECT COUNT(*) FROM seats')
        if cursor.fetchone()[0] == 0:
            init_seats(cursor)
            conn.commit()

def init_seats(cursor):
    """初始化座位数据"""
    seats = []
    
    # 寸金校区座位
    for area in ['A区', 'B区']:
        for row in range(1, 3):
            for col in range(1, 5):
                seat_id = f"寸金-{area[0]}{(row-1)*4 + col}"
                seats.append({
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
                seats.append({
                    'id': seat_id,
                    'area': area,
                    'campus': '湖光校区',
                    'row': row,
                    'col': col,
                    'status': 'available'
                })
    
    cursor.executemany('''
        INSERT INTO seats (id, area, campus, row, col, status)
        VALUES (:id, :area, :campus, :row, :col, :status)
    ''', seats)

# 用户操作
def get_user(student_id):
    """根据学号获取用户"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE studentId = ?', (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_user(student_id, name, campus):
    """添加新用户"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (studentId, name, campus)
            VALUES (?, ?, ?)
        ''', (student_id, name, campus))
        conn.commit()

# 座位操作
def get_seats_by_campus(campus):
    """获取指定校区的座位"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats WHERE campus = ?', (campus,))
        return [dict(row) for row in cursor.fetchall()]

def get_seat_by_id(seat_id):
    """根据ID获取座位"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats WHERE id = ?', (seat_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_seat_status(seat_id, status):
    """更新座位状态"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE seats SET status = ? WHERE id = ?', (status, seat_id))
        conn.commit()

def get_seat_status(seat_id):
    """获取座位状态"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM seats WHERE id = ?', (seat_id,))
        row = cursor.fetchone()
        return row['status'] if row else None

# 预约操作
def add_booking(booking_data):
    """添加预约记录"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bookings (id, studentId, name, seatId, area, campus, timeSlot, date, status, createdAt)
            VALUES (:id, :studentId, :name, :seatId, :area, :campus, :timeSlot, :date, :status, :createdAt)
        ''', booking_data)
        conn.commit()

def get_user_bookings(student_id):
    """获取用户的所有预约"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE studentId = ? ORDER BY date DESC, createdAt DESC', (student_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_booking_by_id(booking_id):
    """根据ID获取预约"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_booking_status(booking_id, status):
    """更新预约状态"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
        conn.commit()

def check_seat_booking(seat_id, date, time_slot):
    """检查座位在指定日期和时段是否已有预约"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE seatId = ? AND date = ? AND timeSlot = ? AND status = 'active'
        ''', (seat_id, date, time_slot))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_daily_booking_count(student_id, date):
    """获取用户某天的预约数量"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM bookings 
            WHERE studentId = ? AND date = ? AND status = 'active'
        ''', (student_id, date))
        return cursor.fetchone()[0]

def get_timeout_bookings():
    """获取超时未签到的预约（超过30分钟）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM bookings 
            WHERE status = 'active'
        ''')
        return [dict(row) for row in cursor.fetchall()]

# 统计操作
def get_campus_area_stats(campus, area):
    """获取指定校区区域的座位统计"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM seats 
            WHERE campus = ? AND area = ? 
            GROUP BY status
        ''', (campus, area))
        result = {}
        for row in cursor.fetchall():
            result[row['status']] = row['count']
        return result

def get_all_seats():
    """获取所有座位"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats')
        return [dict(row) for row in cursor.fetchall()]

def get_seats_by_area(campus, area):
    """获取指定校区区域的座位"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats WHERE campus = ? AND area = ?', (campus, area))
        return [dict(row) for row in cursor.fetchall()]

def get_areas_by_campus(campus):
    """获取指定校区的所有区域"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT area FROM seats WHERE campus = ?', (campus,))
        return [row['area'] for row in cursor.fetchall()]
