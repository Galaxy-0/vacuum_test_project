#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志工具类
用于配置和管理日志
"""

import os
import logging
import logging.handlers
import time
import yaml
from typing import Dict, Any, Optional

class LogUtils:
    """
    日志工具类
    用于配置和管理日志
    """
    @staticmethod
    def setup_logging(
        config_file: Optional[str] = None,
        log_level: str = "INFO",
        log_format: Optional[str] = None,
        log_file: Optional[str] = None
    ) -> None:
        """
        配置日志系统
        
        Args:
            config_file: 配置文件路径，如果提供，将从配置文件读取配置
            log_level: 日志级别
            log_format: 日志格式
            log_file: 日志文件路径
        """
        # 如果提供了配置文件，从配置文件读取配置
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                logging_config = config.get('logging', {})
                log_level = logging_config.get('level', log_level)
                log_format = logging_config.get('format', log_format)
                log_file = logging_config.get('file', log_file)
            except Exception as e:
                print(f"读取日志配置文件失败: {e}")
        
        # 默认日志格式
        if not log_format:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # 创建根日志记录器
        root_logger = logging.getLogger()
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 设置日志级别
        level = getattr(logging, log_level.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(console_handler)
        
        # 如果提供了日志文件，创建文件处理器
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # 创建文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(log_format))
            root_logger.addHandler(file_handler)
        
        logging.info(f"日志系统已配置，级别: {log_level}, 文件: {log_file}")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志记录器对象
        """
        return logging.getLogger(name)

    @staticmethod
    def log_test_start(logger: logging.Logger, test_name: str) -> None:
        """
        记录测试开始
        
        Args:
            logger: 日志记录器
            test_name: 测试名称
        """
        logger.info("=" * 50)
        logger.info(f"开始测试: {test_name}")
        logger.info("=" * 50)

    @staticmethod
    def log_test_end(logger: logging.Logger, test_name: str, success: bool = True) -> None:
        """
        记录测试结束
        
        Args:
            logger: 日志记录器
            test_name: 测试名称
            success: 测试是否成功
        """
        logger.info("=" * 50)
        if success:
            logger.info(f"测试成功: {test_name}")
        else:
            logger.warning(f"测试失败: {test_name}")
        logger.info("=" * 50)

    @staticmethod
    def log_step(logger: logging.Logger, step_name: str) -> None:
        """
        记录测试步骤
        
        Args:
            logger: 日志记录器
            step_name: 步骤名称
        """
        logger.info("-" * 30)
        logger.info(f"步骤: {step_name}")
        logger.info("-" * 30)

    @staticmethod
    def log_api_request(logger: logging.Logger, method: str, url: str, data: Any = None) -> None:
        """
        记录API请求
        
        Args:
            logger: 日志记录器
            method: 请求方法
            url: 请求URL
            data: 请求数据
        """
        logger.debug(f"API请求: {method} {url}")
        if data:
            logger.debug(f"请求数据: {data}")

    @staticmethod
    def log_api_response(logger: logging.Logger, status_code: int, response_data: Any) -> None:
        """
        记录API响应
        
        Args:
            logger: 日志记录器
            status_code: 状态码
            response_data: 响应数据
        """
        if status_code >= 400:
            logger.warning(f"API响应: 状态码={status_code}")
            logger.warning(f"响应数据: {response_data}")
        else:
            logger.debug(f"API响应: 状态码={status_code}")
            logger.debug(f"响应数据: {response_data}")

    @staticmethod
    def log_error(logger: logging.Logger, error_msg: str, exc: Optional[Exception] = None) -> None:
        """
        记录错误
        
        Args:
            logger: 日志记录器
            error_msg: 错误消息
            exc: 异常对象
        """
        if exc:
            logger.error(f"{error_msg}: {exc}", exc_info=True)
        else:
            logger.error(error_msg) 