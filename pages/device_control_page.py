from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class DeviceControlPage:
    """扫地机APP设备控制页面对象类"""
    
    def __init__(self, driver):
        """初始化设备控制页面对象
        
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.url = "http://localhost:8080/device"  # 测试环境URL，实际项目中应从配置文件获取
        
        # 页面元素定位器
        self.page_title_locator = (By.CLASS_NAME, "device-page-title")
        self.device_name_locator = (By.ID, "device-name")
        self.device_status_locator = (By.ID, "device-status")
        self.battery_level_locator = (By.ID, "battery-level")
        self.power_button_locator = (By.ID, "power-button")
        self.start_clean_button_locator = (By.ID, "start-clean-button")
        self.stop_clean_button_locator = (By.ID, "stop-clean-button")
        self.mode_selector_locator = (By.ID, "cleaning-mode-selector")
        self.standard_mode_option_locator = (By.XPATH, "//select[@id='cleaning-mode-selector']/option[@value='standard']")
        self.strong_mode_option_locator = (By.XPATH, "//select[@id='cleaning-mode-selector']/option[@value='strong']")
        self.eco_mode_option_locator = (By.XPATH, "//select[@id='cleaning-mode-selector']/option[@value='eco']")
        self.settings_button_locator = (By.ID, "settings-button")
        self.map_view_locator = (By.ID, "map-view")
        self.dust_bin_status_locator = (By.ID, "dust-bin-status")
        self.cleaning_area_locator = (By.ID, "cleaning-area")
        self.cleaning_time_locator = (By.ID, "cleaning-time")
    
    def open(self):
        """打开设备控制页面"""
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.page_title_locator)
            )
        except TimeoutException:
            raise Exception("设备控制页面加载超时")
    
    def is_page_loaded(self):
        """检查页面是否已加载
        
        Returns:
            bool: 页面是否加载成功
        """
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.page_title_locator)
            )
        except TimeoutException:
            return False
    
    def get_device_name(self):
        """获取设备名称
        
        Returns:
            str: 设备名称
        """
        try:
            return self.driver.find_element(*self.device_name_locator).text
        except NoSuchElementException:
            return ""
    
    def is_device_online(self):
        """检查设备是否在线
        
        Returns:
            bool: 设备是否在线
        """
        try:
            status_text = self.driver.find_element(*self.device_status_locator).text
            return "在线" in status_text or "online" in status_text.lower()
        except NoSuchElementException:
            return False
    
    def get_battery_level(self):
        """获取电池电量百分比
        
        Returns:
            int: 电池电量百分比
        """
        try:
            battery_text = self.driver.find_element(*self.battery_level_locator).text
            # 假设电池电量显示格式为"电量：85%"或"Battery: 85%"
            import re
            match = re.search(r'(\d+)%', battery_text)
            if match:
                return int(match.group(1))
            return 0
        except (NoSuchElementException, ValueError):
            return 0
    
    def is_device_powered_on(self):
        """检查设备是否开机
        
        Returns:
            bool: 设备是否开机
        """
        try:
            power_button = self.driver.find_element(*self.power_button_locator)
            # 假设电源按钮有一个"data-status"属性，值为"on"或"off"
            return power_button.get_attribute("data-status") == "on"
        except NoSuchElementException:
            return False
    
    def toggle_power(self):
        """切换设备电源状态"""
        self.driver.find_element(*self.power_button_locator).click()
        # 等待状态变化
        WebDriverWait(self.driver, 5).until(
            lambda driver: driver.find_element(*self.power_button_locator).get_attribute("data-status") != 
            ("on" if self.is_device_powered_on() else "off")
        )
    
    def is_device_cleaning(self):
        """检查设备是否正在清扫
        
        Returns:
            bool: 设备是否正在清扫
        """
        try:
            # 假设开始清扫按钮被禁用且停止清扫按钮启用时表示正在清扫
            start_button = self.driver.find_element(*self.start_clean_button_locator)
            stop_button = self.driver.find_element(*self.stop_clean_button_locator)
            return start_button.get_attribute("disabled") and not stop_button.get_attribute("disabled")
        except NoSuchElementException:
            return False
    
    def start_cleaning(self):
        """开始清扫"""
        if not self.is_device_cleaning():
            self.driver.find_element(*self.start_clean_button_locator).click()
            # 等待设备开始清扫
            WebDriverWait(self.driver, 5).until(
                lambda driver: self.is_device_cleaning()
            )
    
    def stop_cleaning(self):
        """停止清扫"""
        if self.is_device_cleaning():
            self.driver.find_element(*self.stop_clean_button_locator).click()
            # 等待设备停止清扫
            WebDriverWait(self.driver, 5).until(
                lambda driver: not self.is_device_cleaning()
            )
    
    def get_current_mode(self):
        """获取当前清扫模式
        
        Returns:
            str: 当前清扫模式，可能的值: "standard", "strong", "eco"
        """
        try:
            mode_selector = self.driver.find_element(*self.mode_selector_locator)
            return mode_selector.get_attribute("value")
        except NoSuchElementException:
            return "standard"  # 默认值
    
    def set_cleaning_mode(self, mode):
        """设置清扫模式
        
        Args:
            mode (str): 要设置的清扫模式，可能的值: "standard", "strong", "eco"
        """
        if mode not in ["standard", "strong", "eco"]:
            raise ValueError(f"不支持的清扫模式: {mode}")
            
        if self.get_current_mode() != mode:
            mode_selector = self.driver.find_element(*self.mode_selector_locator)
            mode_selector.click()
            
            # 选择相应的模式
            if mode == "standard":
                self.driver.find_element(*self.standard_mode_option_locator).click()
            elif mode == "strong":
                self.driver.find_element(*self.strong_mode_option_locator).click()
            elif mode == "eco":
                self.driver.find_element(*self.eco_mode_option_locator).click()
            
            # 等待模式变更
            WebDriverWait(self.driver, 5).until(
                lambda driver: self.get_current_mode() == mode
            )
    
    def get_dust_bin_status(self):
        """获取尘盒状态
        
        Returns:
            int: 尘盒占用百分比，0-100
        """
        try:
            dust_bin_text = self.driver.find_element(*self.dust_bin_status_locator).text
            # 假设尘盒状态显示格式为"尘盒：45%"或"Dust bin: 45%"
            import re
            match = re.search(r'(\d+)%', dust_bin_text)
            if match:
                return int(match.group(1))
            return 0
        except (NoSuchElementException, ValueError):
            return 0
    
    def get_cleaning_area(self):
        """获取已清扫面积
        
        Returns:
            float: 已清扫面积，单位平方米
        """
        try:
            area_text = self.driver.find_element(*self.cleaning_area_locator).text
            # 假设清扫面积显示格式为"已清扫: 23.5㎡"或"Cleaned: 23.5㎡"
            import re
            match = re.search(r'([\d.]+)', area_text)
            if match:
                return float(match.group(1))
            return 0.0
        except (NoSuchElementException, ValueError):
            return 0.0
    
    def get_cleaning_time(self):
        """获取清扫时间
        
        Returns:
            int: 清扫时间，单位分钟
        """
        try:
            time_text = self.driver.find_element(*self.cleaning_time_locator).text
            # 假设清扫时间显示格式为"时间: 45分钟"或"Time: 45 minutes"
            import re
            match = re.search(r'(\d+)', time_text)
            if match:
                return int(match.group(1))
            return 0
        except (NoSuchElementException, ValueError):
            return 0
    
    def navigate_to_settings(self):
        """导航到设置页面
        
        Returns:
            SettingsPage: 设置页面对象
        """
        self.driver.find_element(*self.settings_button_locator).click()
        # 导入并返回设置页面对象
        from pages.settings_page import SettingsPage
        settings_page = SettingsPage(self.driver)
        settings_page.is_page_loaded()  # 等待页面加载
        return settings_page 