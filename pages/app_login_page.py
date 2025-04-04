from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AppLoginPage:
    """扫地机APP登录页面对象类"""
    
    def __init__(self, driver):
        """初始化登录页面对象
        
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.url = "http://localhost:8080/login"  # 测试环境URL，实际项目中应从配置文件获取
        
        # 页面元素定位器
        self.username_field_locator = (By.ID, "username")
        self.password_field_locator = (By.ID, "password")
        self.login_button_locator = (By.ID, "login-button")
        self.error_message_locator = (By.CLASS_NAME, "login-error")
        self.logo_locator = (By.CLASS_NAME, "app-logo")
        self.remember_me_checkbox_locator = (By.ID, "remember-me")
        self.forgot_password_link_locator = (By.LINK_TEXT, "忘记密码?")
        self.register_link_locator = (By.LINK_TEXT, "新用户注册")
    
    def open(self):
        """打开登录页面"""
        self.driver.get(self.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.logo_locator)
            )
        except TimeoutException:
            raise Exception("登录页面加载超时")
    
    def is_page_loaded(self):
        """检查页面是否已加载
        
        Returns:
            bool: 页面是否加载成功
        """
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.logo_locator)
            )
        except TimeoutException:
            return False
    
    def is_username_field_displayed(self):
        """检查用户名输入框是否显示
        
        Returns:
            bool: 用户名输入框是否显示
        """
        try:
            return self.driver.find_element(*self.username_field_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def is_password_field_displayed(self):
        """检查密码输入框是否显示
        
        Returns:
            bool: 密码输入框是否显示
        """
        try:
            return self.driver.find_element(*self.password_field_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def is_login_button_displayed(self):
        """检查登录按钮是否显示
        
        Returns:
            bool: 登录按钮是否显示
        """
        try:
            return self.driver.find_element(*self.login_button_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def is_error_message_displayed(self):
        """检查错误消息是否显示
        
        Returns:
            bool: 错误消息是否显示
        """
        try:
            return self.driver.find_element(*self.error_message_locator).is_displayed()
        except NoSuchElementException:
            return False
    
    def get_error_message(self):
        """获取错误消息文本
        
        Returns:
            str: 错误消息文本
        """
        try:
            return self.driver.find_element(*self.error_message_locator).text
        except NoSuchElementException:
            return ""
    
    def enter_username(self, username):
        """输入用户名
        
        Args:
            username (str): 要输入的用户名
        """
        username_field = self.driver.find_element(*self.username_field_locator)
        username_field.clear()
        username_field.send_keys(username)
    
    def enter_password(self, password):
        """输入密码
        
        Args:
            password (str): 要输入的密码
        """
        password_field = self.driver.find_element(*self.password_field_locator)
        password_field.clear()
        password_field.send_keys(password)
    
    def click_login_button(self):
        """点击登录按钮"""
        self.driver.find_element(*self.login_button_locator).click()
    
    def select_remember_me(self, select=True):
        """选择或取消选择"记住我"
        
        Args:
            select (bool): 是否选中复选框
        """
        checkbox = self.driver.find_element(*self.remember_me_checkbox_locator)
        if (checkbox.is_selected() and not select) or (not checkbox.is_selected() and select):
            checkbox.click()
    
    def click_forgot_password(self):
        """点击"忘记密码"链接"""
        self.driver.find_element(*self.forgot_password_link_locator).click()
    
    def click_register(self):
        """点击"新用户注册"链接"""
        self.driver.find_element(*self.register_link_locator).click()
    
    def login(self, username, password, remember_me=False):
        """执行登录操作
        
        Args:
            username (str): 用户名
            password (str): 密码
            remember_me (bool, optional): 是否勾选"记住我"。默认为False
        """
        self.enter_username(username)
        self.enter_password(password)
        
        if remember_me:
            self.select_remember_me()
            
        self.click_login_button()
        
        # 等待页面跳转或错误消息显示
        try:
            WebDriverWait(self.driver, 5).until(
                lambda driver: (
                    # 检查是否已跳转到其他页面
                    "login" not in driver.current_url or
                    # 或者错误消息是否显示
                    self.is_error_message_displayed()
                )
            )
        except TimeoutException:
            raise Exception("登录操作超时，未显示错误消息也未跳转页面") 