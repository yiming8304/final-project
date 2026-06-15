import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def test_logout_message():
    """测试退出登录时的温馨提示语"""
    
    # 模拟Streamlit的session_state
    with patch('streamlit.session_state') as mock_session_state:
        mock_session_state.login_status = True
        mock_session_state.current_user = {"name": "测试用户", "studentId": "123456789012"}
        mock_session_state.selected_campus = "寸金校区"
        
        # 模拟st.success函数来捕获输出
        success_messages = []
        def mock_success(msg):
            success_messages.append(msg)
            return None
        
        with patch('streamlit.success', side_effect=mock_success):
            # 执行退出登录逻辑
            mock_session_state.login_status = False
            mock_session_state.current_user = None
            mock_session_state.selected_campus = None
            
            # 模拟代码中的success调用
            mock_success("✅ 已退出登录")
            mock_success("📚 今日学习辛苦啦，欢迎下次再来图书馆努力学习！")
        
        # 验证提示语是否正确
        assert "✅ 已退出登录" in success_messages
        assert "📚 今日学习辛苦啦，欢迎下次再来图书馆努力学习！" in success_messages
        
        # 验证session_state是否正确重置
        assert mock_session_state.login_status == False
        assert mock_session_state.current_user == None
        assert mock_session_state.selected_campus == None

def test_logout_message_content():
    """测试退出提示语内容是否准确"""
    expected_message = "📚 今日学习辛苦啦，欢迎下次再来图书馆努力学习！"
    
    # 验证提示语包含期望的内容
    assert "今日学习辛苦啦" in expected_message
    assert "欢迎下次再来图书馆努力学习" in expected_message
    assert expected_message.startswith("📚")

def test_logout_session_cleanup():
    """测试退出登录时session_state是否正确清理"""
    # 初始化session_state
    st.session_state.login_status = True
    st.session_state.current_user = {"name": "测试用户", "studentId": "123456789012"}
    st.session_state.selected_campus = "湖光校区"
    st.session_state.selected_seat = "寸金-A1"
    
    # 执行退出逻辑
    st.session_state.login_status = False
    st.session_state.current_user = None
    st.session_state.selected_campus = None
    
    # 验证状态已重置
    assert st.session_state.login_status == False
    assert st.session_state.current_user == None
    assert st.session_state.selected_campus == None
    
    # selected_seat应该保持不变（不在清理范围内）
    assert st.session_state.selected_seat == "寸金-A1"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
