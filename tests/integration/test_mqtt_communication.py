#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MQTT通信测试
测试扫地机器人与服务器之间的MQTT通信
"""

import os
import pytest
import logging
import yaml
import time
import json
from typing import Dict, Any

from libs.api_client import ApiClient
from libs.mqtt_client import MqttClient

logger = logging.getLogger(__name__)

class TestMqttCommunication:
    """
    MQTT通信测试类
    测试扫地机器人与服务器之间的MQTT通信
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
    
    @pytest.fixture(scope="function")
    def mqtt_client(self):
        """
        MQTT客户端fixture
        
        Returns:
            MqttClient: MQTT客户端实例
        """
        # 加载配置
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        env_config_path = os.path.join(config_dir, "env_config.yaml")
        
        with open(env_config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 使用开发环境配置
        mqtt_config = config['dev']['mqtt']
        client = MqttClient(
            broker=mqtt_config['broker'],
            port=mqtt_config['port'],
            client_id="test_client",
            username=mqtt_config['username'],
            password=mqtt_config['password']
        )
        
        # 连接MQTT服务器
        connected = client.connect()
        assert connected, "无法连接到MQTT服务器"
        
        logger.info(f"创建MQTT客户端: {mqtt_config['broker']}:{mqtt_config['port']}")
        yield client
        
        # 断开连接
        client.disconnect()
    
    @pytest.fixture(scope="function")
    def device_id(self):
        """
        设备ID fixture
        
        Returns:
            str: 设备ID
        """
        # 加载配置
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        config_path = os.path.join(config_dir, "config.yaml")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        device_id = config['device']['default_id']
        return device_id
    
    def test_status_update_notification(self, mqtt_client: MqttClient, api_client: ApiClient, device_id: str):
        """
        测试设备状态变更的MQTT通知
        """
        logger.info("测试设备状态变更的MQTT通知")
        
        # 订阅状态主题
        status_topic = f"device/{device_id}/status"
        mqtt_client.subscribe(status_topic)
        
        # 清除之前的消息
        mqtt_client.clear_received_messages()
        
        # 通过API改变设备状态
        api_client.post("/device/power", {"state": "on"})
        time.sleep(0.5)  # 等待消息发送
        
        api_client.post("/device/mode", {"mode": "strong"})
        time.sleep(0.5)  # 等待消息发送
        
        # 获取接收到的消息
        messages = mqtt_client.get_received_messages(status_topic)
        
        # 断言接收到了状态更新消息
        assert len(messages) >= 2, f"未接收到足够的状态更新消息，实际接收: {len(messages)}"
        
        # 验证消息内容
        last_message = messages[-1]
        payload = last_message["payload"]
        
        # 如果payload是字符串，尝试解析为JSON
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                pass
        
        # 检查状态更新内容
        if isinstance(payload, dict):
            assert "mode" in payload, "状态更新消息中没有模式信息"
            assert payload["mode"] == "strong", f"模式信息不正确: {payload['mode']}"
        else:
            assert "strong" in str(payload), f"状态更新消息中没有模式信息: {payload}"
    
    def test_command_execution(self, mqtt_client: MqttClient, api_client: ApiClient, device_id: str):
        """
        测试通过MQTT发送命令控制设备
        """
        logger.info("测试通过MQTT发送命令控制设备")
        
        # 获取初始状态
        status_response = api_client.get("/device/status")
        initial_status = status_response.json()
        
        # 确保设备开机
        if not initial_status.get('power', False):
            api_client.post("/device/power", {"state": "on"})
            time.sleep(0.5)  # 等待设备状态更新
        
        # 设置回初始模式
        api_client.post("/device/mode", {"mode": "standard"})
        time.sleep(0.5)  # 等待设备状态更新
        
        # 命令主题
        command_topic = f"device/{device_id}/command"
        
        # 通过MQTT发送命令设置模式
        mode_command = {"action": "set_mode", "params": {"mode": "eco"}}
        mqtt_client.publish(command_topic, json.dumps(mode_command))
        
        # 等待命令执行
        time.sleep(1)
        
        # 验证设备状态已更改
        status_response = api_client.get("/device/status")
        current_status = status_response.json()
        assert current_status.get('mode') == "eco", f"模式设置失败: {current_status.get('mode')}"
        
        # 测试开始清扫命令
        clean_command = {"action": "start_cleaning"}
        mqtt_client.publish(command_topic, json.dumps(clean_command))
        
        # 等待命令执行
        time.sleep(1)
        
        # 验证清扫状态
        status_response = api_client.get("/device/status")
        current_status = status_response.json()
        assert current_status.get('working') == True, "清扫未开始"
        
        # 测试停止清扫命令
        stop_command = {"action": "stop_cleaning"}
        mqtt_client.publish(command_topic, json.dumps(stop_command))
        
        # 等待命令执行
        time.sleep(1)
        
        # 验证清扫状态
        status_response = api_client.get("/device/status")
        current_status = status_response.json()
        assert current_status.get('working') == False, "清扫未停止"
    
    def test_error_reporting(self, mqtt_client: MqttClient, api_client: ApiClient, device_id: str):
        """
        测试错误报告通知
        """
        logger.info("测试错误报告通知")
        
        # 订阅错误主题
        error_topic = f"device/{device_id}/error"
        mqtt_client.subscribe(error_topic)
        
        # 清除之前的消息
        mqtt_client.clear_received_messages()
        
        # 设置错误状态
        api_client.post("/device/error", {"error_code": 1})  # 1表示尘盒已满
        
        # 等待消息发送
        time.sleep(1)
        
        # 获取接收到的消息
        messages = mqtt_client.get_received_messages(error_topic)
        
        # 断言接收到了错误消息
        assert len(messages) >= 1, "未接收到错误报告消息"
        
        # 验证错误消息内容
        error_message = messages[0]
        payload = error_message["payload"]
        
        # 如果payload是字符串，尝试解析为JSON
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                pass
        
        # 检查错误消息内容
        if isinstance(payload, dict):
            assert "error_code" in payload, "错误消息中没有错误代码"
            assert payload["error_code"] == 1, f"错误代码不正确: {payload['error_code']}"
        else:
            assert "1" in str(payload), f"错误消息中没有正确的错误代码: {payload}"
        
        # 清除错误状态
        api_client.post("/device/error", {"error_code": 0})
    
    def test_multiple_device_communication(self, mqtt_client: MqttClient, api_client: ApiClient):
        """
        测试多设备通信
        """
        logger.info("测试多设备通信")
        
        # 获取不同设备ID
        device_ids = ["SV001", "SV002", "SV003"]
        
        for device_id in device_ids:
            # 订阅设备状态主题
            status_topic = f"device/{device_id}/status"
            mqtt_client.subscribe(status_topic)
        
        # 清除之前的消息
        mqtt_client.clear_received_messages()
        
        # 为每个设备发送不同的命令
        for i, device_id in enumerate(device_ids):
            # 命令主题
            command_topic = f"device/{device_id}/command"
            
            # 不同的模式命令
            modes = ["standard", "strong", "eco"]
            mode_command = {"action": "set_mode", "params": {"mode": modes[i]}}
            
            # 通过MQTT发送命令
            mqtt_client.publish(command_topic, json.dumps(mode_command))
            
            # 等待命令执行
            time.sleep(0.5)
        
        # 等待所有消息接收
        time.sleep(1)
        
        # 获取接收到的所有消息
        all_messages = mqtt_client.get_received_messages()
        
        # 按设备ID分组消息
        device_messages = {}
        for message in all_messages:
            topic = message["topic"]
            parts = topic.split('/')
            if len(parts) >= 3:
                device_id = parts[1]
                if device_id not in device_messages:
                    device_messages[device_id] = []
                device_messages[device_id].append(message)
        
        # 断言每个设备都收到了消息
        for device_id in device_ids:
            assert device_id in device_messages, f"设备 {device_id} 未收到消息"
            assert len(device_messages[device_id]) > 0, f"设备 {device_id} 未收到消息" 