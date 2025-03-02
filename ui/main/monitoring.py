from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QGridLayout, QPushButton, QFrame, QScrollArea,  
                           QGroupBox, QLCDNumber, QProgressBar, QMessageBox,  
                           QLineEdit, QComboBox, QStackedWidget, QToolButton,  
                           QLayout,QGraphicsDropShadowEffect)  # 添加 QLayout  
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal, QDateTime, QSize,   
                         QPropertyAnimation, QEasingCurve, QRect, QPoint)  # 添加 QRect, QPoint  
from PyQt5.QtGui import QColor, QPalette, QIcon, QPainter, QPixmap 
import random  
import os

class StatusIndicator(QWidget):  
    """自定义状态指示器"""  
    def __init__(self, status="online", parent=None):  
        super().__init__(parent)  
        self.status = status  
        self.setFixedSize(12, 12)  
        
    def paintEvent(self, event):  
        painter = QPainter(self)  
        painter.setRenderHint(QPainter.Antialiasing)  
        
        if self.status == "online":  
            color = QColor("#2ecc71")  
        elif self.status == "offline":  
            color = QColor("#e74c3c")  
        else:  
            color = QColor("#f1c40f")  
            
        painter.setBrush(color)  
        painter.setPen(Qt.NoPen)  
        painter.drawEllipse(0, 0, 12, 12)  

class InfoBox(QFrame):  
    def __init__(self, title, parent=None):  
        super().__init__(parent)  
        self.setProperty("class", "info-box")  
        
        # 创建布局  
        self.layout = QVBoxLayout(self)  
        self.layout.setContentsMargins(10, 10, 10, 10)  
        self.layout.setSpacing(5)  
        
        # 标题  
        self.title_label = QLabel(title)  
        self.title_label.setProperty("class", "info-title")  
        
        # 值显示  
        self.value_layout = QHBoxLayout()  
        self.value_label = QLabel("0")  
        self.value_label.setProperty("class", "info-value")  
        self.unit_label = QLabel("")  
        self.unit_label.setProperty("class", "info-value")  
        self.unit_label.setStyleSheet("color: #6c757d;")  
        
        self.value_layout.addWidget(self.value_label)  
        self.value_layout.addWidget(self.unit_label)  
        self.value_layout.addStretch()  
        
        # 进度条（可选）  
        self.progress_bar = None  
        
        # 添加到主布局  
        self.layout.addWidget(self.title_label)  
        self.layout.addLayout(self.value_layout)  

    def update_value(self, value, unit=""):  
        """更新显示的值和单位"""  
        self.value_label.setText(str(value))  
        self.unit_label.setText(str(unit))  
        
        # 如果有进度条，同时更新进度条（确保使用整数值）  
        if self.progress_bar and value.replace(".", "").isdigit():  
            try:  
                # 将浮点数转换为整数  
                int_value = int(float(value))  
                self.progress_bar.setValue(int_value)  
            except (ValueError, TypeError):  
                pass  # 如果转换失败，忽略进度条更新  

    def add_progress_bar(self, progress_bar):  
        """添加进度条到信息框"""  
        self.progress_bar = progress_bar  
        self.layout.addWidget(progress_bar)  

    def set_warning(self, is_warning):  
        """设置警告状态"""  
        if is_warning:  
            self.setProperty("class", "info-box-warning")  
        else:  
            self.setProperty("class", "info-box")  
        self.style().unpolish(self)  
        self.style().polish(self)
