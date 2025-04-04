import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.app_login_page import AppLoginPage
from pages.device_control_page import DeviceControlPage
from utils.log_utils import get_logger

logger = get_logger(__name__)

class TestAppPerformance:
    """测试APP性能表现"""
    
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
    
    def test_app_startup_time(self, setup_driver):
        """测试APP启动时间"""
        # 记录启动开始时间
        start_time = time.time()
        
        # 打开登录页面
        login_page = AppLoginPage(setup_driver)
        login_page.open()
        
        # 等待页面加载完成
        assert login_page.is_page_loaded()
        
        # 计算加载时间
        load_time = time.time() - start_time
        logger.info(f"APP启动加载时间: {load_time:.2f} 秒")
        
        # 断言加载时间在合理范围内（假设3秒是可接受的最大值）
        assert load_time < 3.0, f"APP启动时间过长: {load_time:.2f} 秒"
    
    def test_login_response_time(self, setup_driver):
        """测试登录响应时间"""
        # 打开登录页面
        login_page = AppLoginPage(setup_driver)
        login_page.open()
        
        # 确保页面已加载
        assert login_page.is_page_loaded()
        
        # 输入用户名和密码
        login_page.enter_username("test_user")
        login_page.enter_password("password123")
        
        # 记录点击登录按钮的时间
        start_time = time.time()
        login_page.click_login_button()
        
        # 等待设备控制页面加载
        device_page = DeviceControlPage(setup_driver)
        assert device_page.is_page_loaded()
        
        # 计算登录响应时间
        response_time = time.time() - start_time
        logger.info(f"登录响应时间: {response_time:.2f} 秒")
        
        # 断言响应时间在合理范围内（假设2秒是可接受的最大值）
        assert response_time < 2.0, f"登录响应时间过长: {response_time:.2f} 秒"
    
    def test_page_navigation_performance(self, login):
        """测试页面导航性能"""
        device_page = login
        
        # 记录导航开始时间
        start_time = time.time()
        
        # 导航到设置页面
        settings_page = device_page.navigate_to_settings()
        assert settings_page.is_page_loaded()
        
        # 计算导航时间
        navigation_time = time.time() - start_time
        logger.info(f"导航到设置页面时间: {navigation_time:.2f} 秒")
        
        # 断言导航时间在合理范围内（假设1.5秒是可接受的最大值）
        assert navigation_time < 1.5, f"页面导航时间过长: {navigation_time:.2f} 秒"
        
        # 测试返回导航性能
        start_time = time.time()
        settings_page.navigate_back()
        assert device_page.is_page_loaded()
        
        # 计算返回导航时间
        back_navigation_time = time.time() - start_time
        logger.info(f"返回设备页面时间: {back_navigation_time:.2f} 秒")
        
        # 断言返回导航时间在合理范围内
        assert back_navigation_time < 1.5, f"返回导航时间过长: {back_navigation_time:.2f} 秒"
    
    def test_control_response_time(self, login):
        """测试设备控制响应时间"""
        device_page = login
        
        # 确保设备开机
        if not device_page.is_device_powered_on():
            device_page.toggle_power()
            time.sleep(1)
        
        # 测试开始清扫响应时间
        start_time = time.time()
        device_page.start_cleaning()
        response_time = time.time() - start_time
        logger.info(f"开始清扫响应时间: {response_time:.2f} 秒")
        assert response_time < 1.5, f"开始清扫响应时间过长: {response_time:.2f} 秒"
        
        # 等待一段时间
        time.sleep(2)
        
        # 测试停止清扫响应时间
        start_time = time.time()
        device_page.stop_cleaning()
        response_time = time.time() - start_time
        logger.info(f"停止清扫响应时间: {response_time:.2f} 秒")
        assert response_time < 1.5, f"停止清扫响应时间过长: {response_time:.2f} 秒"
    
    def test_mode_switch_performance(self, login):
        """测试清扫模式切换性能"""
        device_page = login
        
        # 确保设备开机
        if not device_page.is_device_powered_on():
            device_page.toggle_power()
            time.sleep(1)
        
        # 获取当前模式
        current_mode = device_page.get_current_mode()
        
        # 选择一个不同的模式进行切换
        target_mode = "strong" if current_mode != "strong" else "eco"
        
        # 测试模式切换响应时间
        start_time = time.time()
        device_page.set_cleaning_mode(target_mode)
        response_time = time.time() - start_time
        logger.info(f"清扫模式切换响应时间({target_mode}): {response_time:.2f} 秒")
        assert response_time < 1.5, f"模式切换响应时间过长: {response_time:.2f} 秒"
        
        # 恢复原始模式
        device_page.set_cleaning_mode(current_mode)
    
    def test_memory_usage(self, login):
        """测试内存占用情况（模拟）
        
        注意：这是一个模拟测试，实际浏览器内存监控需要使用专业工具
        """
        device_page = login
        
        # 模拟获取内存使用情况（实际项目中应使用专业工具测量）
        try:
            # 使用JavaScript获取内存使用信息（只有Chrome支持）
            memory_info = self.driver.execute_script("return window.performance.memory")
            
            if memory_info:
                used_js_heap = memory_info.get("usedJSHeapSize", 0) / (1024 * 1024)
                total_js_heap = memory_info.get("totalJSHeapSize", 0) / (1024 * 1024)
                js_heap_limit = memory_info.get("jsHeapSizeLimit", 0) / (1024 * 1024)
                
                logger.info(f"内存使用情况:")
                logger.info(f"  已用JS堆: {used_js_heap:.2f} MB")
                logger.info(f"  总JS堆: {total_js_heap:.2f} MB")
                logger.info(f"  JS堆限制: {js_heap_limit:.2f} MB")
                
                # 断言内存使用在合理范围内（根据实际情况调整）
                assert used_js_heap < total_js_heap * 0.8, "内存使用过高"
            else:
                logger.warning("无法获取内存使用信息，浏览器可能不支持")
        except Exception as e:
            logger.warning(f"内存使用测试失败: {str(e)}")
    
    def test_cpu_usage(self, login):
        """测试CPU占用情况（模拟）
        
        注意：这是一个模拟测试，实际CPU监控需要使用专业工具
        """
        device_page = login
        
        # 模拟高负载操作
        for _ in range(5):
            # 快速切换页面
            settings_page = device_page.navigate_to_settings()
            settings_page.navigate_back()
        
        logger.info("完成CPU负载测试模拟")
        # 实际项目中应使用专业工具监控CPU使用率并进行断言 