import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.app_login_page import AppLoginPage
from pages.device_control_page import DeviceControlPage

class TestAppBasic:
    """测试APP基本功能"""
    
    @pytest.fixture(scope="class")
    def setup_driver(self, request):
        """设置WebDriver"""
        # 这里通常会从conftest.py中获取WebDriver配置
        # 简化示例，实际实现需要根据项目配置调整
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")  # 无头模式，CI环境中使用
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service('/usr/local/bin/chromedriver')  # 路径需要根据实际环境设置
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(10)
        
        request.cls.driver = driver
        yield driver
        driver.quit()
    
    @pytest.fixture(scope="function")
    def login(self, setup_driver):
        """登录到APP"""
        login_page = AppLoginPage(setup_driver)
        login_page.open()
        login_page.login("test_user", "password123")
        
        # 验证登录成功
        device_page = DeviceControlPage(setup_driver)
        assert device_page.is_page_loaded(), "登录失败，设备控制页面未加载"
        
        return device_page
    
    def test_app_launch(self, setup_driver):
        """测试APP能否正常启动"""
        login_page = AppLoginPage(setup_driver)
        login_page.open()
        
        # 验证登录页面元素存在
        assert login_page.is_page_loaded(), "登录页面未正确加载"
        assert login_page.is_username_field_displayed(), "用户名输入框未显示"
        assert login_page.is_password_field_displayed(), "密码输入框未显示"
        assert login_page.is_login_button_displayed(), "登录按钮未显示"
    
    def test_user_login(self, setup_driver):
        """测试用户登录功能"""
        login_page = AppLoginPage(setup_driver)
        login_page.open()
        
        # 测试使用正确凭据登录
        login_page.login("test_user", "password123")
        device_page = DeviceControlPage(setup_driver)
        assert device_page.is_page_loaded(), "使用正确凭据登录后未跳转到设备页面"
        
        # 重新打开登录页，测试使用错误凭据登录
        setup_driver.get(login_page.url)
        login_page.login("wrong_user", "wrong_password")
        
        # 验证错误提示
        assert login_page.is_error_message_displayed(), "使用错误凭据登录未显示错误信息"
        assert "用户名或密码错误" in login_page.get_error_message(), "错误信息文本不正确"
    
    def test_device_status_display(self, login):
        """测试设备状态是否正确显示"""
        device_page = login
        
        # 验证设备信息显示正确
        assert device_page.is_device_online(), "设备应显示为在线状态"
        assert device_page.get_battery_level() >= 0, "电池电量应正确显示"
        assert device_page.get_current_mode() in ["standard", "strong", "eco"], "清扫模式应正确显示"
    
    def test_power_control(self, login):
        """测试设备电源控制按钮"""
        device_page = login
        
        # 记录初始状态
        initial_power_state = device_page.is_device_powered_on()
        
        # 切换电源状态
        device_page.toggle_power()
        time.sleep(2)  # 等待设备状态更新
        
        # 验证状态已改变
        new_power_state = device_page.is_device_powered_on()
        assert new_power_state != initial_power_state, "点击电源按钮后设备状态未变更"
        
        # 恢复初始状态
        device_page.toggle_power()
        time.sleep(2)
        final_power_state = device_page.is_device_powered_on()
        assert final_power_state == initial_power_state, "未能恢复到初始电源状态"
    
    def test_cleaning_mode_switch(self, login):
        """测试清扫模式切换"""
        device_page = login
        
        # 确保设备开机
        if not device_page.is_device_powered_on():
            device_page.toggle_power()
            time.sleep(2)
        
        # 测试切换到强力模式
        device_page.set_cleaning_mode("strong")
        time.sleep(2)
        assert device_page.get_current_mode() == "strong", "未能切换到强力清扫模式"
        
        # 测试切换到节能模式
        device_page.set_cleaning_mode("eco")
        time.sleep(2)
        assert device_page.get_current_mode() == "eco", "未能切换到节能清扫模式"
        
        # 测试切换到标准模式
        device_page.set_cleaning_mode("standard")
        time.sleep(2)
        assert device_page.get_current_mode() == "standard", "未能切换到标准清扫模式"
    
    def test_start_stop_cleaning(self, login):
        """测试开始和停止清扫功能"""
        device_page = login
        
        # 确保设备开机
        if not device_page.is_device_powered_on():
            device_page.toggle_power()
            time.sleep(2)
        
        # 确保设备停止清扫
        if device_page.is_device_cleaning():
            device_page.stop_cleaning()
            time.sleep(2)
        
        # 开始清扫
        device_page.start_cleaning()
        time.sleep(2)
        assert device_page.is_device_cleaning(), "点击开始清扫按钮后设备未进入清扫状态"
        
        # 停止清扫
        device_page.stop_cleaning()
        time.sleep(2)
        assert not device_page.is_device_cleaning(), "点击停止清扫按钮后设备仍在清扫状态"
    
    def test_device_settings_page(self, login):
        """测试设备设置页面"""
        device_page = login
        
        # 进入设置页面
        settings_page = device_page.navigate_to_settings()
        assert settings_page.is_page_loaded(), "设置页面未正确加载"
        
        # 验证设置选项存在
        assert settings_page.is_voice_setting_displayed(), "语音设置选项未显示"
        assert settings_page.is_schedule_setting_displayed(), "定时设置选项未显示"
        assert settings_page.is_map_setting_displayed(), "地图设置选项未显示"
        
        # 返回设备控制页面
        settings_page.navigate_back()
        assert device_page.is_page_loaded(), "未能成功返回设备控制页面" 