class DeviceMonitorCard(QFrame):  
    battery_low = pyqtSignal(str, int)  # 设备ID, 电量  
    signal_lost = pyqtSignal(str)  # 设备ID  

    def __init__(self, device_info, parent=None):  
        super().__init__(parent)  
        self._validate_device_info(device_info)  
        self.device_info = device_info  
        self.update_timer = None  
        
        # 设置基础样式  
        self.setStyleSheet("""  
            DeviceMonitorCard {  
                background-color: #ffffff;  
                border-radius: 12px;  
                border: 1px solid #e9ecef;  
                padding: 15px;  
            }  
            DeviceMonitorCard:hover {  
                background-color: #f8f9fa;  
                border: 2px solid #007bff;  
            }  
        """)  
        
        self.setMouseTracking(True)  
        self.init_ui()  
        self.setup_update_timer()  

    def _validate_device_info(self, device_info):  
        """验证设备信息的完整性"""  
        required_fields = ['id', 'name', 'status']  
        if not isinstance(device_info, dict):  
            raise TypeError("设备信息必须是字典类型")  
        
        for field in required_fields:  
            if field not in device_info:  
                raise ValueError(f"设备信息缺少必要字段: {field}")  

    def init_ui(self):  
        layout = QVBoxLayout(self)  
        layout.setSpacing(10)  
        
        # 顶部信息  
        top_layout = QHBoxLayout()  
        
        # 设备名称和状态  
        name_status_layout = QVBoxLayout()  
        
        name_layout = QHBoxLayout()  
        device_name = QLabel(self.device_info['name'])  
        device_name.setProperty("class", "device-name")  
        name_layout.addWidget(device_name)  
        name_layout.addStretch()  
        
        status_layout = QHBoxLayout()  
        status_indicator = QLabel()  
        status_indicator.setFixedSize(8, 8)  
        status_indicator.setStyleSheet(  
            "background-color: #28a745; border-radius: 4px;"   
            if self.device_info['status'] == 'online'   
            else "background-color: #dc3545; border-radius: 4px;"  
        )  
        status_text = QLabel(  
            "在线" if self.device_info['status'] == 'online' else "离线"  
        )  
        status_text.setStyleSheet("color: #6c757d; font-size: 12px;")  
        status_layout.addWidget(status_indicator)  
        status_layout.addWidget(status_text)  
        status_layout.addStretch()  
        
        name_status_layout.addLayout(name_layout)  
        name_status_layout.addLayout(status_layout)  
        
        top_layout.addLayout(name_status_layout)  
        top_layout.addStretch()  
        
        # 信息展示区域  
        info_layout = QGridLayout()  
        info_layout.setSpacing(10)  
        
        # 电池信息  
        self.battery_box = InfoBox("电池电量")  
        self.battery_progress = QProgressBar()  
        self.battery_progress.setProperty("class", "battery")  
        self.battery_progress.setFixedHeight(4)  
        self.battery_progress.setTextVisible(False)  
        self.battery_box.add_progress_bar(self.battery_progress)  
        info_layout.addWidget(self.battery_box, 0, 0)  
        
        # 高度信息  
        self.altitude_box = InfoBox("当前高度")  
        info_layout.addWidget(self.altitude_box, 0, 1)  
        
        # 速度信息  
        self.speed_box = InfoBox("当前速度")  
        info_layout.addWidget(self.speed_box, 1, 0)  
        
        # 信号强度  
        self.signal_box = InfoBox("信号强度")  
        info_layout.addWidget(self.signal_box, 1, 1)  
        
        # 控制按钮  
        button_layout = QHBoxLayout()  
        button_layout.setSpacing(10)  
        
        self.control_btn = QPushButton("紧急着陆")  
        self.control_btn.setProperty("class", "danger")  
        self.control_btn.clicked.connect(self.emergency_landing)  
        
        self.return_btn = QPushButton("一键返航")  
        self.return_btn.setProperty("class", "primary")  
        self.return_btn.clicked.connect(self.return_home)  
        
        button_layout.addWidget(self.control_btn)  
        button_layout.addWidget(self.return_btn)  
        
        # 添加到主布局  
        layout.addLayout(top_layout)  
        layout.addLayout(info_layout)  
        layout.addLayout(button_layout)  
        
    def setup_update_timer(self):  
        self.update_timer = QTimer(self)  
        self.update_timer.timeout.connect(self.update_status)  
        self.update_timer.start(1000)  

    def update_status(self):  
        # 更新电池电量  
        battery = random.randint(20, 100)  
        self.battery_box.update_value(str(battery), "%")  
        self.battery_progress.setValue(battery)  
        
        if battery < 25:  
            self.battery_box.setProperty("class", "info-box-warning")  
            self.battery_low.emit(self.device_info['id'], battery)  
        else:  
            self.battery_box.setProperty("class", "info-box")  
            
        # 更新其他数据  
        altitude = random.randint(50, 200)  
        speed = random.randint(0, 40)  
        signal = random.randint(50, 100)  
        
        self.altitude_box.update_value(f"{altitude:.1f}", "m")  
        self.speed_box.update_value(f"{speed:.1f}", "m/s")  
        self.signal_box.update_value(str(signal), "%")  
        
        if signal < 60:  
            self.signal_box.setProperty("class", "info-box-warning")  
            self.signal_lost.emit(self.device_info['id'])  
        else:  
            self.signal_box.setProperty("class", "info-box")  

    def emergency_landing(self):  
        reply = QMessageBox.question(  
            self,   
            '确认操作',  
            '确定要执行紧急着陆吗？这将中断当前任务！',  
            QMessageBox.Yes | QMessageBox.No  
        )  
        
        if reply == QMessageBox.Yes:  
            self.control_btn.setEnabled(False)  
            self.return_btn.setEnabled(False)  
            
            def landing_complete():  
                self.control_btn.setEnabled(True)  
                self.return_btn.setEnabled(True)  
                self.altitude_box.update_value("0.0", "m")  
                self.speed_box.update_value("0.0", "m/s")  
                
            QTimer.singleShot(3000, landing_complete)  

    def return_home(self):  
        reply = QMessageBox.question(  
            self,   
            '确认操作',  
            '确定要执行一键返航吗？',  
            QMessageBox.Yes | QMessageBox.No  
        )  
        
        if reply == QMessageBox.Yes:  
            self.return_btn.setEnabled(False)  
            
            def return_complete():  
                self.return_btn.setEnabled(True)  
                self.altitude_box.update_value("0.0", "m")  
                self.speed_box.update_value("0.0", "m/s")  
                
            QTimer.singleShot(5000, return_complete)  

    def cleanup(self):  
        if self.update_timer:  
            self.update_timer.stop()  
            self.update_timer.deleteLater()  

    def closeEvent(self, event):  
        self.cleanup()  
        super().closeEvent(event)
