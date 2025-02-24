from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QGridLayout, QPushButton, QFrame, QScrollArea,  
                           QGroupBox, QLCDNumber, QProgressBar)  
from PyQt5.QtCore import Qt, QTimer, pyqtSignal  
from PyQt5.QtGui import QColor, QPalette  
import random  
import os  

class DeviceMonitorCard(QFrame):  
    """单个设备监控卡片"""  
    
    # 定义信号  
    status_changed = pyqtSignal(str, str)  # (device_id, new_status)  
    battery_low = pyqtSignal(str, int)     # (device_id, battery_level)  
    signal_lost = pyqtSignal(str)          # (device_id)  
    
    def __init__(self, device_info, parent=None):  
        super().__init__(parent)  
        self._validate_device_info(device_info)  
        self.device_info = device_info  
        # 移除了setObjectName，因为新样式直接使用类名DeviceMonitorCard  
        self.init_ui()  
        self.setup_update_timer()  
        
    def _validate_device_info(self, device_info):  
        """验证设备信息的有效性"""  
        if not isinstance(device_info, dict):  
            raise TypeError("device_info must be a dictionary")  
            
        required_keys = ['id', 'name', 'status']  
        missing_keys = [key for key in required_keys if key not in device_info]  
        if missing_keys:  
            raise ValueError(f"Missing required keys in device_info: {missing_keys}")  
            
        valid_statuses = ['online', 'offline']  
        if device_info.get('status') not in valid_statuses:  
            raise ValueError(f"Invalid status value. Must be one of: {valid_statuses}")  
        
    def init_ui(self):  
        # 移除setFrameStyle，使用QSS控制边框  
        self.setMinimumSize(300, 250)  
        self.setMaximumSize(350, 300)  
        
        layout = QVBoxLayout(self)  
        
        # 设备标题  
        title_layout = QHBoxLayout()  
        title = QLabel(f"设备: {self.device_info['name']}")  
        title.setProperty("title", "true")  # 修改为字符串"true"以匹配QSS  
        status_label = QLabel("在线" if self.device_info['status'] == 'online' else "离线")  
        status_label.setProperty("status", self.device_info['status'])  
        title_layout.addWidget(title)  
        title_layout.addWidget(status_label)  
        layout.addLayout(title_layout)  
        
        # 设备信息  
        info_layout = QGridLayout()  
        
        # 电池电量  
        self.battery_label = QLabel("电池电量:")  
        self.battery_progress = QProgressBar()  
        self.battery_progress.setProperty("battery", "true")  # 修改为字符串"true"  
        self.battery_progress.setRange(0, 100)  
        info_layout.addWidget(self.battery_label, 0, 0)  
        info_layout.addWidget(self.battery_progress, 0, 1)  
        
        # 飞行高度  
        altitude_label = QLabel("当前高度:")  
        self.altitude_lcd = QLCDNumber()  
        self.altitude_lcd.setSegmentStyle(QLCDNumber.Flat)  
        self.altitude_lcd.setDigitCount(5)  
        info_layout.addWidget(altitude_label, 1, 0)  
        info_layout.addWidget(self.altitude_lcd, 1, 1)  
        
        # 飞行速度  
        speed_label = QLabel("当前速度:")  
        self.speed_lcd = QLCDNumber()  
        self.speed_lcd.setSegmentStyle(QLCDNumber.Flat)  
        self.speed_lcd.setDigitCount(5)  
        info_layout.addWidget(speed_label, 2, 0)  
        info_layout.addWidget(self.speed_lcd, 2, 1)  
        
        # GPS信号强度  
        gps_label = QLabel("GPS信号:")  
        self.gps_strength = QProgressBar()  
        self.gps_strength.setProperty("signal", "true")  # 修改为字符串"true"  
        self.gps_strength.setRange(0, 100)  
        info_layout.addWidget(gps_label, 3, 0)  
        info_layout.addWidget(self.gps_strength, 3, 1)  
        
        # 信号强度  
        signal_label = QLabel("信号强度:")  
        self.signal_strength = QProgressBar()  
        self.signal_strength.setProperty("signal", "true")  # 修改为字符串"true"  
        self.signal_strength.setRange(0, 100)  
        info_layout.addWidget(signal_label, 4, 0)  
        info_layout.addWidget(self.signal_strength, 4, 1)  
        
        layout.addLayout(info_layout)  
        
        # 任务状态  
        task_group = QGroupBox("当前任务")  
        task_layout = QVBoxLayout()  
        self.task_name = QLabel("任务名称: --")  
        self.task_progress = QProgressBar()  
        self.task_progress.setProperty("task", "true")  # 修改为字符串"true"  
        self.task_progress.setRange(0, 100)  
        task_layout.addWidget(self.task_name)  
        task_layout.addWidget(self.task_progress)  
        task_group.setLayout(task_layout)  
        layout.addWidget(task_group)  
        
        # 操作按钮  
        button_layout = QHBoxLayout()  
        self.control_btn = QPushButton("紧急着陆")  
        self.control_btn.setProperty("danger", "true")  # 修改为字符串"true"  
        self.control_btn.clicked.connect(self.emergency_landing)  
        
        self.return_btn = QPushButton("一键返航")  
        self.return_btn.setProperty("primary", "true")  # 修改为字符串"true"  
        self.return_btn.clicked.connect(self.return_home)  
        
        button_layout.addWidget(self.control_btn)  
        button_layout.addWidget(self.return_btn)  
        layout.addLayout(button_layout)  
        
    def setup_update_timer(self):  
        self.update_timer = QTimer(self)  
        self.update_timer.timeout.connect(self.update_status)  
        self.update_timer.start(1000)  
        
    def update_status(self):  
        # 更新电池电量  
        battery = random.randint(20, 100)  
        self.battery_progress.setValue(battery)  
        
        # 使用字符串"low"和"true"来匹配QSS  
        if battery < 25:  
            self.battery_progress.setProperty("battery", "low")  
        else:  
            self.battery_progress.setProperty("battery", "true")  
        
        self.battery_progress.style().unpolish(self.battery_progress)  
        self.battery_progress.style().polish(self.battery_progress)  
            
        self.altitude_lcd.display(f"{random.randint(50, 200):.1f}")  
        self.speed_lcd.display(f"{random.randint(0, 40):.1f}")  
        
        gps = random.randint(60, 100)  
        signal = random.randint(50, 100)  
        self.gps_strength.setValue(gps)  
        self.signal_strength.setValue(signal)  
        
        if hasattr(self, 'task_progress_value'):  
            self.task_progress_value = min(100, self.task_progress_value + random.randint(0, 5))  
        else:  
            self.task_progress_value = 0  
        self.task_progress.setValue(self.task_progress_value)  
        
    def emergency_landing(self):  
        pass  
        
    def return_home(self):  
        pass  
        
    def cleanup(self):  
        if self.update_timer:  
            self.update_timer.stop()  
            self.update_timer.deleteLater()  
    
    def closeEvent(self, event):  
        self.cleanup()  
        super().closeEvent(event)  

