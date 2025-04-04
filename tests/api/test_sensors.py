#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传感器数据测试
测试扫地机器人的传感器数据反馈
"""

import os
import pytest
import logging
import yaml
import time
from typing import Dict, Any

from libs.api_client import ApiClient

logger = logging.getLogger(__name__)

class TestSensors:
    """
    传感器数据测试类
    测试扫地机器人的传感器数据反馈
    """
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """
        API客户端fixture
        
        Returns:
            ApiClient: API客户端实例
        """
        # 加载配置
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        env_config_path = os.path.join(config_dir, "env_config.yaml")
        
        with open(env_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 使用开发环境配置
        api_config = config['dev']['api']
        client = ApiClient(base_url=api_config['base_url'], timeout=api_config['timeout'])
        
        # 确保设备开机
        client.post("/device/power", {"state": "on"})
        
        logger.info(f"创建API客户端: {api_config['base_url']}")
        yield client
        
        # 测试结束后关闭设备
        client.post("/device/power", {"state": "off"})
    
    def test_bumper_sensor(self, api_client: ApiClient):
        """
        测试碰撞传感器响应
        """
        logger.info("测试碰撞传感器响应")
        
        # 设置障碍物
        obstacle = {"x": 0.05, "y": 0}  # 放置在设备前方很近的位置
        api_client.post("/simulation/obstacle", {"obstacles": [obstacle]})
        
        # 让设备向前移动
        api_client.post("/device/move", {"direction": "forward", "distance": 0.1})
        
        # 获取传感器数据
        sensor_response = api_client.get("/device/sensors")
        sensor_data = sensor_response.json()
        
        # 断言碰撞传感器被触发
        assert sensor_data.get('bumper') == True, "碰撞传感器未被触发"
        
        # 清除障碍物
        api_client.post("/simulation/obstacle", {"obstacles": []})
    
    def test_cliff_sensors(self, api_client: ApiClient):
        """
        测试悬崖传感器响应
        """
        logger.info("测试悬崖传感器响应")
        
        # 模拟设备位于悬崖边缘
        api_client.post("/simulation/environment", {"cliffs": [{"x": 0, "y": 0.1, "width": 0.5}]})
        
        # 让设备向前移动
        api_client.post("/device/move", {"direction": "forward", "distance": 0.15})
        
        # 获取传感器数据
        sensor_response = api_client.get("/device/sensors")
        sensor_data = sensor_response.json()
        
        # 断言至少一个悬崖传感器被触发
        assert any(sensor_data.get('cliff', [False, False, False, False])), "悬崖传感器未被触发"
        
        # 清除悬崖
        api_client.post("/simulation/environment", {"cliffs": []})
    
    def test_wheel_speed_in_different_modes(self, api_client: ApiClient):
        """
        测试不同清扫模式下的轮子速度
        """
        logger.info("测试不同清扫模式下的轮子速度")
        
        # 测试各种模式下的轮子速度
        modes = ["standard", "strong", "eco"]
        speeds = {}
        
        for mode in modes:
            # 设置模式
            api_client.post("/device/mode", {"mode": mode})
            
            # 开始清扫
            api_client.post("/device/clean", {"action": "start"})
            
            # 等待速度稳定
            time.sleep(0.5)
            
            # 获取传感器数据
            sensor_response = api_client.get("/device/sensors")
            sensor_data = sensor_response.json()
            
            # 记录速度
            speeds[mode] = sensor_data.get('wheel_speed', [0, 0])
            
            # 停止清扫
            api_client.post("/device/clean", {"action": "stop"})
        
        # 断言不同模式下速度不同
        assert speeds["standard"] != speeds["strong"], "标准模式和强力模式速度相同"
        assert speeds["standard"] != speeds["eco"], "标准模式和节能模式速度相同"
        assert speeds["strong"] != speeds["eco"], "强力模式和节能模式速度相同"
        
        # 断言强力模式速度最大
        assert speeds["strong"][0] > speeds["standard"][0], "强力模式速度不大于标准模式"
        assert speeds["strong"][0] > speeds["eco"][0], "强力模式速度不大于节能模式"
        
        # 断言节能模式速度最小
        assert speeds["eco"][0] < speeds["standard"][0], "节能模式速度不小于标准模式"
        assert speeds["eco"][0] < speeds["strong"][0], "节能模式速度不小于强力模式"
    
    def test_battery_consumption(self, api_client: ApiClient):
        """
        测试电池消耗
        """
        logger.info("测试电池消耗")
        
        # 获取初始电池电量
        status_response = api_client.get("/device/status")
        initial_status = status_response.json()
        initial_battery = initial_status.get('battery', 100)
        
        # 开始清扫10秒
        api_client.post("/device/clean", {"action": "start"})
        
        # 模拟时间推移
        time.sleep(5)
        
        # 获取当前电池电量
        status_response = api_client.get("/device/status")
        current_status = status_response.json()
        current_battery = current_status.get('battery', 100)
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"})
        
        # 断言电池电量有所减少
        assert current_battery < initial_battery, f"电池电量未减少: 初始 {initial_battery}, 当前 {current_battery}"
        
        # 断言减少的电量在合理范围内
        consumed = initial_battery - current_battery
        assert 0 < consumed < 20, f"电池消耗不在合理范围内: {consumed}"
    
    def test_dust_bin_accumulation(self, api_client: ApiClient):
        """
        测试尘盒灰尘积累
        """
        logger.info("测试尘盒灰尘积累")
        
        # 清空尘盒
        api_client.post("/device/maintenance", {"action": "empty_dust_bin"})
        
        # 获取初始尘盒状态
        status_response = api_client.get("/device/status")
        initial_status = status_response.json()
        initial_dust_bin = initial_status.get('dust_bin', 0)
        
        # 断言尘盒为空
        assert initial_dust_bin == 0, f"尘盒未清空: {initial_dust_bin}"
        
        # 开始清扫10秒
        api_client.post("/device/clean", {"action": "start"})
        
        # 模拟时间推移
        time.sleep(5)
        
        # 获取当前尘盒状态
        status_response = api_client.get("/device/status")
        current_status = status_response.json()
        current_dust_bin = current_status.get('dust_bin', 0)
        
        # 停止清扫
        api_client.post("/device/clean", {"action": "stop"})
        
        # 断言尘盒灰尘有所增加
        assert current_dust_bin > initial_dust_bin, f"尘盒灰尘未增加: 初始 {initial_dust_bin}, 当前 {current_dust_bin}" 