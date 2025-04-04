#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API客户端
用于发送API请求和处理响应
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class ApiClient:
    """
    API客户端类
    封装HTTP请求方法，处理请求和响应
    """
    def __init__(self, base_url: str, timeout: int = 10, headers: Optional[Dict[str, str]] = None):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间（秒）
            headers: 请求头
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = headers or {'Content-Type': 'application/json'}
        self.session = requests.Session()
        
        logger.info(f"API客户端初始化，基础URL: {self.base_url}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        发送GET请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            HTTP响应对象
        """
        url = self._build_url(endpoint)
        logger.debug(f"GET请求: {url}, 参数: {params}")
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"GET请求异常: {e}, URL: {url}")
            raise
    
    def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None) -> requests.Response:
        """
        发送POST请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            HTTP响应对象
        """
        url = self._build_url(endpoint)
        logger.debug(f"POST请求: {url}, 数据: {data}")
        
        try:
            # 如果data是字典，转换为JSON字符串
            if isinstance(data, dict):
                data = json.dumps(data)
                
            response = self.session.post(
                url,
                data=data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"POST请求异常: {e}, URL: {url}")
            raise
    
    def put(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None) -> requests.Response:
        """
        发送PUT请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            HTTP响应对象
        """
        url = self._build_url(endpoint)
        logger.debug(f"PUT请求: {url}, 数据: {data}")
        
        try:
            # 如果data是字典，转换为JSON字符串
            if isinstance(data, dict):
                data = json.dumps(data)
                
            response = self.session.put(
                url,
                data=data,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"PUT请求异常: {e}, URL: {url}")
            raise
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        发送DELETE请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            HTTP响应对象
        """
        url = self._build_url(endpoint)
        logger.debug(f"DELETE请求: {url}, 参数: {params}")
        
        try:
            response = self.session.delete(
                url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"DELETE请求异常: {e}, URL: {url}")
            raise
    
    def _build_url(self, endpoint: str) -> str:
        """
        构建完整的URL
        
        Args:
            endpoint: API端点
            
        Returns:
            完整URL
        """
        # 确保endpoint以/开头
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        return f"{self.base_url}{endpoint}"
    
    def _log_response(self, response: requests.Response) -> None:
        """
        记录响应信息
        
        Args:
            response: HTTP响应对象
        """
        log_message = (
            f"响应: 状态码={response.status_code}, "
            f"URL={response.url}, "
            f"时间={response.elapsed.total_seconds()}s"
        )
        
        if response.status_code >= 400:
            logger.warning(log_message)
            logger.warning(f"响应内容: {response.text}")
        else:
            logger.debug(log_message)
            logger.debug(f"响应内容: {response.text}") 