class FlowLayout(QLayout):  
    """流式布局"""  
    def __init__(self, parent=None, margin=0, spacing=-1):  
        super().__init__(parent)  
        self.itemList = []  
        self.setContentsMargins(margin, margin, margin, margin)  
        self.setSpacing(spacing)  
        
    def __del__(self):  
        item = self.takeAt(0)  
        while item:  
            item = self.takeAt(0)  
            
    def addItem(self, item):  
        self.itemList.append(item)  
        
    def count(self):  
        return len(self.itemList)  
        
    def itemAt(self, index):  
        if 0 <= index < len(self.itemList):  
            return self.itemList[index]  
        return None  
        
    def takeAt(self, index):  
        if 0 <= index < len(self.itemList):  
            return self.itemList.pop(index)  
        return None  
        
    def expandingDirections(self):  
        return Qt.Orientations(Qt.Orientation(0))  
        
    def hasHeightForWidth(self):  
        return True  
        
    def heightForWidth(self, width):  
        height = self.doLayout(QRect(0, 0, width, 0), True)  
        return height  
        
    def setGeometry(self, rect):  
        super().setGeometry(rect)  
        self.doLayout(rect, False)  
        
    def sizeHint(self):  
        return self.minimumSize()  
        
    def minimumSize(self):  
        size = QSize()  
        for item in self.itemList:  
            size = size.expandedTo(item.minimumSize())  
        margin = self.contentsMargins()  
        size += QSize(2 * margin.left(), 2 * margin.top())  
        return size  
        
    def doLayout(self, rect, testOnly):  
        x = rect.x()  
        y = rect.y()  
        lineHeight = 0  
        
        for item in self.itemList:  
            wid = item.widget()  
            spaceX = self.spacing()  
            spaceY = self.spacing()  
            nextX = x + item.sizeHint().width() + spaceX  
            if nextX - spaceX > rect.right() and lineHeight > 0:  
                x = rect.x()  
                y = y + lineHeight + spaceY  
                nextX = x + item.sizeHint().width() + spaceX  
                lineHeight = 0  
                
            if not testOnly:  
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))  
                
            x = nextX  
            lineHeight = max(lineHeight, item.sizeHint().height())  
            
        return y + lineHeight - rect.y()
