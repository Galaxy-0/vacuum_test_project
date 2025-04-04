from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SettingsPage:
    """扫地机APP设置页面对象类"""
    
    def __init__(self, driver):
        """初始化设置页面对象
        
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.url = "http://localhost:8080/settings"  # 测试环境URL，实际项目中应从配置文件获取
        
        # 页面元素定位器
        self.page_title_locator = (By.CLASS_NAME, "settings-page-title")
        self.back_button_locator = (By.ID, "back-button")
        self.voice_setting_section_locator = (By.ID, "voice-settings")
        self.schedule_setting_section_locator = (By.ID, "schedule-settings")
        self.map_setting_section_locator = (By.ID, "map-settings")
        self.firmware_version_locator = (By.ID, "firmware-version")
        self.check_update_button_locator = (By.ID, "check-update-button")
        self.notification_toggle_locator = (By.ID, "notification-toggle")
        self.do_not_disturb_toggle_locator = (By.ID, "do-not-disturb-toggle")
        self.voice_volume_slider_locator = (By.ID, "voice-volume-slider")
        self.language_selector_locator = (By.ID, "language-selector")
        self.factory_reset_button_locator = (By.ID, "factory-reset-button")
        self.confirm_reset_button_locator = (By.ID, "confirm-reset-button")
        self.cancel_reset_button_locator = (By.ID, "cancel-reset-button")
    
    def open(self):
        """打开设置页面"""
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.page_title_locator)
            )
        except TimeoutException:
            raise Exception("设置页面加载超时")
    
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
    
    def navigate_back(self):
        """返回上一页"""
        self.driver.find_element(*self.back_button_locator).click()
        # 等待页面跳转
        WebDriverWait(self.driver, 5).until(
            lambda driver: "settings" not in driver.current_url
        )
    
    def is_voice_setting_displayed(self):
        """检查语音设置选项是否显示
        
        Returns:
            bool: 语音设置选项是否显示
        """
        try:
            return self.driver.find_element(*self.voice_setting_section_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def is_schedule_setting_displayed(self):
        """检查定时设置选项是否显示
        
        Returns:
            bool: 定时设置选项是否显示
        """
        try:
            return self.driver.find_element(*self.schedule_setting_section_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def is_map_setting_displayed(self):
        """检查地图设置选项是否显示
        
        Returns:
            bool: 地图设置选项是否显示
        """
        try:
            return self.driver.find_element(*self.map_setting_section_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def get_firmware_version(self):
        """获取固件版本
        
        Returns:
            str: 固件版本号
        """
        try:
            return self.driver.find_element(*self.firmware_version_locator).text
        except NoSuchElementException:
            return ""
    
    def check_for_updates(self):
        """检查更新"""
        update_button = self.driver.find_element(*self.check_update_button_locator)
        
        # 判断按钮是否可点击
        if not update_button.is_enabled():
            raise Exception("更新按钮不可点击")
        
        update_button.click()
        
        # 等待更新检查完成（假设会有某些状态变化）
        WebDriverWait(self.driver, 10).until(
            lambda driver: "checking" not in update_button.get_attribute("class")
        )
        
        # 返回检查结果（假设结果会显示在按钮的data-result属性中）
        return update_button.get_attribute("data-result")
    
    def toggle_notification(self, enable=True):
        """开启或关闭通知
        
        Args:
            enable (bool): 是否启用通知
        """
        toggle = self.driver.find_element(*self.notification_toggle_locator)
        is_enabled = toggle.get_attribute("aria-checked") == "true"
        
        if (enable and not is_enabled) or (not enable and is_enabled):
            toggle.click()
            # 等待状态变化
            WebDriverWait(self.driver, 5).until(
                lambda driver: (toggle.get_attribute("aria-checked") == "true") == enable
            )
    
    def toggle_do_not_disturb(self, enable=True):
        """开启或关闭勿扰模式
        
        Args:
            enable (bool): 是否启用勿扰模式
        """
        toggle = self.driver.find_element(*self.do_not_disturb_toggle_locator)
        is_enabled = toggle.get_attribute("aria-checked") == "true"
        
        if (enable and not is_enabled) or (not enable and is_enabled):
            toggle.click()
            # 等待状态变化
            WebDriverWait(self.driver, 5).until(
                lambda driver: (toggle.get_attribute("aria-checked") == "true") == enable
            )
    
    def set_voice_volume(self, volume):
        """设置语音音量
        
        Args:
            volume (int): 音量大小，0-100
        """
        if not 0 <= volume <= 100:
            raise ValueError("音量必须在0-100范围内")
        
        # 使用JavaScript设置滑块值
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; "
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            self.driver.find_element(*self.voice_volume_slider_locator),
            volume
        )
    
    def get_voice_volume(self):
        """获取当前语音音量
        
        Returns:
            int: 当前音量大小，0-100
        """
        try:
            slider = self.driver.find_element(*self.voice_volume_slider_locator)
            return int(slider.get_attribute("value"))
        except (NoSuchElementException, ValueError):
            return 0
    
    def select_language(self, language_code):
        """选择界面语言
        
        Args:
            language_code (str): 语言代码，如'zh_CN','en_US'
        """
        # 点击语言选择器
        self.driver.find_element(*self.language_selector_locator).click()
        
        # 选择指定语言
        language_option_locator = (By.XPATH, f"//select[@id='language-selector']/option[@value='{language_code}']")
        self.driver.find_element(*language_option_locator).click()
        
        # 等待语言切换完成（假设页面会刷新）
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element(*self.language_selector_locator).get_attribute("value") == language_code
        )
    
    def get_current_language(self):
        """获取当前界面语言
        
        Returns:
            str: 当前语言代码
        """
        try:
            selector = self.driver.find_element(*self.language_selector_locator)
            return selector.get_attribute("value")
        except NoSuchElementException:
            return "en_US"  # 默认值
    
    def perform_factory_reset(self, confirm=False):
        """执行恢复出厂设置
        
        Args:
            confirm (bool): 是否确认恢复出厂设置
        """
        # 点击恢复出厂设置按钮
        self.driver.find_element(*self.factory_reset_button_locator).click()
        
        # 等待确认对话框显示
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(self.confirm_reset_button_locator)
        )
        
        # 根据参数决定是确认还是取消
        if confirm:
            self.driver.find_element(*self.confirm_reset_button_locator).click()
            # 恢复出厂设置后应跳转到其他页面
            WebDriverWait(self.driver, 15).until(
                lambda driver: "settings" not in driver.current_url
            )
        else:
            self.driver.find_element(*self.cancel_reset_button_locator).click()
            # 取消后对话框应消失
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located(self.confirm_reset_button_locator)
            ) 