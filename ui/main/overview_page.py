from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QFrame, QPushButton, QGridLayout)  
from PyQt5.QtCore import Qt, QTimer  
from PyQt5.QtGui import QFont, QColor  
import random  # 用于演示数据  

class StatisticCard(QFrame):  
    """统计数据卡片组件"""  
    def __init__(self, title, value, unit="", parent=None):  
        super().__init__(parent)  
        self.setObjectName("statisticCard")  
        self.setFrameStyle(QFrame.StyledPanel)  
        
        layout = QVBoxLayout(self)  
        
        # 标题  
        title_label = QLabel(title)  
        title_label.setObjectName("cardTitle")  
        
        # 数值  
        self.value_label = QLabel(str(value))  
        self.value_label.setObjectName("cardValue")  
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))  
        
        # 单位  
        if unit:  
            unit_label = QLabel(unit)  
            unit_label.setObjectName("cardUnit")  
        
        layout.addWidget(title_label)  
        layout.addWidget(self.value_label)  
        if unit:  
            layout.addWidget(unit_label)  
            
    def update_value(self, value):  
        self.value_label.setText(str(value))  

class OverviewPage(QWidget):  
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.init_ui()  
        self.setup_data_update()  
        
    def init_ui(self):  
        layout = QVBoxLayout(self)  
        
        # 顶部状态栏  
        status_bar = QHBoxLayout()  
        self.system_status = QLabel("系统状态: 正常运行")  
        self.system_status.setStyleSheet("color: #2ecc71; font-weight: bold;")  
        status_bar.addWidget(self.system_status)  
        
        # 实时时钟  
        self.clock_label = QLabel()  
        self.update_clock()  
        status_bar.addWidget(self.clock_label, alignment=Qt.AlignRight)  
        
        layout.addLayout(status_bar)  
        
        # 统计卡片网格  
        grid = QGridLayout()  
        
        # 创建统计卡片  
        self.device_card = StatisticCard("在线设备", "0", "台")  
        self.task_card = StatisticCard("当前任务", "0", "个")  
        self.flight_card = StatisticCard("总飞行时长", "0", "小时")  
        self.battery_card = StatisticCard("平均电量", "0", "%")  
        
        # 添加卡片到网格  
        grid.addWidget(self.device_card, 0, 0)  
        grid.addWidget(self.task_card, 0, 1)  
        grid.addWidget(self.flight_card, 1, 0)  
        grid.addWidget(self.battery_card, 1, 1)  
        
        layout.addLayout(grid)  
        
        # 快速操作按钮  
        quick_actions = QHBoxLayout()  
        
        add_device_btn = QPushButton("添加设备")  
        add_device_btn.clicked.connect(self.on_add_device_clicked)  
        
        create_task_btn = QPushButton("创建任务")  
        create_task_btn.clicked.connect(self.on_create_task_clicked)  
        
        view_report_btn = QPushButton("查看报告")  
        view_report_btn.clicked.connect(self.on_view_report_clicked)  
        
        quick_actions.addWidget(add_device_btn)  
        quick_actions.addWidget(create_task_btn)  
        quick_actions.addWidget(view_report_btn)  
        
        layout.addLayout(quick_actions)  
        
        # 添加一些留白  
        layout.addStretch()  
        
    def setup_data_update(self):  
        """设置数据更新定时器"""  
        # 更新时钟  
        self.clock_timer = QTimer(self)  
        self.clock_timer.timeout.connect(self.update_clock)  
        self.clock_timer.start(1000)  # 每秒更新  
        
        # 更新统计数据  
        self.data_timer = QTimer(self)  
        self.data_timer.timeout.connect(self.update_statistics)  
        self.data_timer.start(5000)  # 每5秒更新  
        
    def update_clock(self):  
        """更新时钟显示"""  
        from datetime import datetime  
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
        self.clock_label.setText(current_time)  
        
    def update_statistics(self):  
        """更新统计数据（示例使用随机数）"""  
        # 这里应该从实际的数据源获取数据  
        self.device_card.update_value(random.randint(3, 8))  
        self.task_card.update_value(random.randint(1, 5))  
        self.flight_card.update_value(random.randint(100, 200))  
        self.battery_card.update_value(random.randint(60, 100))  
        
    def on_add_device_clicked(self):  
        """添加设备按钮点击处理"""  
        # 这里应该打开添加设备对话框  
        print("打开添加设备对话框")  
        
    def on_create_task_clicked(self):  
        """创建任务按钮点击处理"""  
        # 这里应该打开创建任务对话框  
        print("打开创建任务对话框")  
        
    def on_view_report_clicked(self):  
        """查看报告按钮点击处理"""  
        # 这里应该打开报告查看界面  
        print("打开报告查看界面")