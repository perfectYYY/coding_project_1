from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QPushButton, QTableWidget, QTableWidgetItem,  
                           QDialog, QLineEdit, QFormLayout, QMessageBox,  
                           QComboBox, QHeaderView)  
from PyQt5.QtCore import Qt, pyqtSignal, QTimer  
from PyQt5.QtGui import QColor  
import json  
import os  

class DeviceDialog(QDialog):  
    """设备添加/编辑对话框"""  
    def __init__(self, parent=None, device_data=None):  
        super().__init__(parent)  
        self.device_data = device_data  
        self.init_ui()  
        
    def init_ui(self):  
        self.setWindowTitle("添加设备" if not self.device_data else "编辑设备")  
        self.setFixedSize(400, 300)  
        
        layout = QFormLayout(self)  
        
        # 设备名称  
        self.name_input = QLineEdit()  
        if self.device_data:  
            self.name_input.setText(self.device_data.get('name', ''))  
        layout.addRow("设备名称:", self.name_input)  
        
        # 设备型号  
        self.model_input = QComboBox()  
        self.model_input.addItems(["GIF model3", "GIF model5", "GIF modelY", "Genshin Impact series X"])  
        if self.device_data:  
            self.model_input.setCurrentText(self.device_data.get('model', ''))  
        layout.addRow("设备型号:", self.model_input)  
        
        # 序列号  
        self.serial_input = QLineEdit()  
        if self.device_data:  
            self.serial_input.setText(self.device_data.get('serial', ''))  
        layout.addRow("序列号:", self.serial_input)  
        
        # 固件版本  
        self.firmware_input = QLineEdit()  
        if self.device_data:  
            self.firmware_input.setText(self.device_data.get('firmware', ''))  
        layout.addRow("固件版本:", self.firmware_input)  
        
        # 确认和取消按钮  
        button_layout = QHBoxLayout()  
        confirm_btn = QPushButton("确认")  
        confirm_btn.clicked.connect(self.accept)  
        cancel_btn = QPushButton("取消")  
        cancel_btn.clicked.connect(self.reject)  
        
        button_layout.addWidget(confirm_btn)  
        button_layout.addWidget(cancel_btn)  
        layout.addRow("", button_layout)  
        
    def get_device_data(self):  
        """获取设备数据"""  
        return {  
            'name': self.name_input.text(),  
            'model': self.model_input.currentText(),  
            'serial': self.serial_input.text(),  
            'firmware': self.firmware_input.text(),  
            'status': 'offline'  # 新添加的设备默认为离线状态  
        }  

