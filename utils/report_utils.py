#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告工具类
用于生成测试报告
"""

import os
import json
import time
import datetime
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportUtils:
    """
    报告工具类
    用于生成测试报告
    """
    @staticmethod
    def create_report_dir(base_dir: str) -> str:
        """
        创建报告目录
        
        Args:
            base_dir: 基础目录
            
        Returns:
            报告目录路径
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(base_dir, f"report_{timestamp}")
        
        # 确保目录存在
        os.makedirs(report_dir, exist_ok=True)
        os.makedirs(os.path.join(report_dir, "screenshots"), exist_ok=True)
        
        logger.info(f"创建报告目录: {report_dir}")
        return report_dir
    
    @staticmethod
    def save_test_results(
        report_dir: str,
        results: List[Dict[str, Any]],
        report_name: str = "test_results.json"
    ) -> str:
        """
        保存测试结果
        
        Args:
            report_dir: 报告目录
            results: 测试结果列表
            report_name: 报告文件名
            
        Returns:
            报告文件路径
        """
        report_path = os.path.join(report_dir, report_name)
        
        # 计算统计信息
        total = len(results)
        passed = sum(1 for r in results if r.get('status') == 'passed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        
        # 生成摘要
        summary = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': f"{(passed / total * 100) if total > 0 else 0:.2f}%",
            'timestamp': datetime.datetime.now().isoformat(),
            'duration': sum(r.get('duration', 0) for r in results)
        }
        
        # 完整报告
        report = {
            'summary': summary,
            'results': results
        }
        
        # 保存为JSON文件
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"保存测试结果到: {report_path}")
        logger.info(f"测试摘要: 总数={total}, 通过={passed}, 失败={failed}, 跳过={skipped}")
        
        return report_path
    
    @staticmethod
    def generate_html_report(
        json_report_path: str,
        template_path: Optional[str] = None
    ) -> str:
        """
        生成HTML测试报告
        
        Args:
            json_report_path: JSON报告路径
            template_path: HTML模板路径
            
        Returns:
            HTML报告路径
        """
        try:
            # 读取JSON报告
            with open(json_report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # 生成HTML报告路径
            html_report_path = json_report_path.replace('.json', '.html')
            
            # 如果没有提供模板，使用默认模板
            if not template_path:
                html_content = ReportUtils._generate_default_html_report(report_data)
            else:
                # 读取模板
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                
                # 替换变量
                html_content = ReportUtils._apply_template(template, report_data)
            
            # 写入HTML报告
            with open(html_report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"生成HTML报告: {html_report_path}")
            return html_report_path
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return ""
    
    @staticmethod
    def _generate_default_html_report(report_data: Dict[str, Any]) -> str:
        """
        生成默认HTML报告
        
        Args:
            report_data: 报告数据
            
        Returns:
            HTML内容
        """
        summary = report_data['summary']
        results = report_data['results']
        
        # 生成HTML头部
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>扫地机器人测试报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
            padding: 20px;
        }}
        h1, h2 {{
            color: #333;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary-data {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }}
        .summary-item {{
            flex: 1;
            min-width: 150px;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
        }}
        .total {{
            background-color: #17a2b8;
            color: white;
        }}
        .passed {{
            background-color: #28a745;
            color: white;
        }}
        .failed {{
            background-color: #dc3545;
            color: white;
        }}
        .skipped {{
            background-color: #ffc107;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #ddd;
        }}
        .status-passed {{
            color: #28a745;
            font-weight: bold;
        }}
        .status-failed {{
            color: #dc3545;
            font-weight: bold;
        }}
        .status-skipped {{
            color: #ffc107;
            font-weight: bold;
        }}
        .error-message {{
            color: #dc3545;
            background-color: #f8d7da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>扫地机器人测试报告</h1>
        <div class="summary">
            <h2>测试摘要</h2>
            <p>执行时间: {summary['timestamp']}</p>
            <p>总耗时: {summary['duration']:.2f} 秒</p>
            <div class="summary-data">
                <div class="summary-item total">
                    <h3>总用例数</h3>
                    <p>{summary['total']}</p>
                </div>
                <div class="summary-item passed">
                    <h3>通过</h3>
                    <p>{summary['passed']}</p>
                </div>
                <div class="summary-item failed">
                    <h3>失败</h3>
                    <p>{summary['failed']}</p>
                </div>
                <div class="summary-item skipped">
                    <h3>跳过</h3>
                    <p>{summary['skipped']}</p>
                </div>
                <div class="summary-item total">
                    <h3>通过率</h3>
                    <p>{summary['pass_rate']}</p>
                </div>
            </div>
        </div>
        
        <h2>测试用例详情</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>状态</th>
                    <th>耗时 (秒)</th>
                    <th>详情</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # 生成测试用例行
        for i, result in enumerate(results):
            status_class = f"status-{result.get('status', 'unknown')}"
            error_message = ""
            if result.get('status') == 'failed' and result.get('error'):
                error_message = f"""
                <div class="error-message">
                    {result.get('error')}
                </div>
                """
            
            html += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{result.get('name', 'Unknown')}</td>
                    <td class="{status_class}">{result.get('status', 'unknown')}</td>
                    <td>{result.get('duration', 0):.2f}</td>
                    <td>
                        {result.get('description', '')}
                        {error_message}
                    </td>
                </tr>
            """
        
        # 完成HTML
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
        """
        
        return html
    
    @staticmethod
    def _apply_template(template: str, report_data: Dict[str, Any]) -> str:
        """
        应用模板生成HTML报告
        
        Args:
            template: HTML模板
            report_data: 报告数据
            
        Returns:
            HTML内容
        """
        # 简单替换变量
        template = template.replace('{{timestamp}}', report_data['summary']['timestamp'])
        template = template.replace('{{duration}}', str(report_data['summary']['duration']))
        template = template.replace('{{total}}', str(report_data['summary']['total']))
        template = template.replace('{{passed}}', str(report_data['summary']['passed']))
        template = template.replace('{{failed}}', str(report_data['summary']['failed']))
        template = template.replace('{{skipped}}', str(report_data['summary']['skipped']))
        template = template.replace('{{pass_rate}}', report_data['summary']['pass_rate'])
        
        # 处理测试用例列表
        results_placeholder = '{{test_results}}'
        if results_placeholder in template:
            results_html = ""
            for i, result in enumerate(report_data['results']):
                status_class = f"status-{result.get('status', 'unknown')}"
                error_message = ""
                if result.get('status') == 'failed' and result.get('error'):
                    error_message = f"""
                    <div class="error-message">
                        {result.get('error')}
                    </div>
                    """
                
                results_html += f"""
                    <tr>
                        <td>{i+1}</td>
                        <td>{result.get('name', 'Unknown')}</td>
                        <td class="{status_class}">{result.get('status', 'unknown')}</td>
                        <td>{result.get('duration', 0):.2f}</td>
                        <td>
                            {result.get('description', '')}
                            {error_message}
                        </td>
                    </tr>
                """
            
            template = template.replace(results_placeholder, results_html)
        
        return template
    
    @staticmethod
    def save_screenshot(driver, report_dir: str, name: str) -> str:
        """
        保存截图
        
        Args:
            driver: Selenium WebDriver对象
            report_dir: 报告目录
            name: 截图名称
            
        Returns:
            截图路径
        """
        try:
            screenshots_dir = os.path.join(report_dir, "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            driver.save_screenshot(filepath)
            logger.info(f"保存截图: {filepath}")
            
            return filepath
        except Exception as e:
            logger.error(f"保存截图失败: {e}")
            return "" 