#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扫地机器人设备模拟器
模拟扫地机器人的基本功能和状态，用于测试
"""

import time
import random
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class VacuumRobotSimulator:
    """
    扫地机器人模拟器类
    模拟扫地机器人的各种功能和状态，用于测试
    """
    def __init__(self, device_id: str = "SV001"):
        """
        初始化扫地机器人模拟器
        
        Args:
            device_id: 设备ID
        """
        self.device_id = device_id
        self.status = {
            "power": False,
            "battery": 100,
            "mode": "standard",  # standard, strong, eco
            "dust_bin": 0,       # 0-100%
            "water_tank": 100,   # 0-100%
            "working": False,
            "error_code": 0,
            "location": {"x": 0, "y": 0},
            "cleaning_area": 0,
            "cleaning_time": 0
        }
        self.sensors = {
            "cliff": [False, False, False, False],  # 四个悬崖传感器
            "bumper": False,                        # 碰撞传感器
            "wall": [0, 0, 0],                      # 墙壁检测传感器
            "wheel_speed": [0, 0],                  # 左右轮速度
            "brush_current": 0,                     # 刷子电流
            "lidar_data": []                        # 激光雷达数据
        }
        self._obstacles = []                        # 障碍物位置列表
        self._cleaning_thread = None                # 清扫线程
        self._is_charging = False                   # 是否正在充电
        self._start_time = 0                        # 开始清扫时间
        
        logger.info(f"设备 {device_id} 模拟器已初始化")
        
    def power_on(self) -> Dict[str, Any]:
        """开机"""
        logger.info(f"设备 {self.device_id} 开机")
        self.status["power"] = True
        return {"result": "success"}
        
    def power_off(self) -> Dict[str, Any]:
        """关机"""
        logger.info(f"设备 {self.device_id} 关机")
        if self.status["working"]:
            self._stop_cleaning()
        self.status["power"] = False
        self.status["working"] = False
        return {"result": "success"}
    
    def set_mode(self, mode: str) -> Dict[str, Any]:
        """
        设置清扫模式
        
        Args:
            mode: 清扫模式 (standard, strong, eco)
            
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 设置模式: {mode}")
        if not self.status["power"]:
            logger.warning(f"设备 {self.device_id} 未开机，无法设置模式")
            return {"result": "error", "message": "设备未开机"}
            
        if mode not in ["standard", "strong", "eco", "quiet", "max"]:
            logger.warning(f"设备 {self.device_id} 不支持的模式: {mode}")
            return {"result": "error", "message": "不支持的模式"}
            
        self.status["mode"] = mode
        return {"result": "success"}
    
    def start_cleaning(self) -> Dict[str, Any]:
        """
        开始清扫
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 开始清扫")
        if not self.status["power"]:
            logger.warning(f"设备 {self.device_id} 未开机，无法开始清扫")
            return {"result": "error", "message": "设备未开机"}
        
        # 检查电量是否足够
        if self.status["battery"] < 10:
            logger.warning(f"设备 {self.device_id} 电量低，无法开始清扫")
            return {"result": "error", "message": "电池电量低", "error_code": 2}
        
        # 检查尘盒是否已满
        if self.status["dust_bin"] >= 90:
            logger.warning(f"设备 {self.device_id} 尘盒已满，无法开始清扫")
            return {"result": "error", "message": "尘盒已满", "error_code": 1}
            
        self.status["working"] = True
        self._start_time = time.time()
        
        # 模拟清扫过程
        self._simulate_cleaning()
        
        return {
            "result": "success",
            "message": "正在清扫",
            "location": self.status["location"],
            "battery": self.status["battery"],
            "dust_bin": self.status["dust_bin"]
        }
    
    def stop_cleaning(self) -> Dict[str, Any]:
        """
        停止清扫
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 停止清扫")
        if not self.status["power"]:
            logger.warning(f"设备 {self.device_id} 未开机，无法停止清扫")
            return {"result": "error", "message": "设备未开机"}
            
        if not self.status["working"]:
            logger.warning(f"设备 {self.device_id} 未在清扫，无需停止")
            return {"result": "error", "message": "设备未在清扫"}
            
        self._stop_cleaning()
        return {"result": "success"}
    
    def _stop_cleaning(self) -> None:
        """内部方法：停止清扫过程"""
        self.status["working"] = False
        # 更新清扫时间
        cleaning_time = time.time() - self._start_time
        self.status["cleaning_time"] += int(cleaning_time / 60)  # 转换为分钟
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取设备状态
        
        Returns:
            设备状态信息
        """
        logger.debug(f"获取设备 {self.device_id} 状态")
        return self.status
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """
        获取传感器数据
        
        Returns:
            传感器数据
        """
        logger.debug(f"获取设备 {self.device_id} 传感器数据")
        return self.sensors
    
    def set_obstacle(self, obstacle_list: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        设置障碍物
        
        Args:
            obstacle_list: 障碍物位置列表
            
        Returns:
            操作结果
        """
        logger.info(f"设置设备 {self.device_id} 障碍物: {obstacle_list}")
        self._obstacles = obstacle_list
        self._update_sensors()
        return {"result": "success"}
    
    def move(self, direction: str, distance: float) -> Dict[str, Any]:
        """
        移动设备
        
        Args:
            direction: 移动方向 (forward, backward, left, right)
            distance: 移动距离
            
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 移动: {direction} {distance}")
        if not self.status["power"]:
            logger.warning(f"设备 {self.device_id} 未开机，无法移动")
            return {"result": "error", "message": "设备未开机"}
            
        # 模拟设备移动
        if direction == "forward":
            self.status["location"]["y"] += distance
        elif direction == "backward":
            self.status["location"]["y"] -= distance
        elif direction == "left":
            self.status["location"]["x"] -= distance
        elif direction == "right":
            self.status["location"]["x"] += distance
        else:
            logger.warning(f"设备 {self.device_id} 不支持的移动方向: {direction}")
            return {"result": "error", "message": "不支持的移动方向"}
        
        # 更新传感器数据
        self._update_sensors()
        
        # 更新电池电量
        self._update_battery(distance * 0.1)
        
        return {"result": "success"}
    
    def _update_sensors(self) -> None:
        """内部方法：更新传感器数据"""
        # 重置传感器状态
        self.sensors["bumper"] = False
        self.sensors["cliff"] = [False, False, False, False]
        
        # 检查是否碰到障碍物
        for obstacle in self._obstacles:
            # 计算与障碍物的距离
            dx = obstacle["x"] - self.status["location"]["x"]
            dy = obstacle["y"] - self.status["location"]["y"]
            distance = (dx**2 + dy**2)**0.5
            
            # 如果距离小于阈值，触发碰撞传感器
            if distance < 0.1:
                self.sensors["bumper"] = True
                logger.debug(f"设备 {self.device_id} 检测到碰撞")
                break
        
        # 模拟轮子速度
        if self.status["working"]:
            speed = 0
            if self.status["mode"] == "standard":
                speed = 5
            elif self.status["mode"] == "strong":
                speed = 7
            elif self.status["mode"] == "eco":
                speed = 3
            elif self.status["mode"] == "quiet":
                speed = 2
            elif self.status["mode"] == "max":
                speed = 9
            
            self.sensors["wheel_speed"] = [speed, speed]  # 左右轮速度
            self.sensors["brush_current"] = speed * 100  # 刷子电流
        else:
            self.sensors["wheel_speed"] = [0, 0]  # 停止
            self.sensors["brush_current"] = 0
    
    def _update_battery(self, consumption: float) -> None:
        """
        内部方法：更新电池电量
        
        Args:
            consumption: 电量消耗百分比
        """
        if self._is_charging:
            # 充电中，电量增加
            self.status["battery"] = min(100, self.status["battery"] + 0.5)
        else:
            # 放电中，电量减少
            self.status["battery"] = max(0, self.status["battery"] - consumption)
            
            # 如果电量耗尽，停止工作
            if self.status["battery"] == 0 and self.status["working"]:
                logger.warning(f"设备 {self.device_id} 电量耗尽，自动停止")
                self._stop_cleaning()
    
    def _simulate_cleaning(self) -> None:
        """内部方法：模拟清扫过程"""
        # 随机移动和收集灰尘
        if self.status["working"]:
            # 随机选择方向
            direction = random.choice(["forward", "backward", "left", "right"])
            distance = random.uniform(0.1, 0.5)
            
            # 移动设备
            self.move(direction, distance)
            
            # 增加清扫面积
            self.status["cleaning_area"] += random.uniform(0.1, 0.5)
            
            # 增加尘盒灰尘
            self.status["dust_bin"] = min(100, self.status["dust_bin"] + random.uniform(0.1, 0.5))
    
    def start_charging(self) -> Dict[str, Any]:
        """
        开始充电
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 开始充电")
        if self.status["working"]:
            self._stop_cleaning()
            
        self._is_charging = True
        return {"result": "success"}
    
    def stop_charging(self) -> Dict[str, Any]:
        """
        停止充电
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 停止充电")
        self._is_charging = False
        return {"result": "success"}
    
    def empty_dust_bin(self) -> Dict[str, Any]:
        """
        清空尘盒
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 清空尘盒")
        self.status["dust_bin"] = 0
        return {"result": "success"}
    
    def fill_water_tank(self) -> Dict[str, Any]:
        """
        加满水箱
        
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 加满水箱")
        self.status["water_tank"] = 100
        return {"result": "success"}
    
    def set_error(self, error_code: int) -> Dict[str, Any]:
        """
        设置错误状态
        
        Args:
            error_code: 错误代码
            
        Returns:
            操作结果
        """
        logger.info(f"设备 {self.device_id} 设置错误: {error_code}")
        self.status["error_code"] = error_code
        
        # 如果有严重错误，停止清扫
        if error_code > 0 and self.status["working"]:
            self._stop_cleaning()
            
        return {"result": "success"} 