class DeviceManagementPage(QWidget):  
    # 定义信号  
    device_added = pyqtSignal(dict)  
    device_removed = pyqtSignal(str)  
    device_updated = pyqtSignal(dict)  
    
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.devices = {}  # 存储设备信息  
        self.load_devices()  # 加载已保存的设备  
        self.init_ui()  
        self.setup_connections()  
        
    def init_ui(self):  
        layout = QVBoxLayout(self)  
        
        # 顶部操作栏  
        top_bar = QHBoxLayout()  
        
        # 添加设备按钮  
        add_btn = QPushButton("添加设备")  
        add_btn.clicked.connect(self.show_add_device_dialog)  
        top_bar.addWidget(add_btn)  
        
        # 刷新按钮  
        refresh_btn = QPushButton("刷新")  
        refresh_btn.clicked.connect(self.refresh_devices)  
        top_bar.addWidget(refresh_btn)  
        
        top_bar.addStretch()  # 添加弹性空间  
        
        # 搜索框  
        self.search_input = QLineEdit()  
        self.search_input.setPlaceholderText("搜索设备...")  
        self.search_input.textChanged.connect(self.filter_devices)  
        top_bar.addWidget(self.search_input)  
        
        layout.addLayout(top_bar)  
        
        # 设备列表表格  
        self.device_table = QTableWidget()  
        self.device_table.setColumnCount(6)  
        self.device_table.setHorizontalHeaderLabels(["设备名称", "型号", "序列号", "固件版本", "状态", "操作"])  
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        layout.addWidget(self.device_table)  
        
        # 初始化设备表格  
        self.refresh_devices()  
        
        # 设置定时器更新设备状态  
        self.status_timer = QTimer(self)  
        self.status_timer.timeout.connect(self.update_device_status)  
        self.status_timer.start(5000)  # 每5秒更新一次  
        
    def setup_connections(self):  
        """设置信号连接"""  
        self.device_added.connect(self.on_device_added)  
        self.device_removed.connect(self.on_device_removed)  
        self.device_updated.connect(self.on_device_updated)  
        
    def show_add_device_dialog(self):  
        """显示添加设备对话框"""  
        dialog = DeviceDialog(self)  
        if dialog.exec_() == QDialog.Accepted:  
            device_data = dialog.get_device_data()  
            self.add_device(device_data)  
            
    def add_device(self, device_data):  
        """添加新设备"""  
        if not device_data['serial'] in self.devices:  
            self.devices[device_data['serial']] = device_data  
            self.device_added.emit(device_data)  
            self.save_devices()  
            self.refresh_devices()  
        else:  
            QMessageBox.warning(self, "错误", "设备序列号已存在！")  
            
    def remove_device(self, serial):  
        """删除设备"""  
        if serial in self.devices:  
            del self.devices[serial]  
            self.device_removed.emit(serial)  
            self.save_devices()  
            self.refresh_devices()  
            
    def edit_device(self, serial):  
        """编辑设备"""  
        if serial in self.devices:  
            dialog = DeviceDialog(self, self.devices[serial])  
            if dialog.exec_() == QDialog.Accepted:  
                device_data = dialog.get_device_data()  
                self.devices[serial] = device_data  
                self.device_updated.emit(device_data)  
                self.save_devices()  
                self.refresh_devices()  
                
    def refresh_devices(self):  
        """刷新设备列表"""  
        self.device_table.setRowCount(0)  
        for serial, device in self.devices.items():  
            self.add_device_to_table(device)  
            
    def add_device_to_table(self, device):  
        """将设备添加到表格中"""  
        row = self.device_table.rowCount()  
        self.device_table.insertRow(row)  
        
        # 添加设备信息  
        self.device_table.setItem(row, 0, QTableWidgetItem(device['name']))  
        self.device_table.setItem(row, 1, QTableWidgetItem(device['model']))  
        self.device_table.setItem(row, 2, QTableWidgetItem(device['serial']))  
        self.device_table.setItem(row, 3, QTableWidgetItem(device['firmware']))  
        
        # 状态显示  
        status_item = QTableWidgetItem(device['status'])  
        status_item.setForeground(QColor("#27ae60") if device['status'] == 'online' else QColor("#c0392b"))  
        self.device_table.setItem(row, 4, status_item)  
        
        # 操作按钮  
        operations = QWidget()  
        operations_layout = QHBoxLayout(operations)  
        operations_layout.setContentsMargins(0, 0, 0, 0)  
        
        edit_btn = QPushButton("编辑")  
        edit_btn.clicked.connect(lambda: self.edit_device(device['serial']))  
        
        remove_btn = QPushButton("删除")  
        remove_btn.clicked.connect(lambda: self.remove_device(device['serial']))  
        
        operations_layout.addWidget(edit_btn)  
        operations_layout.addWidget(remove_btn)  
        
        self.device_table.setCellWidget(row, 5, operations)  
        
    def filter_devices(self):  
        """过滤设备列表"""  
        search_text = self.search_input.text().lower()  
        for row in range(self.device_table.rowCount()):  
            show = False  
            for col in range(4):  # 只搜索前4列  
                item = self.device_table.item(row, col)  
                if item and search_text in item.text().lower():  
                    show = True  
                    break  
            self.device_table.setRowHidden(row, not show)  
            
    def update_device_status(self):  
        """更新设备状态（模拟）"""  
        import random  
        for serial in self.devices:  
            # 随机更新设备状态，实际应该根据真实设备状态更新  
            self.devices[serial]['status'] = 'online' if random.random() > 0.3 else 'offline'  
        self.refresh_devices()  
        
    def save_devices(self):  
        """保存设备信息到文件"""  
        try:  
            with open('data/devices.json', 'w') as f:  
                json.dump(self.devices, f)  
        except Exception as e:  
            QMessageBox.warning(self, "错误", f"保存设备信息失败：{str(e)}")  
            
    def load_devices(self):  
        """从文件加载设备信息"""  
        try:  
            if not os.path.exists('data'):  
                os.makedirs('data')  
            if os.path.exists('data/devices.json'):  
                with open('data/devices.json', 'r') as f:  
                    self.devices = json.load(f)  
        except Exception as e:  
            QMessageBox.warning(self, "错误", f"加载设备信息失败：{str(e)}")  
            
    # 信号处理函数  
    def on_device_added(self, device_data):  
        print(f"设备已添加: {device_data['name']}")  
        
    def on_device_removed(self, serial):  
        print(f"设备已移除: {serial}")  
        
    def on_device_updated(self, device_data):  
        print(f"设备已更新: {device_data['name']}")