class MonitoringPage(QWidget):  
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.init_ui()  
        self.load_stylesheet()  
        
    def load_stylesheet(self):  
        try:  
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
            style_path = os.path.join(base_dir, 'resources', 'styles', 'monitoring.qss')  
            
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"加载样式表失败：{str(e)}")  
        
    def init_ui(self):  
        layout = QVBoxLayout(self)  
        
        # 顶部信息栏  
        info_bar = QHBoxLayout()  
        self.total_devices = QLabel("在线设备: 0")  
        self.total_devices.setProperty("info", "true")  # 修改为字符串"true"  
        self.active_tasks = QLabel("执行任务: 0")  
        self.active_tasks.setProperty("info", "true")  # 修改为字符串"true"  
        info_bar.addWidget(self.total_devices)  
        info_bar.addWidget(self.active_tasks)  
        info_bar.addStretch()  
        layout.addLayout(info_bar)  
        
        # 创建滚动区域  
        scroll = QScrollArea()  
        scroll.setWidgetResizable(True)  
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        
        # 创建设备监控卡片容器  
        self.cards_container = QWidget()  
        self.cards_container.setObjectName("cards_container")  
        self.cards_layout = QGridLayout(self.cards_container)  
        self.cards_layout.setSpacing(20)  
        scroll.setWidget(self.cards_container)  
        
        layout.addWidget(scroll)  
        
        self.add_test_devices()  
        
    def add_test_devices(self):  
        test_devices = [  
            {'id': '001', 'name': 'Drone-001', 'status': 'online'},  
            {'id': '002', 'name': 'Drone-002', 'status': 'online'},  
            {'id': '003', 'name': 'Drone-003', 'status': 'offline'},  
            {'id': '004', 'name': 'Drone-004', 'status': 'online'},  
        ]  
        
        for i, device in enumerate(test_devices):  
            row = i // 2  
            col = i % 2  
            try:  
                card = DeviceMonitorCard(device)  
                self.cards_layout.addWidget(card, row, col)  
            except (TypeError, ValueError) as e:  
                print(f"创建设备卡片失败: {str(e)}")  
            
        online_count = sum(1 for device in test_devices if device['status'] == 'online')  
        self.total_devices.setText(f"在线设备: {online_count}/{len(test_devices)}")  
        self.active_tasks.setText(f"执行任务: {random.randint(0, online_count)}")