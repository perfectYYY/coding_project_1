from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,   
                           QComboBox, QMessageBox)  
from PyQt5.QtWebEngineWidgets import QWebEngineView  
from PyQt5.QtCore import QUrl  
import os  

def get_resource_path(relative_path):  
    """获取资源文件的绝对路径"""  
    # 获取项目根目录  
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
    # 组合完整路径  
    return os.path.join(root_dir, relative_path)  

class MappingPage(QWidget):  
    def __init__(self):  
        super().__init__()  
        self.init_ui()  
        self.init_connections()  

    def init_ui(self):  
        """初始化UI"""  
        # 创建主布局  
        main_layout = QVBoxLayout(self)  
        
        # 创建工具栏布局  
        toolbar_layout = QHBoxLayout()  
        main_layout.addLayout(toolbar_layout)  
        
        # 添加地图类型选择下拉框  
        self.map_type_combo = QComboBox()  
        self.map_type_combo.addItems(['普通地图', '卫星地图', '混合地图'])  
        toolbar_layout.addWidget(self.map_type_combo)  
        
        # 添加按钮  
        self.add_route_btn = QPushButton('添加航线')  
        self.clear_route_btn = QPushButton('清除航线')  
        self.add_area_btn = QPushButton('添加区域')  
        self.clear_area_btn = QPushButton('清除区域')  
        
        toolbar_layout.addWidget(self.add_route_btn)  
        toolbar_layout.addWidget(self.clear_route_btn)  
        toolbar_layout.addWidget(self.add_area_btn)  
        toolbar_layout.addWidget(self.clear_area_btn)  
        
        toolbar_layout.addStretch()  # 添加弹簧  
        
        # 创建 WebEngineView  
        self.web_view = QWebEngineView()  
        main_layout.addWidget(self.web_view)  
        
        # 加载地图  
        self.load_map()  

    def init_connections(self):  
        """初始化信号连接"""  
        self.map_type_combo.currentIndexChanged.connect(self.change_map_type)  
        self.add_route_btn.clicked.connect(self.start_route_planning)  
        self.clear_route_btn.clicked.connect(self.clear_route)  
        self.add_area_btn.clicked.connect(self.start_area_planning)  
        self.clear_area_btn.clicked.connect(self.clear_area)  

    def load_map(self):  
        """加载地图"""  
        try:  
            map_path = get_resource_path('resources/map.html')  
            self.web_view.setUrl(QUrl.fromLocalFile(map_path))  
        except Exception as e:  
            QMessageBox.critical(self, '错误', f'加载地图失败：{str(e)}')  

    def change_map_type(self, index):  
        """切换地图类型"""  
        map_types = ['BMAP_NORMAL_MAP', 'BMAP_SATELLITE_MAP', 'BMAP_HYBRID_MAP']  
        if 0 <= index < len(map_types):  
            js_code = f'map.setMapType({map_types[index]});'  
            self.web_view.page().runJavaScript(js_code)  

    def start_route_planning(self):  
        """开始航线规划"""  
        js_code = '''  
        if (typeof startRoutePlanning === 'function') {  
            startRoutePlanning();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  
        self.add_route_btn.setEnabled(False)  

    def clear_route(self):  
        """清除航线"""  
        js_code = '''  
        if (typeof clearRoute === 'function') {  
            clearRoute();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  
        self.add_route_btn.setEnabled(True)  

    def start_area_planning(self):  
        """开始区域规划"""  
        js_code = '''  
        if (typeof startAreaPlanning === 'function') {  
            startAreaPlanning();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  
        self.add_area_btn.setEnabled(False)  

    def clear_area(self):  
        """清除区域"""  
        js_code = '''  
        if (typeof clearArea === 'function') {  
            clearArea();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  
        self.add_area_btn.setEnabled(True)  

    def get_route_points(self):  
        """获取航线点位信息"""  
        js_code = '''  
        if (typeof getRoutePoints === 'function') {  
            getRoutePoints();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  

    def get_area_points(self):  
        """获取区域点位信息"""  
        js_code = '''  
        if (typeof getAreaPoints === 'function') {  
            getAreaPoints();  
        }  
        '''  
        self.web_view.page().runJavaScript(js_code)  

    def handle_javascript_console_message(self, level, message, line, source_id):  
        """处理JavaScript控制台消息"""  
        print(f"JavaScript: {message} (line: {line}, source: {source_id})")