from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QPushButton, QTableWidget, QTableWidgetItem,  
                           QDialog, QLineEdit, QFormLayout, QMessageBox,  
                           QComboBox, QSpinBox, QDateTimeEdit, QTextEdit,  
                           QHeaderView, QCheckBox)  
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime  
from PyQt5.QtGui import QColor  
import json  
import os  
from datetime import datetime  

class TaskDialog(QDialog):  
    """任务创建/编辑对话框"""  
    def __init__(self, parent=None, task_data=None, available_devices=None):  
        super().__init__(parent)  
        self.task_data = task_data  
        self.available_devices = available_devices or []  
        self.init_ui()  
        
    def init_ui(self):  
        self.setWindowTitle("创建任务" if not self.task_data else "编辑任务")  
        self.setFixedSize(500, 600)  
        
        layout = QFormLayout(self)  
        
        # 任务名称  
        self.name_input = QLineEdit()  
        if self.task_data:  
            self.name_input.setText(self.task_data.get('name', ''))  
        layout.addRow("任务名称:", self.name_input)  
        
        # 选择设备  
        self.device_select = QComboBox()  
        self.device_select.addItems([device['name'] for device in self.available_devices])  
        if self.task_data:  
            index = self.device_select.findText(self.task_data.get('device', ''))  
            if index >= 0:  
                self.device_select.setCurrentIndex(index)  
        layout.addRow("执行设备:", self.device_select)  
        
        # 任务类型  
        self.type_select = QComboBox()  
        self.type_select.addItems(["巡检任务", "测绘任务", "监控任务", "喷洒任务"])  
        if self.task_data:  
            self.type_select.setCurrentText(self.task_data.get('type', ''))  
        layout.addRow("任务类型:", self.type_select)  
        
        # 计划开始时间  
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime())  
        self.start_time.setCalendarPopup(True)  
        if self.task_data:  
            self.start_time.setDateTime(QDateTime.fromString(self.task_data.get('start_time', ''),   
                                                           "yyyy-MM-dd hh:mm:ss"))  
        layout.addRow("开始时间:", self.start_time)  
        
        # 预计持续时间（分钟）  
        self.duration = QSpinBox()  
        self.duration.setRange(1, 180)  
        self.duration.setValue(30)  
        if self.task_data:  
            self.duration.setValue(int(self.task_data.get('duration', 30)))  
        layout.addRow("持续时间(分钟):", self.duration)  
        
        # 飞行高度  
        self.altitude = QSpinBox()  
        self.altitude.setRange(0, 500)  
        self.altitude.setValue(100)  
        self.altitude.setSuffix(" m")  
        if self.task_data:  
            self.altitude.setValue(int(self.task_data.get('altitude', 100)))  
        layout.addRow("飞行高度:", self.altitude)  
        
        # 任务描述  
        self.description = QTextEdit()  
        self.description.setMaximumHeight(100)  
        if self.task_data:  
            self.description.setText(self.task_data.get('description', ''))  
        layout.addRow("任务描述:", self.description)  
        
        # 任务优先级  
        self.priority = QComboBox()  
        self.priority.addItems(["低", "中", "高"])  
        if self.task_data:  
            self.priority.setCurrentText(self.task_data.get('priority', '中'))  
        layout.addRow("优先级:", self.priority)  
        
        # 自动执行  
        self.auto_execute = QCheckBox("启用")  
        if self.task_data:  
            self.auto_execute.setChecked(self.task_data.get('auto_execute', False))  
        layout.addRow("自动执行:", self.auto_execute)  
        
        # 按钮  
        button_layout = QHBoxLayout()  
        confirm_btn = QPushButton("确认")  
        confirm_btn.clicked.connect(self.accept)  
        cancel_btn = QPushButton("取消")  
        cancel_btn.clicked.connect(self.reject)  
        
        button_layout.addWidget(confirm_btn)  
        button_layout.addWidget(cancel_btn)  
        layout.addRow("", button_layout)  
        
    def get_task_data(self):  
        """获取任务数据"""  
        return {  
            'id': self.task_data.get('id', '') if self.task_data else datetime.now().strftime('%Y%m%d%H%M%S'),  
            'name': self.name_input.text(),  
            'device': self.device_select.currentText(),  
            'type': self.type_select.currentText(),  
            'start_time': self.start_time.dateTime().toString("yyyy-MM-dd hh:mm:ss"),  
            'duration': self.duration.value(),  
            'altitude': self.altitude.value(),  
            'description': self.description.toPlainText(),  
            'priority': self.priority.currentText(),  
            'auto_execute': self.auto_execute.isChecked(),  
            'status': self.task_data.get('status', '待执行') if self.task_data else '待执行'  
        }  

