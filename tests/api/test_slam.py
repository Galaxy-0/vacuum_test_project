import pytest
import json
import time
from libs.api_client import ApiClient

class TestSlamNavigation:
    """测试扫地机SLAM导航系统"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        client = ApiClient(base_url="http://localhost:8080/api/v1")
        yield client
    
    @pytest.fixture(scope="function")
    def setup_device(self, api_client):
        """设置设备清扫前状态"""
        # 确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 重置地图数据
        api_client.post("/maps/reset", {})
        
        # 确保设备停止清扫
        status = api_client.get("/device/status").json()
        if status.get("working"):
            api_client.post("/device/clean", {"action": "stop"})
        
        # 定位设备到初始位置
        api_client.post("/simulation/position", {"x": 0, "y": 0, "orientation": 0})
        
        # 清除障碍物
        api_client.post("/simulation/obstacle", {"obstacles": []})
        
        yield api_client
        
        # 清理：停止所有操作
        api_client.post("/device/clean", {"action": "stop"})
    
    def test_map_building(self, setup_device):
        """测试地图构建功能"""
        api_client = setup_device
        
        # 开始清扫，构建地图
        api_client.post("/device/clean", {"action": "start"})
        
        # 等待足够时间让设备完成部分地图构建
        time.sleep(5)
        
        # 获取当前地图数据
        map_data = api_client.get("/maps/current").json()
        
        # 验证地图数据有效
        assert "map_id" in map_data, "地图数据缺少map_id"
        assert "cells" in map_data, "地图数据缺少cells"
        assert len(map_data["cells"]) > 0, "地图单元格数据为空"
        
        # 验证地图包含必要信息
        assert "obstacles" in map_data, "地图数据缺少障碍物信息"
        assert "explored_area" in map_data, "地图数据缺少已探索区域信息"
        assert map_data["explored_area"] > 0, "已探索区域为0"
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"})
    
    def test_obstacle_avoidance(self, setup_device):
        """测试障碍物避障能力"""
        api_client = setup_device
        
        # 设置障碍物
        obstacles = [
            {"x": 1.0, "y": 0.0, "radius": 0.2},  # 正前方1米处
            {"x": 0.0, "y": 1.0, "radius": 0.2},  # 左侧1米处
            {"x": -1.0, "y": 0.0, "radius": 0.2}  # 右侧1米处
        ]
        api_client.post("/simulation/obstacle", {"obstacles": obstacles})
        
        # 获取初始位置
        initial_position = api_client.get("/device/position").json()
        
        # 开始清扫
        api_client.post("/device/clean", {"action": "start"})
        
        # 等待足够时间让设备尝试避障
        time.sleep(10)
        
        # 获取当前位置
        current_position = api_client.get("/device/position").json()
        
        # 获取传感器数据
        sensor_data = api_client.get("/device/sensors").json()
        
        # 验证设备没有碰撞到障碍物
        assert not sensor_data["bumper"], "设备碰撞到障碍物"
        
        # 验证设备已经移动（避障并寻找可行路径）
        assert current_position != initial_position, "设备未能成功避障移动"
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"})
    
    def test_path_planning(self, setup_device):
        """测试路径规划能力"""
        api_client = setup_device
        
        # 设置起点和目标点
        start_position = {"x": 0.0, "y": 0.0}
        target_position = {"x": 3.0, "y": 2.0}
        
        # 设置障碍物，创建一个需要绕行的环境
        obstacles = [
            {"x": 1.5, "y": 0.0, "radius": 0.5},  # 路径中间的障碍物
            {"x": 1.5, "y": 1.0, "radius": 0.5}   # 另一个障碍物
        ]
        api_client.post("/simulation/obstacle", {"obstacles": obstacles})
        
        # 将设备放置在起点
        api_client.post("/simulation/position", start_position)
        
        # 请求设备规划路径到目标点
        response = api_client.post("/navigation/plan_path", {
            "target": target_position
        })
        
        # 验证响应
        path_data = response.json()
        assert "path" in path_data, "返回数据缺少路径信息"
        assert len(path_data["path"]) > 0, "规划的路径为空"
        
        # 验证路径的起点和终点正确
        assert path_data["path"][0]["x"] == start_position["x"], "路径起点X坐标不正确"
        assert path_data["path"][0]["y"] == start_position["y"], "路径起点Y坐标不正确"
        
        final_point = path_data["path"][-1]
        assert abs(final_point["x"] - target_position["x"]) < 0.1, "路径终点X坐标误差过大"
        assert abs(final_point["y"] - target_position["y"]) < 0.1, "路径终点Y坐标误差过大"
        
        # 验证路径避开了障碍物
        for point in path_data["path"]:
            for obstacle in obstacles:
                # 计算点到障碍物中心的距离
                dx = point["x"] - obstacle["x"]
                dy = point["y"] - obstacle["y"]
                distance = (dx**2 + dy**2)**0.5
                
                # 确保距离大于障碍物半径（添加一些安全余量）
                assert distance > obstacle["radius"] + 0.1, "路径点过于接近障碍物"
    
    def test_area_cleaning(self, setup_device):
        """测试区域清扫功能"""
        api_client = setup_device
        
        # 定义要清扫的矩形区域
        cleaning_area = {
            "x1": 1.0, "y1": 1.0,  # 左上角
            "x2": 3.0, "y2": 3.0   # 右下角
        }
        
        # 将设备放置在起点附近
        api_client.post("/simulation/position", {"x": 0.0, "y": 0.0})
        
        # 开始区域清扫
        api_client.post("/cleaning/area", cleaning_area)
        
        # 等待足够时间让设备开始清扫
        time.sleep(5)
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备处于清扫状态
        assert status["working"], "设备未进入清扫状态"
        assert status.get("cleaning_mode") == "area", "设备未进入区域清扫模式"
        
        # 等待一段时间让设备清扫部分区域
        time.sleep(10)
        
        # 获取设备位置
        position = api_client.get("/device/position").json()
        
        # 验证设备已进入指定清扫区域
        assert cleaning_area["x1"] <= position["x"] <= cleaning_area["x2"], "设备X坐标不在清扫区域内"
        assert cleaning_area["y1"] <= position["y"] <= cleaning_area["y2"], "设备Y坐标不在清扫区域内"
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"})
    
    def test_return_to_dock(self, setup_device):
        """测试回充功能"""
        api_client = setup_device
        
        # 设置充电座位置
        dock_position = {"x": 0.0, "y": 0.0}
        api_client.post("/simulation/dock", dock_position)
        
        # 将设备放置在远离充电座的位置
        api_client.post("/simulation/position", {"x": 3.0, "y": 2.0})
        
        # 命令设备回充
        api_client.post("/device/dock", {})
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备处于回充状态
        assert status.get("returning_to_dock"), "设备未进入回充状态"
        
        # 等待足够时间让设备返回充电座（实际测试中可能需要更长时间）
        # 这里设置一个较短的时间以保持测试高效
        time.sleep(15)
        
        # 获取设备最新状态和位置
        status = api_client.get("/device/status").json()
        position = api_client.get("/device/position").json()
        
        # 验证设备是否成功对接充电座
        assert status.get("docked"), "设备未成功对接充电座"
        
        # 验证设备位置接近充电座
        assert abs(position["x"] - dock_position["x"]) < 0.1, "设备未能精确对接充电座X位置"
        assert abs(position["y"] - dock_position["y"]) < 0.1, "设备未能精确对接充电座Y位置"
    
    def test_multiroom_navigation(self, setup_device):
        """测试多房间导航功能"""
        api_client = setup_device
        
        # 上传一个预定义的多房间地图
        with open("data/multiroom_map.json", "r") as f:
            map_data = json.load(f)
        
        api_client.post("/maps/load", {"map_data": map_data})
        
        # 定义要清扫的房间ID列表
        room_ids = ["living_room", "kitchen"]
        
        # 开始多房间清扫
        api_client.post("/cleaning/rooms", {"room_ids": room_ids})
        
        # 等待足够时间让设备开始清扫
        time.sleep(5)
        
        # 获取设备状态
        status = api_client.get("/device/status").json()
        
        # 验证设备处于清扫状态
        assert status["working"], "设备未进入清扫状态"
        assert status.get("cleaning_mode") == "room", "设备未进入房间清扫模式"
        
        # 获取当前清扫房间信息
        cleaning_info = api_client.get("/cleaning/current").json()
        
        # 验证清扫的房间在指定列表中
        assert cleaning_info.get("current_room") in room_ids, "当前清扫的房间不在指定列表中"
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"}) 