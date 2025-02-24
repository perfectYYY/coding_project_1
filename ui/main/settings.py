from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,   
                           QComboBox, QCheckBox, QPushButton, QFrame,  
                           QSpacerItem, QSizePolicy, QScrollArea)  
from PyQt5.QtCore import Qt, pyqtSignal  
from PyQt5.QtGui import QFont  
import os  

class SettingsPage(QWidget):  
    # 定义信号  
    settingsChanged = pyqtSignal(dict)  
    
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.setObjectName("settingsContainer")  
        self.load_stylesheet()  
        self.init_ui()  
        self.load_settings()  
        
    def load_stylesheet(self):  
        """加载样式表"""  
        try:  
            style_path = os.path.join("resources", "styles", "settings.qss")  
            with open(style_path, "r", encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"Failed to load stylesheet: {e}")  
        
    def init_ui(self):  
        # 创建主布局  
        main_layout = QVBoxLayout(self)  
        main_layout.setContentsMargins(20, 20, 20, 20)  
        main_layout.setSpacing(15)  
        
        # 创建滚动区域  
        scroll = QScrollArea()  
        scroll.setWidgetResizable(True)  
        scroll.setFrameShape(QFrame.NoFrame)  
        scroll.setObjectName("settingsScroll")  
        
        # 创建容器widget  
        container = QWidget()  
        container.setObjectName("settingsInnerContainer")  
        container_layout = QVBoxLayout(container)  
        container_layout.setSpacing(20)  
        
        # 添加标题  
        title_label = QLabel("设置")  
        title_label.setObjectName("titleLabel")  
        container_layout.addWidget(title_label)  
        
        # 添加分割线  
        line = QFrame()  
        line.setFrameShape(QFrame.HLine)  
        line.setFrameShadow(QFrame.Sunken)  
        container_layout.addWidget(line)  
        
        # 基本设置组  
        self.add_group_title(container_layout, "基本设置")  
        
        # 主题设置  
        theme_layout = QHBoxLayout()  
        theme_label = QLabel("主题:")  
        self.theme_combo = QComboBox()  
        self.theme_combo.setObjectName("themeCombo")  
        self.theme_combo.addItems(["浅色", "深色", "跟随系统"])  
        theme_layout.addWidget(theme_label)  
        theme_layout.addWidget(self.theme_combo)  
        theme_layout.addStretch()  
        container_layout.addLayout(theme_layout)  
        
        # 语言设置  
        lang_layout = QHBoxLayout()  
        lang_label = QLabel("语言:")  
        self.lang_combo = QComboBox()  
        self.lang_combo.setObjectName("langCombo")  
        self.lang_combo.addItems(["简体中文", "English"])  
        lang_layout.addWidget(lang_label)  
        lang_layout.addWidget(self.lang_combo)  
        lang_layout.addStretch()  
        container_layout.addLayout(lang_layout)  
        
        # 高级设置组  
        self.add_group_title(container_layout, "高级设置")  
        
        # 自动更新选项  
        self.auto_update_cb = QCheckBox("启用自动更新")  
        self.auto_update_cb.setObjectName("autoUpdateCheckBox")  
        container_layout.addWidget(self.auto_update_cb)  
        
        # 数据收集选项  
        self.data_collection_cb = QCheckBox("允许收集使用数据")  
        self.data_collection_cb.setObjectName("dataCollectionCheckBox")  
        container_layout.addWidget(self.data_collection_cb)  
        
        # 开发者选项  
        self.developer_mode_cb = QCheckBox("开发者模式")  
        self.developer_mode_cb.setObjectName("developerModeCheckBox")  
        container_layout.addWidget(self.developer_mode_cb)  
        
        # 添加底部弹性空间  
        container_layout.addStretch()  
        
        # 设置滚动区域  
        scroll.setWidget(container)  
        main_layout.addWidget(scroll)  
        
        # 添加按钮区域  
        buttons_layout = QHBoxLayout()  
        buttons_layout.addStretch()  
        
        # 取消按钮  
        self.cancel_btn = QPushButton("取消")  
        self.cancel_btn.setObjectName("cancelButton")  
        self.cancel_btn.clicked.connect(self.cancel_settings)  
        
        # 保存按钮  
        self.save_btn = QPushButton("保存")  
        self.save_btn.setObjectName("saveButton")  
        self.save_btn.clicked.connect(self.save_settings)  
        
        buttons_layout.addWidget(self.cancel_btn)  
        buttons_layout.addWidget(self.save_btn)  
        main_layout.addLayout(buttons_layout)  
        
    def add_group_title(self, layout, title):  
        """添加分组标题"""  
        label = QLabel(title)  
        label.setProperty("class", "groupTitle")  
        layout.addWidget(label)  
    
    def load_settings(self):  
        """加载设置"""  
        # TODO: 从配置文件或数据库加载设置  
        # 这里先使用默认值  
        self.theme_combo.setCurrentText("浅色")  
        self.lang_combo.setCurrentText("简体中文")  
        self.auto_update_cb.setChecked(True)  
        self.data_collection_cb.setChecked(False)  
        self.developer_mode_cb.setChecked(False)  
    
    def save_settings(self):  
        """保存设置"""  
        settings = {  
            'theme': self.theme_combo.currentText(),  
            'language': self.lang_combo.currentText(),  
            'auto_update': self.auto_update_cb.isChecked(),  
            'data_collection': self.data_collection_cb.isChecked(),  
            'developer_mode': self.developer_mode_cb.isChecked()  
        }  
        
        # 发送设置变更信号  
        self.settingsChanged.emit(settings)  
        
        # TODO: 保存到配置文件或数据库  
        
    def cancel_settings(self):  
        """取消设置"""  
        self.load_settings()  # 重新加载原始设置