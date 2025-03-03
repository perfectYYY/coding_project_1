from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QGridLayout, QPushButton, QFrame, QScrollArea,  
                           QGroupBox, QLCDNumber, QProgressBar, QMessageBox,  
                           QLineEdit, QComboBox, QStackedWidget, QToolButton,  
                           QLayout,QGraphicsDropShadowEffect,QDialog,QDialogButtonBox,QFormLayout)  # 添加 QLayout  
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal, QDateTime, QSize,   
                         QPropertyAnimation, QEasingCurve, QRect, QPoint)  # 添加 QRect, QPoint  
from PyQt5.QtGui import QColor, QPalette, QIcon, QPainter, QPixmap 
from PyQt5.QtCore import QObject, pyqtSignal
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
    signal_lost = pyqtSignal(str)       # 设备ID
    status_changed = pyqtSignal(str, str)  # 设备ID, 新状态

    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self._validate_device_info(device_info)
        self.device_info = device_info
        self.device_id = device_info['id']
        self.physics_model = DevicePhysicsModel(self.device_id)
        self.last_values = {}
        self.update_timer = None
        self.physics_model.status_changed.connect(self._handle_status_change)
        
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
    def _handle_status_change(self, new_status):
        """处理物理模型的状态变化"""
        if new_status != self.device_info['status']:
            self.device_info['status'] = new_status
            self.status_changed.emit(self.device_id, new_status)
            
            # 更新本地显示
            self.status_indicator.status = new_status
            self.status_indicator.update()
            self._update_status_text(new_status)
            
    def _update_status_text(self, status):
        """更新状态文本"""
        for i in range(self.status_layout.count()):
            widget = self.status_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and ("在线" in widget.text() or "离线" in widget.text()):
                widget.setText("在线" if status == 'online' else "离线")
                widget.setStyleSheet(
                    "color: #28a745;" if status == 'online' else "color: #dc3545;"
                )

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
        
        self.status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator(self.device_info['status'])
        status_text = QLabel("在线" if self.device_info['status'] == 'online' else "离线")
        status_text.setStyleSheet("color: #6c757d; font-size: 12px;")
        self.status_layout.addWidget(self.status_indicator)
        self.status_layout.addWidget(status_text)
        self.status_layout.addStretch()
        
        name_status_layout.addLayout(name_layout)
        name_status_layout.addLayout(self.status_layout)
        top_layout.addLayout(name_status_layout)
        top_layout.addStretch()
        
        # 信息展示区域
        self.info_layout = QGridLayout()
        self.info_layout.setSpacing(10)
        
        # 电池信息
        self.battery_box = InfoBox("电池电量")
        self.battery_progress = QProgressBar()
        self.battery_progress.setProperty("class", "battery")
        self.battery_progress.setFixedHeight(4)
        self.battery_progress.setTextVisible(False)
        self.battery_box.add_progress_bar(self.battery_progress)
        self.info_layout.addWidget(self.battery_box, 0, 0)
        
        # 高度信息
        self.altitude_box = InfoBox("当前高度")
        self.info_layout.addWidget(self.altitude_box, 0, 1)
        
        # 速度信息
        self.speed_box = InfoBox("当前速度")
        self.info_layout.addWidget(self.speed_box, 1, 0)
        
        # 信号强度
        self.signal_box = InfoBox("信号强度")
        self.info_layout.addWidget(self.signal_box, 1, 1)
        
        # 新增电压电流显示
        self.voltage_box = InfoBox("电池电压")
        self.current_box = InfoBox("工作电流")
        self.info_layout.addWidget(self.voltage_box, 2, 0)
        self.info_layout.addWidget(self.current_box, 2, 1)
        
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
        layout.addLayout(self.info_layout)
        layout.addLayout(button_layout)

    def setup_update_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)

    def update_status(self):
        """基于物理模型更新状态"""
        self.physics_model.update_state()
        state = self.physics_model.get_current_state()
        
        # 更新数值显示（带趋势指示）
        self._update_display("altitude", state["altitude"], "m")
        self._update_display("speed", state["speed"], "m/s")
        self._update_display("battery", state["battery"], "%")
        self._update_display("signal", state["signal"], "%")
        self._update_display("voltage", state["voltage"], "V")
        self._update_display("current", state["current"], "A")

        # 更新设备状态
        new_status = "online" if state["signal"] > 5 else "offline"
        if new_status != self.device_info['status']:
            self.status_changed.emit(self.device_id, new_status)
            self.device_info['status'] = new_status
            self.status_indicator.status = new_status
            self.status_indicator.update()

        # 触发预警检测
        self._check_warnings(state)

    def _update_display(self, key, value, unit):
        """带趋势指示的数值更新"""
        trend = ""
        diff = 0
        if key in self.last_values:
            diff = value - self.last_values[key]
            if abs(diff) > 0.01:  # 过滤微小变化
                trend = "↑" if diff > 0 else "↓"
        
        # 带颜色和趋势符号的显示
        display_text = f"""
        <span style='font-size:18pt;'>{value}</span>
        <span style='color:#6c757d;font-size:10pt;'> {unit} </span>
        <span style='color:{self._get_trend_color(diff)};font-size:12pt;'>{trend}</span>
        """
        
        # 更新对应组件
        target_box = getattr(self, f"{key}_box")
        target_box.value_label.setText(display_text)
        
        # 特殊处理进度条
        if key == "battery":
            self.battery_progress.setValue(int(value))
        
        self.last_values[key] = value

    def _get_trend_color(self, diff):
        """获取趋势箭头颜色"""
        if diff > 0:
            return "#28a745" if diff < 5 else "#dc3545"  # 正常上升/过快上升
        elif diff < 0:
            return "#6c757d" if abs(diff) < 5 else "#ffc107"  # 正常下降/快速下降
        return "transparent"

    def _check_warnings(self, state):
        """综合预警检测"""
        # 电池预警（多级判断）
        if state["battery"] < 10:
            self._trigger_warning("battery", "critical", state["battery"])
        elif state["battery"] < 20:
            self._trigger_warning("battery", "warning", state["battery"])
        
        # 信号强度预警
        if state["signal"] < 30:
            self._trigger_warning("signal", "critical", state["signal"])
        elif state["signal"] < 50:
            self._trigger_warning("signal", "warning", state["signal"])

    def _trigger_warning(self, category, level, value):
        """触发分级预警"""
        target_box = getattr(self, f"{category}_box")
        target_box.set_warning(level)
        
        if level == "critical":
            if category == "battery":
                self.battery_low.emit(self.device_id, value)
            elif category == "signal":
                self.signal_lost.emit(self.device_id)

    # 保留原有控制方法
    def emergency_landing(self):
        reply = QMessageBox.question(
            self, 
            '确认操作',
            '确定要执行紧急着陆吗？这将中断当前任务！',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.physics_model.set_flight_mode("descending")
            self.control_btn.setEnabled(False)
            self.return_btn.setEnabled(False)

    def return_home(self):
        reply = QMessageBox.question(
            self,
            '确认操作',
            '确定要执行一键返航吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.physics_model.set_flight_mode("moving")
            self.return_btn.setEnabled(False)

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

    device_status_changed = pyqtSignal(str, str)  # 设备ID, 新状态
    def __init__(self, parent=None):  
        super().__init__(parent)
        self.device_manager = None
        self.device_cards = {} 
        self.init_ui()  
        self.load_stylesheet()
        self.device_manager = DeviceManager()  # 获取单例实例
        self._load_devices()
        # 添加时间更新定时器  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_time)  
        self.timer.start(1000)

    def remove_selected_device(self):
        """删除选中设备的完整实现"""
        selected_serial = self.get_selected_device()
        
        if not selected_serial:
            QMessageBox.warning(self, "警告", "请先选择要删除的设备")
            return
            
        try:
            # 确认对话框
            confirm = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除设备 {selected_serial} 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # 从设备管理器移除
                if self.device_manager.remove_device(selected_serial):
                    # 从界面移除卡片
                    self.remove_device_card(selected_serial)
                    QMessageBox.information(
                        self, 
                        "删除成功", 
                        f"设备 {selected_serial} 已成功删除"
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "删除失败",
                f"删除设备时发生错误: {str(e)}",
                QMessageBox.Ok
            )

    def get_selected_device(self):
        """获取当前选中设备的序列号"""
        # 实现设备选择逻辑（可通过卡片点击状态判断）
        # 此处为示例实现，实际需根据选择机制调整
        for serial, card in self.device_cards.items():
            if card.property("selected"):
                return serial
        return None

    # 在设备卡片点击事件中增加选中状态切换
    def setup_card_interaction(self):
        """设置卡片交互逻辑"""
        for card in self.device_cards.values():
            # 使用闭包绑定当前卡片对象
            def make_handler(c):
                def handler(event):
                    self.toggle_card_selection(c)
                return handler
            card.mousePressEvent = make_handler(card)
            
    def toggle_card_selection(self, card):
        """切换卡片选中状态"""
        # 清除所有卡片的选中状态
        for c in self.device_cards.values():
            c.setProperty("selected", False)
            c.style().unpolish(c)
            c.style().polish(c)
        
        # 设置当前选中状态
        card.setProperty("selected", True)
        card.style().unpolish(card)
        card.style().polish(card)

    def _load_devices(self):
        """加载设备数据（替代原load_initial_devices）"""
        if self.device_manager and hasattr(self.device_manager, 'devices'):
            for serial, device in self.device_manager.devices.items():
                self.add_device_card(device)
            self._update_stats()
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
        self._add_management_buttons(filter_layout)
        
        parent_layout.addWidget(filter_frame) 
    
    def _add_management_buttons(self, layout):
        """添加设备管理按钮组（简化版）"""
        btn_container = QFrame()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)
        
        # 添加设备按钮
        self.add_btn = QToolButton()
        self.add_btn.setText("添加设备")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.add_btn.setProperty("class", "tool-button success")
        self.add_btn.clicked.connect(self.show_add_device_dialog)
        
        # 删除设备按钮
        self.del_btn = QToolButton()
        self.del_btn.setText("删除设备")
        self.del_btn.setIcon(QIcon.fromTheme("list-add"))
        self.del_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.del_btn.setProperty("class", "tool-button danger")
        self.del_btn.clicked.connect(self.remove_selected_device)
        
        # 移除了更多操作菜单
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        
        layout.addStretch()
        layout.addWidget(btn_container)
        
    def show_add_device_dialog(self):
        """显示添加设备对话框（简化版）"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加新设备")
        dialog.setFixedSize(300, 200)
    
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
    
        self.serial_input = QLineEdit()
        self.name_input = QLineEdit()
    
        form.addRow("序列号:", self.serial_input)
        form.addRow("设备名称:", self.name_input)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(lambda: self._add_device(dialog))
        btn_box.rejected.connect(dialog.reject)
    
        layout.addLayout(form)
        layout.addWidget(btn_box)
        dialog.exec_()

    def _add_device(self, dialog):
        """执行添加设备操作"""
        if not self.device_manager:
            QMessageBox.critical(self, "错误", "设备管理器未初始化")
            return
    
        device_info = {
            "serial": self.serial_input.text(),
            "name": self.name_input.text(),
            "status": "online",
            "type": "四旋翼",
            "id": self.serial_input.text()
        }
    
        try:
            if self.device_manager.add_device(device_info):
                self.add_device_card(device_info)
                dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加失败: {str(e)}")
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
        
    def add_device_card(self, device_data):
        """添加新的设备卡片"""
        try:
            if device_data['serial'] not in self.device_cards:
                card = DeviceMonitorCard(device_data)
                self.cards_layout.addWidget(card)
                self.device_cards[device_data['serial']] = card
                self._update_stats()
        except (TypeError, ValueError) as e:
            print(f"创建设备卡片失败: {str(e)}")

    def remove_device_card(self, serial):
        """移除设备卡片"""
        if serial in self.device_cards:
            card = self.device_cards.pop(serial)
            card.cleanup()
            card.deleteLater()
            self._update_stats()

    def update_device_card(self, device_data):
        """更新现有设备卡片"""
        serial = device_data['serial']
        if serial in self.device_cards:
            card = self.device_cards[serial]
            # 更新基础信息
            card.device_info = device_data
            # 更新状态显示
            card.status_indicator.status = device_data['status']
            card.status_indicator.update()
            # 更新状态文本
            for i in range(card.status_layout.count()):
                widget = card.status_layout.itemAt(i).widget()
                if isinstance(widget, QLabel) and "在线" in widget.text():
                    widget.setText("在线" if device_data['status'] == 'online' else "离线")

    def _update_stats(self):
        """更新统计信息"""
        total = len(self.device_cards)
        online = sum(1 for card in self.device_cards.values() 
                    if card.device_info['status'] == 'online')
        self.device_count.setText(str(total))
        self.online_count.setText(str(online))
        self.task_count.setText(str(random.randint(0, online)))
    def refresh_devices(self):
        """刷新监控设备显示"""
        # 1. 清理旧卡片
        for serial in list(self.device_cards.keys()):
            self.remove_device_card(serial)
        
        # 2. 重新加载设备（这里需要获取设备数据源）
        # 假设通过主窗口获取设备管理器实例
        if hasattr(self.parent(), 'device_manager'):
            devices = self.parent().device_manager.devices
            for serial, device in devices.items():
                self.add_device_card(device)
        
        # 3. 更新统计信息
        self._update_stats()
        
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

def init_enhanced_controls(self):
    control_bar = QHBoxLayout()
    
    # 飞行模式选择
    self.mode_selector = QComboBox()
    self.mode_selector.addItems(["悬停", "上升", "下降", "移动"])
    self.mode_selector.currentTextChanged.connect(self.change_flight_mode)
    
    # 全局控制按钮
    self.emergency_stop = QPushButton("全机紧急停止")
    self.emergency_stop.setProperty("class", "super-danger")
    self.emergency_stop.clicked.connect(self.stop_all_drones)
    
    control_bar.addWidget(QLabel("飞行模式:"))
    control_bar.addWidget(self.mode_selector)
    control_bar.addStretch()
    control_bar.addWidget(self.emergency_stop)
    
    self.main_layout.insertLayout(2, control_bar)

def change_flight_mode(self, mode_text):
    mode_mapping = {
        "悬停": "hover",
        "上升": "ascending",
        "下降": "descending",
        "移动": "moving"
    }
    selected_mode = mode_mapping.get(mode_text, "hover")
    
    for i in range(self.cards_layout.count()):
        card = self.cards_layout.itemAt(i).widget()
        if card and card.isVisible():
            card.physics_model.set_flight_mode(selected_mode)

class DevicePhysicsModel(QObject):
    """设备物理状态模拟模型"""
    status_changed = pyqtSignal(str)
    def __init__(self, device_id):

        super().__init__()
        self.device_id = device_id
        self._current_status = "offline"
        self._flight_mode = "hover"  # [hover, ascending, descending, moving]
        self._base_params = {
            "max_altitude": 500.0,    # 最大飞行高度（米）
            "max_speed": 30.0,        # 最大速度（m/s）
            "battery_capacity": 5200, # 电池容量（mAh）
            "power_consumption": {    # 功耗模式（mA/s）
                "hover": 120,
                "moving": 300,
                "ascending": 450,
                "descending": 80
            }
        }
        self._current_state = {
            "altitude": 0.0,      # 当前高度
            "speed": 0.0,         # 当前速度
            "battery": 100,       # 剩余电量百分比
            "signal": 100,       # 信号强度百分比
            "voltage": 11.1,     # 电池电压（V）
            "current": 0.0       # 电流（A）
        }
        self._physics_params = {
            "ascend_rate": 2.5,   # 上升速率（m/s²）
            "descend_rate": 1.8,  # 下降速率（m/s²）
            "acceleration": 0.8,  # 水平加速度（m/s²）
            "deceleration": 1.2   # 减速度（m/s²）
        }
        self._last_update = QDateTime.currentDateTime()
        
    def update_state(self):
        """根据物理模型更新状态"""
        time_diff = self._last_update.msecsTo(QDateTime.currentDateTime()) / 1000.0
        self._last_update = QDateTime.currentDateTime()

        # 根据飞行模式更新高度
        if self._flight_mode == "ascending":
            self._current_state["altitude"] = min(
                self._current_state["altitude"] + 
                self._physics_params["ascend_rate"] * time_diff,
                self._base_params["max_altitude"]
            )
        elif self._flight_mode == "descending":
            self._current_state["altitude"] = max(
                self._current_state["altitude"] - 
                self._physics_params["descend_rate"] * time_diff,
                0.0
            )

        # 更新速度（模拟加速/减速过程）
        target_speed = self._base_params["max_speed"] if self._flight_mode == "moving" else 0.0
        if self._current_state["speed"] < target_speed:
            self._current_state["speed"] = min(
                self._current_state["speed"] + 
                self._physics_params["acceleration"] * time_diff,
                target_speed
            )
        else:
            self._current_state["speed"] = max(
                self._current_state["speed"] - 
                self._physics_params["deceleration"] * time_diff,
                target_speed
            )

        # 计算电池消耗（基于实时电流）
        current_power = self._base_params["power_consumption"][self._flight_mode]
        consumed = (current_power * time_diff) / self._base_params["battery_capacity"]
        self._current_state["battery"] = max(
            self._current_state["battery"] - consumed * 100,
            0.0
        )

        # 模拟电压变化（根据负载）
        self._current_state["voltage"] = 11.1 - (0.015 * (100 - self._current_state["battery"]))

        # 模拟信号强度（带随机扰动）
        base_signal = 100 - (self._current_state["altitude"] / 15)
        self._current_state["signal"] = max(
            base_signal + random.uniform(-3, 3),
            0.0
        )
        new_status = "online" if random.random() > 0.5 else "offline"
        
        if new_status != self._current_status:
            self._current_status = new_status
            self.status_changed.emit(new_status)  # 发射信号

    def set_flight_mode(self, mode):
        """设置飞行模式"""
        valid_modes = ["hover", "ascending", "descending", "moving"]
        if mode in valid_modes:
            self._flight_mode = mode

    def get_current_state(self):
        """获取当前状态快照"""
        return {
            "altitude": round(self._current_state["altitude"], 1),
            "speed": round(self._current_state["speed"], 1),
            "battery": round(self._current_state["battery"], 1),
            "signal": int(self._current_state["signal"]),
            "voltage": round(self._current_state["voltage"], 2),
            "current": round(
                self._base_params["power_consumption"][self._flight_mode] / 1000, 
                1
            )
        }
    
class DeviceManager(QWidget):
    """设备管理类（单例模式）"""
    _instance = None
    device_added = pyqtSignal(dict)         # 设备添加信号
    device_removed = pyqtSignal(str)        # 设备移除信号（serial）
    device_updated = pyqtSignal(dict)       # 设备更新信号
    status_changed = pyqtSignal(str, str)   # 设备状态变化信号（serial, new_status）

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent=None):
        if self._initialized:
            return
        super().__init__(parent)
        self._devices = {}  # {serial: device_info}
        self._physics_models = {}  # {serial: DevicePhysicsModel}
        self._initialized = True

    @property
    def devices(self):
        """获取所有设备信息（只读）"""
        return self._devices.copy()

    def add_device(self, device_info):
        """添加新设备"""
        self._validate_device_info(device_info)
        serial = device_info['serial']

        if serial in self._devices:
            raise ValueError(f"设备 {serial} 已存在")

        # 初始化物理模型
        self._physics_models[serial] = DevicePhysicsModel(serial)
        self._physics_models[serial].status_changed.connect(
            lambda status, s=serial: self._handle_physics_status_change(s, status)
        )

        # 存储设备信息
        self._devices[serial] = device_info
        self.device_added.emit(device_info)
        return True

    def remove_device(self, serial):
        """移除设备"""
        if serial not in self._devices:
            raise KeyError(f"设备 {serial} 不存在")

        # 清理物理模型
        if serial in self._physics_models:
            del self._physics_models[serial]

        del self._devices[serial]
        self.device_removed.emit(serial)
        return True

    def update_device(self, serial, new_info):
        """更新设备信息"""
        if serial not in self._devices:
            raise KeyError(f"设备 {serial} 不存在")

        old_info = self._devices[serial]
        merged_info = {**old_info, **new_info}
        self._validate_device_info(merged_info)

        self._devices[serial] = merged_info
        self.device_updated.emit(merged_info)
        new_status = "online" if self._current_state["signal"] > 5 else "offline"
        if new_status != self._current_status:
            self._current_status = new_status
            self.status_changed.emit(new_status)
        return True

    def get_device(self, serial):
        """获取指定设备信息"""
        return self._devices.get(serial, None)

    def get_physics_model(self, serial):
        """获取设备的物理模型"""
        return self._physics_models.get(serial, None)

    def _validate_device_info(self, device_info):
        """验证设备信息有效性"""
        required_fields = ['serial', 'name', 'type', 'status']
        if not isinstance(device_info, dict):
            raise TypeError("设备信息必须是字典类型")
        for field in required_fields:
            if field not in device_info:
                raise ValueError(f"设备信息缺少必要字段: {field}")

    def _handle_physics_status_change(self, serial, new_status):
        """处理物理模型的状态变化"""
        if serial in self._devices:
            old_status = self._devices[serial]['status']
            if new_status != old_status:
                self._devices[serial]['status'] = new_status
                self.status_changed.emit(serial, new_status)
                self.device_updated.emit(self._devices[serial])

    def cleanup(self):
        """清理所有资源"""
        self._devices.clear()
        for model in self._physics_models.values():
            model.deleteLater()
        self._physics_models.clear()