class MonitoringPage(QWidget):  
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.init_ui()  
        self.load_stylesheet()  
        
        # 添加时间更新定时器  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_time)  
        self.timer.start(1000)  
        
    def load_stylesheet(self):  
        try:  
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
            style_path = os.path.join(base_dir, 'resources', 'styles', 'monitoring.qss')  
            
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"加载样式表失败：{str(e)}")  
            
    def init_ui(self):  
        main_layout = QVBoxLayout(self)  
        main_layout.setSpacing(20)  
        main_layout.setContentsMargins(20, 20, 20, 20)  
        
        # 顶部区域  
        self.init_header(main_layout)  
        
        # 系统状态概览  
        self.init_status_overview(main_layout)  
        
        # 设备过滤和搜索区域  
        self.init_filter_section(main_layout)  
        
        # 设备监控区域  
        self.init_monitor_section(main_layout)  
        
        # 底部状态栏  
        self.init_footer(main_layout)  
        
        self.setMinimumSize(1200, 800)  
        
    def init_header(self, parent_layout):  
        header = QHBoxLayout()  
        
        # 左侧标题和时间  
        left_header = QVBoxLayout()  
        
        title_row = QHBoxLayout()  
        title_label = QLabel("无人机监控系统")  
        title_label.setProperty("class", "main-title")  
        title_row.addWidget(title_label)  
        title_row.addStretch()  
        
        time_row = QHBoxLayout()  
        self.time_label = QLabel()  
        self.time_label.setProperty("class", "time-display")  
        time_row.addWidget(self.time_label)  
        time_row.addStretch()  
        
        left_header.addLayout(title_row)  
        left_header.addLayout(time_row)  
        
        # 右侧快捷操作区  
        right_header = QHBoxLayout()  
        
        refresh_btn = QPushButton("刷新")  
        refresh_btn.setProperty("class", "tool-button")  
        refresh_btn.clicked.connect(self.refresh_devices)  
        
        settings_btn = QPushButton("设置")  
        settings_btn.setProperty("class", "tool-button")  
        
        right_header.addWidget(refresh_btn)  
        right_header.addWidget(settings_btn)  
        
        header.addLayout(left_header)  
        header.addStretch()  
        header.addLayout(right_header)  
        
        parent_layout.addLayout(header)  
        
    def init_status_overview(self, parent_layout):  
        status_frame = QFrame()  
        status_frame.setProperty("class", "status-overview")  
        status_layout = QHBoxLayout(status_frame)  
        
        # 设备统计  
        device_stats = QVBoxLayout()  
        self.total_devices = QLabel("总设备数")  
        self.total_devices.setProperty("class", "stats-title")  
        self.device_count = QLabel("0")  
        self.device_count.setProperty("class", "stats-value")  
        device_stats.addWidget(self.total_devices, alignment=Qt.AlignCenter)  
        device_stats.addWidget(self.device_count, alignment=Qt.AlignCenter)  
        
        # 在线设备  
        online_stats = QVBoxLayout()  
        self.online_devices = QLabel("在线设备")  
        self.online_devices.setProperty("class", "stats-title")  
        self.online_count = QLabel("0")  
        self.online_count.setProperty("class", "stats-value")  
        online_stats.addWidget(self.online_devices, alignment=Qt.AlignCenter)  
        online_stats.addWidget(self.online_count, alignment=Qt.AlignCenter)  
        
        # 活动任务  
        task_stats = QVBoxLayout()  
        self.active_tasks_label = QLabel("活动任务")  
        self.active_tasks_label.setProperty("class", "stats-title")  
        self.task_count = QLabel("0")  
        self.task_count.setProperty("class", "stats-value")  
        task_stats.addWidget(self.active_tasks_label, alignment=Qt.AlignCenter)  
        task_stats.addWidget(self.task_count, alignment=Qt.AlignCenter)  
        
        # 告警信息  
        warning_stats = QVBoxLayout()  
        self.warnings_label = QLabel("设备告警")  
        self.warnings_label.setProperty("class", "stats-title")  
        self.warning_count = QLabel("0")  
        self.warning_count.setProperty("class", "stats-value warning")  
        warning_stats.addWidget(self.warnings_label, alignment=Qt.AlignCenter)  
        warning_stats.addWidget(self.warning_count, alignment=Qt.AlignCenter)  
        
        status_layout.addLayout(device_stats)  
        status_layout.addLayout(online_stats)  
        status_layout.addLayout(task_stats)  
        status_layout.addLayout(warning_stats)  
        
        parent_layout.addWidget(status_frame)  
        
    def init_filter_section(self, parent_layout):  
        filter_frame = QFrame()  
        filter_frame.setProperty("class", "filter-section")  
        filter_layout = QHBoxLayout(filter_frame)  
        
        # 搜索框  
        self.search_input = QLineEdit()  
        self.search_input.setPlaceholderText("搜索设备...")  
        self.search_input.textChanged.connect(self.filter_devices)  
        
        # 状态过滤  
        self.status_filter = QComboBox()  
        self.status_filter.addItems(["全部状态", "在线", "离线"])  
        self.status_filter.currentTextChanged.connect(self.filter_devices)  
        
        # 排序方式  
        self.sort_by = QComboBox()  
        self.sort_by.addItems(["默认排序", "按状态排序", "按电量排序"])  
        self.sort_by.currentTextChanged.connect(self.sort_devices)  
        
        filter_layout.addWidget(QLabel("搜索:"))  
        filter_layout.addWidget(self.search_input)  
        filter_layout.addWidget(QLabel("状态:"))  
        filter_layout.addWidget(self.status_filter)  
        filter_layout.addWidget(QLabel("排序:"))  
        filter_layout.addWidget(self.sort_by)  
        filter_layout.addStretch()  
        
        parent_layout.addWidget(filter_frame)  
        
    def init_monitor_section(self, parent_layout):  
        monitor_frame = QFrame()  
        monitor_frame.setProperty("class", "monitor-section")  
        monitor_layout = QVBoxLayout(monitor_frame)  
        
        # 创建滚动区域  
        scroll = QScrollArea()  
        scroll.setWidgetResizable(True)  
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  
        
        # 使用流式布局来展示设备卡片  
        self.cards_container = QWidget()  
        self.cards_layout = FlowLayout(self.cards_container)  
        self.cards_layout.setSpacing(20)  
        scroll.setWidget(self.cards_container)  
        
        monitor_layout.addWidget(scroll)  
        parent_layout.addWidget(monitor_frame)  
        
        # 添加测试设备  
        self.add_test_devices()  
        
    def init_footer(self, parent_layout):  
        footer = QHBoxLayout()  
        
        system_status = QLabel("系统状态: 正常运行中")  
        system_status.setProperty("class", "footer-text")  
        
        version = QLabel("版本: v2.0.0")  
        version.setProperty("class", "footer-text")  
        
        footer.addWidget(system_status)  
        footer.addStretch()  
        footer.addWidget(version)  
        
        parent_layout.addLayout(footer)  
        
    def update_time(self):  
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")  
        self.time_label.setText(current_time)  
        
    def add_test_devices(self):  
        test_devices = [  
            {'id': '001', 'name': 'Drone-001', 'status': 'online'},  
            {'id': '002', 'name': 'Drone-002', 'status': 'online'},  
            {'id': '003', 'name': 'Drone-003', 'status': 'offline'},  
            {'id': '004', 'name': 'Drone-004', 'status': 'online'},  
            {'id': '005', 'name': 'Drone-005', 'status': 'online'},  
            {'id': '006', 'name': 'Drone-006', 'status': 'offline'},  
        ]  
        
        for device in test_devices:  
            try:  
                card = DeviceMonitorCard(device)  
                self.cards_layout.addWidget(card)  
            except (TypeError, ValueError) as e:  
                print(f"创建设备卡片失败: {str(e)}")  
                
        # 更新统计信息  
        self.device_count.setText(str(len(test_devices)))  
        online_count = sum(1 for device in test_devices if device['status'] == 'online')  
        self.online_count.setText(str(online_count))  
        self.task_count.setText(str(random.randint(0, online_count)))  
        self.warning_count.setText("0")  
        
    def refresh_devices(self):  
        """刷新设备状态"""  
        # 这里应该实现实际的设备状态刷新逻辑  
        pass  
        
    def filter_devices(self):  
        """根据搜索条件和状态过滤设备"""  
        search_text = self.search_input.text().lower()  
        status_filter = self.status_filter.currentText()  
        
        for i in range(self.cards_layout.count()):  
            card = self.cards_layout.itemAt(i).widget()  
            if card:  
                device_name = card.device_info['name'].lower()  
                device_status = card.device_info['status']  
                
                name_match = search_text in device_name  
                status_match = (status_filter == "全部状态" or  
                              (status_filter == "在线" and device_status == "online") or  
                              (status_filter == "离线" and device_status == "offline"))  
                
                card.setVisible(name_match and status_match)  
                
    def sort_devices(self):  
        """根据选择的方式对设备进行排序"""  
        # 实现设备排序逻辑  
        pass