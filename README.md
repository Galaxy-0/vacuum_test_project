# 扫地机器人自动化测试项目

## 项目概述
这是一个针对智能扫地机器人的全面自动化测试框架，提供了从API测试、UI测试到性能测试的完整解决方案。该项目不仅可以作为实际项目中的测试工具，也是学习自动化测试和智能家居测试的理想教程。

## 适用场景
- 扫地机器人功能自动化测试
- 智能家居设备测试经验积累
- 测试工程师面试准备
- Python自动化测试学习

## 技术栈
- Python 3.8+
- Pytest 测试框架
- Selenium/Appium UI自动化
- Requests HTTP客户端
- MQTT 通信协议
- Docker 容器化测试
- CI/CD 集成 (Jenkins/GitHub Actions)

## 项目结构
```
vacuum_test_project/
├── config/                 # 配置文件目录
│   ├── config.yaml         # 全局配置
│   └── env_config.yaml     # 环境配置
├── data/                   # 测试数据
│   ├── api_test_data.yaml  # API测试数据
│   └── device_profiles.yaml # 设备配置文件
├── libs/                   # 公共库
│   ├── api_client.py       # API请求客户端
│   ├── device_simulator.py # 设备模拟器
│   └── mqtt_client.py      # MQTT通信客户端
├── pages/                  # 页面对象
│   ├── app_login_page.py   # 登录页面
│   └── device_control_page.py # 设备控制页面
├── tests/                  # 测试用例
│   ├── api/                # API测试
│   ├── ui/                 # UI测试
│   └── integration/        # 集成测试
├── utils/                  # 工具类
│   ├── log_utils.py        # 日志工具
│   └── report_utils.py     # 报告工具
├── conftest.py             # Pytest配置
├── requirements.txt        # 依赖管理
└── README.md               # 项目说明
```

## 七天学习计划

### 第1天：测试基础与Python环境搭建
- **上午**：测试基础概念学习
  - 测试分类：单元测试、集成测试、系统测试、验收测试
  - 测试设计技术：等价类划分、边界值分析、因果图
- **下午**：环境搭建
  - Python安装与配置
  - 安装项目依赖：`pip install -r requirements.txt`
- **练习**：
  - 阅读`libs/device_simulator.py`代码
  - 运行第一个测试用例：`pytest tests/api/test_basic_functions.py::TestBasicFunctions::test_power_on -v`

### 第2天：Pytest框架入门
- **上午**：Pytest基础
  - 测试用例编写规范
  - 测试用例发现与执行
  - 断言机制
- **下午**：Pytest高级特性
  - Fixture机制（学习`conftest.py`中的示例）
  - 参数化测试（查看测试文件中的`@pytest.mark.parametrize`示例）
  - 测试报告生成：`pytest --html=report.html`
- **练习**：
  - 编写5个新的测试用例，使用不同的测试夹具和参数化测试

### 第3天：API测试实战
- **上午**：Requests库学习
  - 学习`libs/api_client.py`的封装方法
  - HTTP请求方法实践
  - 请求参数与响应处理
- **下午**：构建API测试框架
  - 运行并分析`tests/api/`目录下的测试用例
  - 学习数据驱动测试方法（使用`data/`下的YAML文件）
- **练习**：
  - 为扫地机的路径规划API开发3个新测试用例
  - 使用YAML文件进行测试数据管理

### 第4天：UI自动化测试
- **上午**：Selenium基础
  - 学习`pages/`目录下的页面对象模式实现
  - 元素定位技术与页面操作
- **下午**：应用UI测试
  - 运行`tests/ui/`目录下的UI测试用例
  - 分析Page Object模式的优势
- **练习**：
  - 开发一个新的页面对象类
  - 编写扫地机APP设置页面的UI测试用例

### 第5天：测试框架整合
- **上午**：深入测试架构
  - 学习`utils/`目录下的工具类使用
  - 研究日志系统和报告生成机制
- **下午**：混沌测试与异常处理
  - 学习如何模拟网络故障、设备异常等场景
  - 异常处理和测试稳定性提升
- **练习**：
  - 开发一个混沌测试模块，模拟3种异常场景
  - 在现有测试用例中加入异常处理机制

### 第6天：MQTT通信与物联网测试
- **上午**：MQTT协议学习
  - 研究`libs/mqtt_client.py`的实现
  - 理解发布/订阅模式
- **下午**：物联网测试实践
  - 运行`tests/integration/`下的MQTT测试用例
  - 分析设备通信测试要点
- **练习**：
  - 开发MQTT性能测试用例
  - 实现设备指令响应时间测试

### 第7天：CI/CD与测试报告
- **上午**：CI/CD集成
  - 学习Jenkins或GitHub Actions配置
  - 自动化测试执行与报告生成
- **下午**：项目综合实战
  - 运行完整测试套件
  - 分析测试报告并优化测试用例
- **练习**：
  - 搭建完整CI/CD流程
  - 准备项目演示与讲解

## 实战演练：扫地机测试场景

### 基础功能测试
- 设备开关机
- 清扫模式切换
- 定点清扫与区域清扫
- 返回充电与定时清扫

### 传感器测试
- 碰撞传感器响应
- 悬崖传感器触发
- 尘满传感器检测
- 激光雷达测距

### 导航与路径规划
- 地图构建准确性
- 障碍物绕行策略
- 区域划分与清扫路径
- 充电桩寻找与对接

### 性能与稳定性
- 电池续航测试
- 长时间运行稳定性
- 弱网环境适应性
- 边界场景处理能力

### APP交互测试
- 设备配网流程
- 远程控制响应
- 地图编辑与保存
- 清扫记录与统计

## 如何开始

1. 克隆项目:
```bash
git clone https://github.com/yourusername/vacuum_test_project.git
cd vacuum_test_project
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 运行基础测试:
```bash
pytest tests/api/test_basic_functions.py -v
```

4. 生成HTML测试报告:
```bash
pytest --html=report.html
```

## 进阶开发
- 添加更多设备模型支持
- 集成真实设备控制
- 开发视觉识别测试模块
- 拓展多设备协同测试
- 接入云平台API测试

## 贡献指南
欢迎提交Pull Request或Issue来完善此项目。贡献前请先阅读项目结构和代码规范。

## 许可证
MIT
