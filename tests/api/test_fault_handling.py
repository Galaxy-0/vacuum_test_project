import pytest
import time
from libs.api_client import ApiClient

class TestFaultHandling:
    """测试扫地机异常处理与故障恢复能力"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        client = ApiClient(base_url="http://localhost:8080/api/v1")
        yield client
    
    @pytest.fixture(scope="function")
    def setup_device(self, api_client):
        """设置设备正常工作状态"""
        # 确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 重置任何故障状态
        api_client.post("/simulation/reset_faults", {})
        
        # 确保设备停止清扫
        status = api_client.get("/device/status").json()
        if status.get("working"):
            api_client.post("/device/clean", {"action": "stop"})
        
        # 将设备放置在初始位置
        api_client.post("/simulation/position", {"x": 0, "y": 0, "orientation": 0})
        
        yield api_client
        
        # 清理：停止所有操作并重置故障
        api_client.post("/device/clean", {"action": "stop"})
        api_client.post("/simulation/reset_faults", {})
    
    def test_wheel_stuck(self, setup_device):
        """测试轮子卡住故障处理"""
        api_client = setup_device
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        
        # 模拟轮子卡住故障
        api_client.post("/simulation/fault", {"type": "wheel_stuck", "wheel": "left"})
        
        # 等待设备响应故障
        time.sleep(5)
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备检测到故障并停止工作
        assert status.get("error_code") != 0, "设备未能检测到轮子卡住故障"
        assert not status.get("working"), "检测到故障后设备未停止工作"
        
        # 检查故障信息详情
        fault_info = api_client.get("/device/fault_info").json()
        assert "wheel_stuck" in fault_info.get("type", ""), "故障信息未正确记录轮子卡住"
        assert "left" in fault_info.get("details", ""), "故障信息未正确记录是左轮卡住"
        
        # 清除故障
        api_client.post("/simulation/reset_faults", {})
        time.sleep(2)
        
        # 验证设备故障已清除
        status = api_client.get("/device/status").json()
        assert status.get("error_code") == 0, "故障清除后错误代码未重置"
    
    def test_cliff_detection(self, setup_device):
        """测试悬崖检测功能"""
        api_client = setup_device
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        
        # 模拟悬崖检测触发
        api_client.post("/simulation/cliff", {"detect": True, "position": {"x": 0.5, "y": 0.5}})
        
        # 等待设备响应
        time.sleep(3)
        
        # 获取设备位置和状态
        position_before = api_client.get("/device/position").json()
        
        # 等待设备尝试避开悬崖
        time.sleep(5)
        
        # 获取设备新位置
        position_after = api_client.get("/device/position").json()
        
        # 验证设备已经移动以避开悬崖
        assert position_before != position_after, "设备未能成功避开悬崖"
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备继续工作，没有因为悬崖检测而停止（应该是避开后继续）
        assert status.get("working"), "设备在避开悬崖后未继续工作"
        
        # 持续模拟悬崖围绕设备（模拟设备被放在桌子上的情况）
        api_client.post("/simulation/cliff", {
            "detect": True, 
            "surrounding": True,
            "radius": 1.0
        })
        
        # 等待设备响应
        time.sleep(5)
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备检测到被困在悬崖中，发出警报并停止工作
        assert not status.get("working"), "设备在被困在悬崖中时未停止工作"
        assert status.get("error_code") != 0, "设备未能检测到被困在悬崖中的故障"
    
    def test_main_brush_stuck(self, setup_device):
        """测试主刷卡住故障处理"""
        api_client = setup_device
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        
        # 模拟主刷卡住故障
        api_client.post("/simulation/fault", {"type": "brush_stuck", "brush": "main"})
        
        # 等待设备响应故障
        time.sleep(3)
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备检测到故障并停止工作
        assert status.get("error_code") != 0, "设备未能检测到主刷卡住故障"
        assert not status.get("working"), "检测到故障后设备未停止工作"
        
        # 检查故障信息详情
        fault_info = api_client.get("/device/fault_info").json()
        assert "brush_stuck" in fault_info.get("type", ""), "故障信息未正确记录刷子卡住"
        assert "main" in fault_info.get("details", ""), "故障信息未正确记录是主刷卡住"
    
    def test_overheating(self, setup_device):
        """测试过热保护功能"""
        api_client = setup_device
        
        # 开始高强度清扫
        api_client.post("/device/mode", {"mode": "strong"})
        api_client.post("/device/clean", {"action": "start"})
        
        # 模拟电机温度升高
        for temp in range(40, 85, 5):  # 从40°C逐渐升高到80°C
            api_client.post("/simulation/temperature", {"component": "main_motor", "value": temp})
            time.sleep(1)
            
            # 每次温度变化后检查状态
            status = api_client.get("/device/status").json()
            
            # 检查设备响应
            if temp >= 75:  # 假设75°C是过热阈值
                assert not status.get("working"), f"温度达到{temp}°C时设备未停止工作"
                assert status.get("error_code") != 0, f"温度达到{temp}°C时设备未报告过热故障"
                
                # 故障类型检查
                fault_info = api_client.get("/device/fault_info").json()
                assert "overheating" in fault_info.get("type", ""), "故障信息未正确记录过热"
                assert "main_motor" in fault_info.get("details", ""), "故障信息未正确记录是主电机过热"
                break
        
        # 模拟温度下降
        api_client.post("/simulation/temperature", {"component": "main_motor", "value": 50})
        time.sleep(5)
        
        # 清除故障
        api_client.post("/simulation/reset_faults", {})
        time.sleep(2)
        
        # 验证设备能正常启动
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        status = api_client.get("/device/status").json()
        assert status.get("working"), "温度恢复正常后设备未能重新启动"
    
    def test_low_battery_return(self, setup_device):
        """测试低电量自动回充功能"""
        api_client = setup_device
        
        # 设置充电座位置
        dock_position = {"x": 0.0, "y": 0.0}
        api_client.post("/simulation/dock", dock_position)
        
        # 将设备放置在远离充电座的位置
        api_client.post("/simulation/position", {"x": 3.0, "y": 2.0})
        
        # 设置电量为中等水平
        api_client.post("/simulation/battery", {"level": 50})
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(3)
        
        # 逐渐降低电量
        for level in range(45, 10, -5):
            api_client.post("/simulation/battery", {"level": level})
            time.sleep(1)
            
            # 每次电量变化后检查状态
            status = api_client.get("/device/status").json()
            
            # 检查设备响应
            if level <= 15:  # 假设15%是低电量阈值
                assert status.get("returning_to_dock"), f"电量降至{level}%时设备未自动返回充电座"
                assert not status.get("working"), f"电量降至{level}%且返回充电座时设备仍显示为清扫状态"
                break
        
        # 等待设备返回充电座
        time.sleep(10)
        
        # 获取设备最新状态和位置
        status = api_client.get("/device/status").json()
        position = api_client.get("/device/position").json()
        
        # 验证设备是否接近充电座
        distance_to_dock = ((position["x"] - dock_position["x"])**2 + 
                          (position["y"] - dock_position["y"])**2)**0.5
        
        assert distance_to_dock < 0.5, "设备未能成功接近充电座"
        assert status.get("docked") or status.get("returning_to_dock"), "设备未成功对接或尝试对接充电座"
    
    def test_dust_bin_full(self, setup_device):
        """测试尘盒满警告功能"""
        api_client = setup_device
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        
        # 逐渐增加尘盒占用
        for fill_level in range(60, 105, 5):  # 从60%到100%
            api_client.post("/simulation/dust_bin", {"fill_level": fill_level})
            time.sleep(1)
            
            # 获取设备状态
            status = api_client.get("/device/status").json()
            
            # 检查设备响应
            if fill_level >= 95:  # 假设95%是尘盒满警告阈值
                assert status.get("dust_bin_full"), f"尘盒占用达到{fill_level}%时未显示尘盒满警告"
                
                # 检查设备是否继续工作（尘盒满通常是警告而非错误）
                assert status.get("working"), "尘盒满警告不应导致设备停止工作"
                break
        
        # 尘盒占用达到100%以上时设备应停止工作
        api_client.post("/simulation/dust_bin", {"fill_level": 100})
        time.sleep(3)
        
        status = api_client.get("/device/status").json()
        assert not status.get("working"), "尘盒完全满时设备未停止工作"
        assert status.get("error_code") != 0, "尘盒完全满时设备未报告错误"
    
    def test_network_disconnection(self, setup_device):
        """测试网络断连处理"""
        api_client = setup_device
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        time.sleep(2)
        
        # 获取设备状态
        initial_status = api_client.get("/device/status").json()
        assert initial_status.get("working"), "设备未能正常启动清扫"
        
        # 模拟网络断开
        api_client.post("/simulation/network", {"connected": False})
        time.sleep(5)
        
        # 模拟网络恢复
        api_client.post("/simulation/network", {"connected": True})
        time.sleep(3)
        
        # 获取设备状态
        reconnected_status = api_client.get("/device/status").json()
        
        # 验证设备在网络断开再恢复后依然保持相同的工作状态
        assert reconnected_status.get("working") == initial_status.get("working"), "网络恢复后设备工作状态发生变化"
        assert reconnected_status.get("mode") == initial_status.get("mode"), "网络恢复后设备清扫模式发生变化"
        
        # 模拟长时间网络断开
        api_client.post("/simulation/network", {"connected": False})
        api_client.post("/simulation/time_advance", {"minutes": 60})  # 模拟时间前进1小时
        
        # 恢复网络
        api_client.post("/simulation/network", {"connected": True})
        time.sleep(3)
        
        # 获取设备状态
        long_disconnect_status = api_client.get("/device/status").json()
        
        # 验证设备在长时间网络断开后依然保持正确状态
        assert "last_seen" in long_disconnect_status, "设备状态中缺少last_seen时间戳"
        assert long_disconnect_status.get("connection_state") == "reconnected", "设备未显示重新连接状态" 