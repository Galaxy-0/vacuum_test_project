#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基本功能测试
测试扫地机器人的基本功能，如开关机、设置模式等
"""

import os
import pytest
import logging
import yaml
import time
from typing import Dict, Any

from libs.api_client import ApiClient

logger = logging.getLogger(__name__)

class TestBasicFunctions:
    """
    基本功能测试类
    测试扫地机器人的基本功能，如开关机、设置模式等
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
        
        logger.info(f"创建API客户端: {api_config['base_url']}")
        yield client
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """
        测试数据fixture
        
        Returns:
            Dict: 测试数据
        """
        # 加载测试数据
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        data_path = os.path.join(data_dir, "api_test_data.yaml")
        
        with open(data_path, 'r') as f:
            test_data = yaml.safe_load(f)
        
        logger.info("加载测试数据")
        return test_data
    
    def test_power_on(self, api_client: ApiClient, test_data: Dict[str, Any]):
        """
        测试开机功能
        """
        logger.info("测试开机功能")
        
        # 获取测试数据
        data = test_data['power_test']['power_on']
        
        # 发送请求
        response = api_client.post("/device/power", data['request'])
        
        # 断言响应状态码
        assert response.status_code == data['expected']['status_code'], \
            f"状态码不匹配: 期望 {data['expected']['status_code']}, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == data['expected']['result'], \
            f"结果不匹配: 期望 {data['expected']['result']}, 实际 {response_data['result']}"
        
        # 验证设备状态
        status_response = api_client.get("/device/status")
        status = status_response.json()
        assert status['power'] == True, "设备未开机"
    
    def test_power_off(self, api_client: ApiClient, test_data: Dict[str, Any]):
        """
        测试关机功能
        """
        logger.info("测试关机功能")
        
        # 先确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 获取测试数据
        data = test_data['power_test']['power_off']
        
        # 发送请求
        response = api_client.post("/device/power", data['request'])
        
        # 断言响应状态码
        assert response.status_code == data['expected']['status_code'], \
            f"状态码不匹配: 期望 {data['expected']['status_code']}, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == data['expected']['result'], \
            f"结果不匹配: 期望 {data['expected']['result']}, 实际 {response_data['result']}"
        
        # 验证设备状态
        status_response = api_client.get("/device/status")
        status = status_response.json()
        assert status['power'] == False, "设备未关机"
    
    @pytest.mark.parametrize("mode_data", ["standard", "strong", "eco"])
    def test_set_valid_mode(self, api_client: ApiClient, mode_data: str):
        """
        测试设置有效的清扫模式
        
        Args:
            mode_data: 清扫模式
        """
        logger.info(f"测试设置有效的清扫模式: {mode_data}")
        
        # 先确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 发送请求
        response = api_client.post("/device/mode", {"mode": mode_data})
        
        # 断言响应状态码
        assert response.status_code == 200, \
            f"状态码不匹配: 期望 200, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == "success", \
            f"结果不匹配: 期望 success, 实际 {response_data['result']}"
        
        # 验证设备状态
        status_response = api_client.get("/device/status")
        status = status_response.json()
        assert status['mode'] == mode_data, f"模式设置失败: 期望 {mode_data}, 实际 {status['mode']}"
    
    def test_set_invalid_mode(self, api_client: ApiClient, test_data: Dict[str, Any]):
        """
        测试设置无效的清扫模式
        """
        logger.info("测试设置无效的清扫模式")
        
        # 先确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 获取测试数据
        data = test_data['mode_test']['invalid_mode']
        
        # 发送请求
        response = api_client.post("/device/mode", {"mode": data['mode']})
        
        # 断言响应状态码
        assert response.status_code == data['expected']['status_code'], \
            f"状态码不匹配: 期望 {data['expected']['status_code']}, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == data['expected']['result'], \
            f"结果不匹配: 期望 {data['expected']['result']}, 实际 {response_data['result']}"
    
    def test_start_cleaning(self, api_client: ApiClient, test_data: Dict[str, Any]):
        """
        测试开始清扫
        """
        logger.info("测试开始清扫")
        
        # 先确保设备开机
        api_client.post("/device/power", {"state": "on"})
        
        # 获取测试数据
        data = test_data['cleaning_test']['start']
        
        # 发送请求
        response = api_client.post("/device/clean", data['request'])
        
        # 断言响应状态码
        assert response.status_code == data['expected']['status_code'], \
            f"状态码不匹配: 期望 {data['expected']['status_code']}, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == data['expected']['result'], \
            f"结果不匹配: 期望 {data['expected']['result']}, 实际 {response_data['result']}"
        
        # 验证设备状态
        status_response = api_client.get("/device/status")
        status = status_response.json()
        assert status['working'] == data['expected']['working'], \
            f"工作状态不匹配: 期望 {data['expected']['working']}, 实际 {status['working']}"
    
    def test_stop_cleaning(self, api_client: ApiClient, test_data: Dict[str, Any]):
        """
        测试停止清扫
        """
        logger.info("测试停止清扫")
        
        # 先确保设备开机并开始清扫
        api_client.post("/device/power", {"state": "on"})
        api_client.post("/device/clean", {"action": "start"})
        
        # 等待清扫开始
        time.sleep(1)
        
        # 获取测试数据
        data = test_data['cleaning_test']['stop']
        
        # 发送请求
        response = api_client.post("/device/clean", data['request'])
        
        # 断言响应状态码
        assert response.status_code == data['expected']['status_code'], \
            f"状态码不匹配: 期望 {data['expected']['status_code']}, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == data['expected']['result'], \
            f"结果不匹配: 期望 {data['expected']['result']}, 实际 {response_data['result']}"
        
        # 验证设备状态
        status_response = api_client.get("/device/status")
        status = status_response.json()
        assert status['working'] == data['expected']['working'], \
            f"工作状态不匹配: 期望 {data['expected']['working']}, 实际 {status['working']}"
    
    def test_start_cleaning_without_power(self, api_client: ApiClient):
        """
        测试在关机状态下开始清扫
        """
        logger.info("测试在关机状态下开始清扫")
        
        # 确保设备关机
        api_client.post("/device/power", {"state": "off"})
        
        # 发送请求
        response = api_client.post("/device/clean", {"action": "start"})
        
        # 断言响应状态码
        assert response.status_code == 400, \
            f"状态码不匹配: 期望 400, 实际 {response.status_code}"
        
        # 断言响应结果
        response_data = response.json()
        assert response_data['result'] == "error", \
            f"结果不匹配: 期望 error, 实际 {response_data['result']}"
        assert "设备未开机" in response_data.get('message', ""), \
            f"错误消息不匹配: 应包含 '设备未开机', 实际 {response_data.get('message', '')}" 