class TaskPlanningPage(QWidget):  
    # 定义信号  
    task_added = pyqtSignal(dict)  
    task_removed = pyqtSignal(str)  
    task_updated = pyqtSignal(dict)  
    task_executed = pyqtSignal(dict)  
    
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.tasks = {}  # 存储任务信息  
        self.load_tasks()  # 加载已保存的任务  
        self.init_ui()  
        self.setup_connections()  
        
    def init_ui(self):  
        layout = QVBoxLayout(self)  
        
        # 顶部操作栏  
        top_bar = QHBoxLayout()  
        
        # 创建任务按钮  
        add_btn = QPushButton("创建任务")  
        add_btn.clicked.connect(self.show_add_task_dialog)  
        top_bar.addWidget(add_btn)  
        
        # 任务类型过滤  
        self.type_filter = QComboBox()  
        self.type_filter.addItems(["全部类型", "巡检任务", "测绘任务", "监控任务", "喷洒任务"])  
        self.type_filter.currentTextChanged.connect(self.filter_tasks)  
        top_bar.addWidget(QLabel("任务类型:"))  
        top_bar.addWidget(self.type_filter)  
        
        # 状态过滤  
        self.status_filter = QComboBox()  
        self.status_filter.addItems(["全部状态", "待执行", "执行中", "已完成", "已取消"])  
        self.status_filter.currentTextChanged.connect(self.filter_tasks)  
        top_bar.addWidget(QLabel("状态:"))  
        top_bar.addWidget(self.status_filter)  
        
        top_bar.addStretch()  
        
        # 搜索框  
        self.search_input = QLineEdit()  
        self.search_input.setPlaceholderText("搜索任务...")  
        self.search_input.textChanged.connect(self.filter_tasks)  
        top_bar.addWidget(self.search_input)  
        
        layout.addLayout(top_bar)  
        
        # 任务列表表格  
        self.task_table = QTableWidget()  
        self.task_table.setColumnCount(9)  
        self.task_table.setHorizontalHeaderLabels([  
            "任务名称", "执行设备", "类型", "开始时间",   
            "持续时间", "优先级", "状态", "自动执行", "操作"  
        ])  
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        layout.addWidget(self.task_table)  
        
        # 初始化任务表格  
        self.refresh_tasks()  
        
    def setup_connections(self):  
        """设置信号连接"""  
        self.task_added.connect(self.on_task_added)  
        self.task_removed.connect(self.on_task_removed)  
        self.task_updated.connect(self.on_task_updated)  
        self.task_executed.connect(self.on_task_executed)  
        
    def show_add_task_dialog(self):  
        """显示添加任务对话框"""  
        # 这里应该从设备管理模块获取可用设备列表  
        available_devices = [  
            {'name': 'Device 1'},  
            {'name': 'Device 2'},  
            {'name': 'Device 3'}  
        ]  
        dialog = TaskDialog(self, available_devices=available_devices)  
        if dialog.exec_() == QDialog.Accepted:  
            task_data = dialog.get_task_data()  
            self.add_task(task_data)  
            
    def add_task(self, task_data):  
        """添加新任务"""  
        self.tasks[task_data['id']] = task_data  
        self.task_added.emit(task_data)  
        self.save_tasks()  
        self.refresh_tasks()  
        
    def remove_task(self, task_id):  
        """删除任务"""  
        if task_id in self.tasks:  
            del self.tasks[task_id]  
            self.task_removed.emit(task_id)  
            self.save_tasks()  
            self.refresh_tasks()  
            
    def edit_task(self, task_id):  
        """编辑任务"""  
        if task_id in self.tasks:  
            available_devices = [  
                {'name': 'Device 1'},  
                {'name': 'Device 2'},  
                {'name': 'Device 3'}  
            ]  
            dialog = TaskDialog(self, self.tasks[task_id], available_devices)  
            if dialog.exec_() == QDialog.Accepted:  
                task_data = dialog.get_task_data()  
                self.tasks[task_id] = task_data  
                self.task_updated.emit(task_data)  
                self.save_tasks()  
                self.refresh_tasks()  
                
    def execute_task(self, task_id):  
        """执行任务"""  
        if task_id in self.tasks:  
            task = self.tasks[task_id]  
            task['status'] = '执行中'  
            self.task_executed.emit(task)  
            self.save_tasks()  
            self.refresh_tasks()  
            
    def cancel_task(self, task_id):  
        """取消任务"""  
        if task_id in self.tasks:  
            task = self.tasks[task_id]  
            task['status'] = '已取消'  
            self.save_tasks()  
            self.refresh_tasks()  
            
    def refresh_tasks(self):  
        """刷新任务列表"""  
        self.task_table.setRowCount(0)  
        for task_id, task in self.tasks.items():  
            self.add_task_to_table(task)  
            
    def add_task_to_table(self, task):  
        """将任务添加到表格中"""  
        row = self.task_table.rowCount()  
        self.task_table.insertRow(row)  
        
        # 添加任务信息  
        self.task_table.setItem(row, 0, QTableWidgetItem(task['name']))  
        self.task_table.setItem(row, 1, QTableWidgetItem(task['device']))  
        self.task_table.setItem(row, 2, QTableWidgetItem(task['type']))  
        self.task_table.setItem(row, 3, QTableWidgetItem(task['start_time']))  
        self.task_table.setItem(row, 4, QTableWidgetItem(f"{task['duration']}分钟"))  
        self.task_table.setItem(row, 5, QTableWidgetItem(task['priority']))  
        
        # 状态显示  
        status_item = QTableWidgetItem(task['status'])  
        status_color = {  
            '待执行': QColor("#f39c12"),  
            '执行中': QColor("#3498db"),  
            '已完成': QColor("#27ae60"),  
            '已取消': QColor("#e74c3c")  
        }  
        status_item.setForeground(status_color.get(task['status'], QColor("#000000")))  
        self.task_table.setItem(row, 6, status_item)  
        
        # 自动执行  
        auto_execute = QTableWidgetItem("是" if task['auto_execute'] else "否")  
        self.task_table.setItem(row, 7, auto_execute)  
        
        # 操作按钮  
        operations = QWidget()  
        operations_layout = QHBoxLayout(operations)  
        operations_layout.setContentsMargins(0, 0, 0, 0)  
        
        if task['status'] == '待执行':  
            execute_btn = QPushButton("执行")  
            execute_btn.clicked.connect(lambda: self.execute_task(task['id']))  
            operations_layout.addWidget(execute_btn)  
            
            cancel_btn = QPushButton("取消")  
            cancel_btn.clicked.connect(lambda: self.cancel_task(task['id']))  
            operations_layout.addWidget(cancel_btn)  
        
        edit_btn = QPushButton("编辑")  
        edit_btn.clicked.connect(lambda: self.edit_task(task['id']))  
        operations_layout.addWidget(edit_btn)  
        
        remove_btn = QPushButton("删除")  
        remove_btn.clicked.connect(lambda: self.remove_task(task['id']))  
        operations_layout.addWidget(remove_btn)  
        
        self.task_table.setCellWidget(row, 8, operations)  
        
    def filter_tasks(self):  
        """过滤任务列表"""  
        search_text = self.search_input.text().lower()  
        type_filter = self.type_filter.currentText()  
        status_filter = self.status_filter.currentText()  
        
        for row in range(self.task_table.rowCount()):  
            show_row = True  
            
            # 搜索文本过滤  
            if search_text:  
                row_matches_search = False  
                for col in range(5):  # 搜索前5列  
                    item = self.task_table.item(row, col)  
                    if item and search_text in item.text().lower():  
                        row_matches_search = True  
                        break  
                show_row = row_matches_search  
            
            # 任务类型过滤  
            if show_row and type_filter != "全部类型":  
                type_item = self.task_table.item(row, 2)  
                if type_item and type_item.text() != type_filter:  
                    show_row = False  
            
            # 状态过滤  
            if show_row and status_filter != "全部状态":  
                status_item = self.task_table.item(row, 6)  
                if status_item and status_item.text() != status_filter:  
                    show_row = False  
            
            # 设置行的显示/隐藏状态  
            self.task_table.setRowHidden(row, not show_row)  
            
    def save_tasks(self):  
        """保存任务信息到文件"""  
        try:  
            if not os.path.exists('data'):  
                os.makedirs('data')  
            with open('data/tasks.json', 'w', encoding='utf-8') as f:  
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)  
        except Exception as e:  
            QMessageBox.warning(self, "错误", f"保存任务信息失败：{str(e)}")  
            
    def load_tasks(self):  
        """从文件加载任务信息"""  
        try:  
            if os.path.exists('data/tasks.json'):  
                with open('data/tasks.json', 'r', encoding='utf-8') as f:  
                    self.tasks = json.load(f)  
        except Exception as e:  
            QMessageBox.warning(self, "错误", f"加载任务信息失败：{str(e)}")  
            
    # 信号处理函数  
    def on_task_added(self, task_data):  
        """任务添加信号处理"""  
        print(f"任务已添加: {task_data['name']}")  
        QMessageBox.information(self, "成功", f"任务 '{task_data['name']}' 已创建")  
        
    def on_task_removed(self, task_id):  
        """任务删除信号处理"""  
        print(f"任务已删除: {task_id}")  
        
    def on_task_updated(self, task_data):  
        """任务更新信号处理"""  
        print(f"任务已更新: {task_data['name']}")  
        QMessageBox.information(self, "成功", f"任务 '{task_data['name']}' 已更新")  
        
    def on_task_executed(self, task_data):  
        """任务执行信号处理"""  
        print(f"任务开始执行: {task_data['name']}")  
        QMessageBox.information(self, "成功", f"任务 '{task_data['name']}' 开始执行")



class TaskPlanningPage(QWidget):  
    def create_task_from_ai(self, task_data):  
        """处理来自AI助手的任务创建请求"""  
        try:  
            # 根据task_data创建新任务  
            task_name = task_data["task_name"]  
            device_id = task_data["device_id"]  
            task_type = task_data["task_type"]  
            parameters = task_data["parameters"]  
            
            # 创建任务的具体实现...  
            
            return True  
        except Exception as e:  
            print(f"创建任务失败：{str(e)}")  
            return False