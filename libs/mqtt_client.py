#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MQTT客户端
用于与设备进行MQTT通信
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Callable, List
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MqttClient:
    """
    MQTT客户端类
    封装MQTT通信功能，处理消息发布和订阅
    """
    def __init__(
        self,
        broker: str,
        port: int = 1883,
        client_id: str = "",
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        timeout: int = 60
    ):
        """
        初始化MQTT客户端
        
        Args:
            broker: MQTT服务器地址
            port: MQTT服务器端口
            client_id: 客户端ID
            username: 用户名
            password: 密码
            use_ssl: 是否使用SSL
            timeout: 连接超时时间（秒）
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        
        # 创建MQTT客户端
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        
        # 设置认证信息
        if username and password:
            self.client.username_pw_set(username, password)
        
        # 设置SSL
        if use_ssl:
            self.client.tls_set()
        
        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe
        
        # 消息回调函数映射
        self.topic_callbacks = {}
        
        # 已接收消息列表
        self.received_messages = []
        
        logger.info(f"MQTT客户端初始化，服务器: {broker}:{port}")
    
    def connect(self) -> bool:
        """
        连接到MQTT服务器
        
        Returns:
            是否连接成功
        """
        try:
            logger.info(f"连接到MQTT服务器 {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            
            # 等待连接完成
            start_time = time.time()
            while not self.client.is_connected() and time.time() - start_time < self.timeout:
                time.sleep(0.1)
            
            if not self.client.is_connected():
                logger.error(f"连接MQTT服务器超时: {self.broker}:{self.port}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"连接MQTT服务器失败: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开MQTT连接"""
        logger.info("断开MQTT连接")
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """
        发布MQTT消息
        
        Args:
            topic: 主题
            payload: 消息内容
            qos: 服务质量
            retain: 是否保留消息
            
        Returns:
            是否发布成功
        """
        try:
            # 如果payload不是字符串，尝试转换为JSON
            if not isinstance(payload, str):
                payload = json.dumps(payload)
            
            logger.debug(f"发布MQTT消息: 主题={topic}, 内容={payload}")
            result = self.client.publish(topic, payload, qos, retain)
            
            # 检查发布结果
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.warning(f"发布MQTT消息失败: {result}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"发布MQTT消息异常: {e}")
            return False
    
    def subscribe(self, topic: str, callback: Callable = None, qos: int = 0) -> bool:
        """
        订阅MQTT主题
        
        Args:
            topic: 主题
            callback: 消息回调函数
            qos: 服务质量
            
        Returns:
            是否订阅成功
        """
        try:
            logger.debug(f"订阅MQTT主题: {topic}")
            result, _ = self.client.subscribe(topic, qos)
            
            # 注册回调函数
            if callback:
                self.topic_callbacks[topic] = callback
            
            # 检查订阅结果
            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.warning(f"订阅MQTT主题失败: {result}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"订阅MQTT主题异常: {e}")
            return False
    
    def unsubscribe(self, topic: str) -> bool:
        """
        取消订阅MQTT主题
        
        Args:
            topic: 主题
            
        Returns:
            是否取消订阅成功
        """
        try:
            logger.debug(f"取消订阅MQTT主题: {topic}")
            result, _ = self.client.unsubscribe(topic)
            
            # 移除回调函数
            if topic in self.topic_callbacks:
                del self.topic_callbacks[topic]
            
            # 检查取消订阅结果
            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.warning(f"取消订阅MQTT主题失败: {result}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"取消订阅MQTT主题异常: {e}")
            return False
    
    def get_received_messages(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取接收到的消息
        
        Args:
            topic: 过滤特定主题的消息，为None则返回所有消息
            
        Returns:
            消息列表
        """
        if topic:
            return [msg for msg in self.received_messages if msg["topic"] == topic]
        else:
            return self.received_messages
    
    def clear_received_messages(self) -> None:
        """清空接收到的消息列表"""
        self.received_messages = []
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        连接回调函数
        
        Args:
            client: MQTT客户端
            userdata: 用户数据
            flags: 连接标志
            rc: 连接结果代码
        """
        if rc == 0:
            logger.info("已连接到MQTT服务器")
        else:
            logger.error(f"连接MQTT服务器失败，代码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """
        断开连接回调函数
        
        Args:
            client: MQTT客户端
            userdata: 用户数据
            rc: 断开连接结果代码
        """
        if rc == 0:
            logger.info("已断开MQTT连接")
        else:
            logger.warning(f"MQTT连接异常断开，代码: {rc}")
    
    def _on_message(self, client, userdata, message):
        """
        消息回调函数
        
        Args:
            client: MQTT客户端
            userdata: 用户数据
            message: 接收到的消息
        """
        topic = message.topic
        payload = message.payload.decode()
        
        # 记录接收到的消息
        try:
            # 尝试解析JSON
            payload_json = json.loads(payload)
            msg_data = payload_json
        except:
            # 如果不是JSON，保持原始字符串
            msg_data = payload
        
        # 将消息添加到接收列表
        timestamp = time.time()
        received_msg = {
            "topic": topic,
            "payload": msg_data,
            "timestamp": timestamp,
            "qos": message.qos,
            "retain": message.retain
        }
        self.received_messages.append(received_msg)
        
        logger.debug(f"接收到MQTT消息: 主题={topic}, 内容={payload}")
        
        # 处理特定主题的回调
        if topic in self.topic_callbacks:
            try:
                self.topic_callbacks[topic](client, userdata, message)
            except Exception as e:
                logger.error(f"处理MQTT消息回调异常: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """
        消息发布回调函数
        
        Args:
            client: MQTT客户端
            userdata: 用户数据
            mid: 消息ID
        """
        logger.debug(f"MQTT消息已发布: mid={mid}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """
        主题订阅回调函数
        
        Args:
            client: MQTT客户端
            userdata: 用户数据
            mid: 消息ID
            granted_qos: 授予的服务质量
        """
        logger.debug(f"MQTT主题已订阅: mid={mid}, qos={granted_qos}") 