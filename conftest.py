#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pytest配置文件
"""

import os
import sys
import pytest
import logging
import yaml

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.log_utils import LogUtils

def pytest_configure(config):
    """
    Pytest配置函数
    在测试开始前配置环境
    
    Args:
        config: Pytest配置对象
    """
    # 加载配置
    config_path = os.path.join(project_root, "config", "config.yaml")
    
    # 配置日志
    LogUtils.setup_logging(config_file=config_path)
    
    # 输出测试环境信息
    logging.info("=" * 60)
    logging.info("开始扫地机器人测试")
    logging.info(f"项目路径: {project_root}")
    logging.info(f"Python版本: {sys.version}")
    logging.info("=" * 60)

def pytest_addoption(parser):
    """
    添加命令行选项
    
    Args:
        parser: 命令行参数解析器
    """
    parser.addoption("--env", action="store", default="dev", help="指定测试环境: dev, test, prod")
    parser.addoption("--device", action="store", default="SV001", help="指定测试设备ID")

@pytest.fixture(scope="session")
def env(request):
    """
    环境fixture
    
    Args:
        request: Pytest请求对象
        
    Returns:
        str: 环境名称
    """
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def device_id(request):
    """
    设备ID fixture
    
    Args:
        request: Pytest请求对象
        
    Returns:
        str: 设备ID
    """
    return request.config.getoption("--device")

@pytest.fixture(scope="session")
def config(env):
    """
    配置fixture
    
    Args:
        env: 环境名称
        
    Returns:
        dict: 配置字典
    """
    # 加载全局配置
    config_path = os.path.join(project_root, "config", "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # 加载环境配置
    env_config_path = os.path.join(project_root, "config", "env_config.yaml")
    with open(env_config_path, 'r') as f:
        env_config = yaml.safe_load(f)
    
    # 合并配置
    if env in env_config:
        config['env'] = env
        config['env_config'] = env_config[env]
    else:
        config['env'] = 'dev'
        config['env_config'] = env_config['dev']
    
    return config

def pytest_runtest_setup(item):
    """
    测试用例开始前执行
    
    Args:
        item: 测试项
    """
    # 输出测试用例信息
    logging.info("=" * 60)
    logging.info(f"开始执行测试: {item.name}")
    logging.info(f"文件路径: {item.fspath}")
    logging.info("=" * 60)

def pytest_runtest_teardown(item, nextitem):
    """
    测试用例结束后执行
    
    Args:
        item: 测试项
        nextitem: 下一个测试项
    """
    # 输出测试用例结束信息
    logging.info("=" * 60)
    logging.info(f"测试执行完成: {item.name}")
    logging.info("=" * 60)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    生成测试报告
    
    Args:
        item: 测试项
        call: 测试调用
        
    Returns:
        测试报告
    """
    # 获取测试结果
    outcome = yield
    report = outcome.get_result()
    
    # 记录测试结果
    if report.when == "call":
        if report.passed:
            logging.info(f"测试通过: {item.name}")
        elif report.failed:
            logging.error(f"测试失败: {item.name}")
            if hasattr(report, "wasxfail"):
                logging.info("预期失败的测试")
            else:
                logging.error(f"错误信息: {call.excinfo}")
        elif report.skipped:
            logging.warning(f"测试跳过: {item.name}") 