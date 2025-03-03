from PyQt5.QtWidgets import (  
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,   
    QPushButton, QLabel, QStackedWidget, QFrame,  
    QGraphicsOpacityEffect, QComboBox, QMessageBox, QTabWidget 
)  
from PyQt5.QtCore import (  
    Qt, QPropertyAnimation, QEasingCurve, QPoint,   
    QTimer, QSize, QRect, QRectF, QPointF, QLineF  
)  
from PyQt5.QtGui import (  
    QFont, QIcon, QColor, QPainter, QPainterPath,   
    QPixmap  
)  
from math import cos, sin, pi  
from .mapping import MappingPage  
from .task_planning import TaskPlanningPage  
from .monitoring import MonitoringPage  
from .overview_page import OverviewPage  
from .ai_assistant import AIAssistant  
from .settings import SettingsPage
import os  

class IconFactory:  
    """图标工厂类"""  
    @staticmethod  
    def create_icon(icon_type, color=QColor("#ffffff"), size=QSize(24, 24)):  
        """创建图标"""  
        pixmap = QPixmap(size)  
        pixmap.fill(Qt.transparent)  
        painter = QPainter(pixmap)  
        painter.setRenderHint(QPainter.Antialiasing)  
        painter.setPen(color)  
        painter.setBrush(color)  

        rect = QRectF(0, 0, size.width(), size.height())  
        rect.adjust(2, 2, -2, -2)  # 留出2像素边距  

        if icon_type == "overview":  
            IconFactory._draw_overview_icon(painter, rect)  
        elif icon_type == "devices":  
            IconFactory._draw_devices_icon(painter, rect)  
        elif icon_type == "tasks":  
            IconFactory._draw_tasks_icon(painter, rect)  
        elif icon_type == "monitor":  
            IconFactory._draw_monitor_icon(painter, rect)  
        elif icon_type == "map":  
            IconFactory._draw_map_icon(painter, rect)  
        elif icon_type == "settings":  
            IconFactory._draw_settings_icon(painter, rect)  
        elif icon_type == "assistant":  
            IconFactory._draw_assistant_icon(painter, rect)  

        painter.end()  
        return QIcon(pixmap)  

    @staticmethod  
    def _draw_assistant_icon(painter, rect):  
        """绘制AI助手图标"""  
        path = QPainterPath()  
        
        # 主要气泡  
        bubble_rect = QRectF(rect.x(), rect.y(), rect.width() * 0.8, rect.height() * 0.7)  
        path.addRoundedRect(bubble_rect, 5, 5)  
        
        # 小气泡  
        small_bubble = QRectF(  
            rect.x() + rect.width() * 0.4,  
            rect.y() + rect.height() * 0.6,  
            rect.width() * 0.4,  
            rect.height() * 0.3  
        )  
        path.addRoundedRect(small_bubble, 3, 3)  
        
        painter.drawPath(path)  
        
        # 添加三个点  
        dot_y = bubble_rect.center().y()  
        dot_spacing = rect.width() * 0.15  
        dot_size = rect.width() * 0.08  
        
        for i in range(3):  
            x = bubble_rect.x() + bubble_rect.width() * 0.25 + i * dot_spacing  
            painter.drawEllipse(QRectF(x - dot_size/2, dot_y - dot_size/2, dot_size, dot_size))  

    @staticmethod  
    def _draw_overview_icon(painter, rect):  
        """绘制总览图标"""  
        painter.drawRect(QRectF(  
            rect.x(),  
            rect.y(),  
            rect.width() * 0.45,  
            rect.height() * 0.45  
        ))  
        painter.drawRect(QRectF(  
            rect.x() + rect.width() * 0.55,  
            rect.y(),  
            rect.width() * 0.45,  
            rect.height() * 0.45  
        ))  
        painter.drawRect(QRectF(  
            rect.x(),  
            rect.y() + rect.height() * 0.55,  
            rect.width() * 0.45,  
            rect.height() * 0.45  
        ))  
        painter.drawRect(QRectF(  
            rect.x() + rect.width() * 0.55,  
            rect.y() + rect.height() * 0.55,  
            rect.width() * 0.45,  
            rect.height() * 0.45  
        ))  

    @staticmethod  
    def _draw_devices_icon(painter, rect):  
        """绘制设备图标"""  
        path = QPainterPath()  
        path.moveTo(rect.center().x(), rect.y())  
        path.lineTo(rect.x(), rect.bottom())  
        path.lineTo(rect.right(), rect.bottom())  
        path.lineTo(rect.center().x(), rect.y())  
        painter.drawPath(path)  

    @staticmethod  
    def _draw_tasks_icon(painter, rect):  
        """绘制任务图标"""  
        for i in range(3):  
            y = rect.y() + i * (rect.height() * 0.4)  
            painter.drawRect(QRectF(  
                rect.x(),  
                y,  
                rect.width(),  
                rect.height() * 0.3  
            ))  

    @staticmethod  
    def _draw_monitor_icon(painter, rect):  
        """绘制监控图标"""  
        painter.drawRect(rect)  
        painter.drawLine(  
            QPointF(rect.x(), rect.center().y()),  
            QPointF(rect.right(), rect.center().y())  
        )  
        painter.drawLine(  
            QPointF(rect.center().x(), rect.y()),  
            QPointF(rect.center().x(), rect.bottom())  
        )  

    @staticmethod  
    def _draw_map_icon(painter, rect):  
        """绘制地图图标"""  
        path = QPainterPath()  
        path.moveTo(rect.x(), rect.y())  
        path.lineTo(rect.center().x(), rect.bottom())  
        path.lineTo(rect.right(), rect.y())  
        path.lineTo(rect.x(), rect.y())  
        painter.drawPath(path)  

    @staticmethod  
    def _draw_settings_icon(painter, rect):  
        """绘制设置图标"""  
        center = rect.center()  
        radius = min(rect.width(), rect.height()) * 0.4  
        painter.drawEllipse(center, radius, radius)  
        num_spokes = 8  
        spoke_length = radius * 0.3  
        
        for i in range(num_spokes):  
            angle = i * (360 / num_spokes)  
            rad_angle = angle * pi / 180  
            start_point = QPointF(  
                center.x() + radius * 1.2 * cos(rad_angle),  
                center.y() + radius * 1.2 * sin(rad_angle)  
            )  
            end_point = QPointF(  
                center.x() + (radius + spoke_length) * 1.2 * cos(rad_angle),  
                center.y() + (radius + spoke_length) * 1.2 * sin(rad_angle)  
            )  
            painter.drawLine(QLineF(start_point, end_point))
class NavigationButton(QPushButton):  
    """自定义导航按钮"""  
    def __init__(self, text, icon_type, parent=None):  
        super().__init__(parent)  
        self.setText(text)  
        self.setIcon(IconFactory.create_icon(icon_type))  
        self.setIconSize(QSize(24, 24))  
        self.setCheckable(True)  
        self.setAutoExclusive(True)  
        self.setFixedHeight(50)  

class SlideStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self._current_index = 0

    def slide_in(self, index):
        """滑入指定索引的窗口（安全增强版）"""
        try:
            # 边界检查
            if index < 0 or index >= self.count():
                raise IndexError(f"无效索引: {index} (总页数: {self.count()})")
            
            # 重复点击检查
            if index == self.currentIndex():
                return

            # 动画参数设置
            offset = self.width() if index > self.currentIndex() else -self.width()
            next_page = self.widget(index)
            
            # 页面可见性处理
            next_page.show()
            next_page.raise_()

            # 动画配置
            self.animation.stop()
            self.animation.setStartValue(self.pos())
            self.animation.setEndValue(self.pos() + QPoint(offset, 0))
            self.animation.finished.connect(
                lambda: self._complete_slide(index)
            )
            self.animation.start()
            
            # 更新当前索引
            self._current_index = index

        except Exception as e:
            print(f"页面切换失败: {str(e)}")
            QMessageBox.warning(self.parent(), "错误", f"无法切换页面: {str(e)}")

    def _complete_slide(self, index):
        """完成动画后的处理"""
        try:
            self.setCurrentIndex(index)
            self.move(self.animation.startValue())
            self.animation.finished.disconnect()
        except Exception as e:
            print(f"动画完成处理失败: {str(e)}")
class MainWindow(QMainWindow):  
    def __init__(self):
        super().__init__()
        self.init_ui()  
        self.load_stylesheet()

    def init_ui(self):  
        """初始化UI"""  
        self.setWindowTitle('Genshin Impact Fly')  
        self.setMinimumSize(1200, 800)  
        
        main_widget = QWidget()  
        self.setCentralWidget(main_widget)  
        
        layout = QHBoxLayout(main_widget)  
        layout.setSpacing(0)  
        layout.setContentsMargins(0, 0, 0, 0)  
        
        self.nav_widget = self.create_nav_widget()  
        layout.addWidget(self.nav_widget)  
        
        self.content_widget = self.create_content_widget()  
        layout.addWidget(self.content_widget)  
        
        layout.setStretch(0, 1)  
        layout.setStretch(1, 5)  
        
        self.init_status_update()

    def _connect_signals(self):
        # 修改信号连接方式
        self.monitor_page.device_status_changed.connect(
            self._handle_device_status_change
        )

    def _handle_device_status_change(self, device_id, status):
        """统一处理设备状态变更"""
        # 更新设备管理页面的数据
        for serial, device in self.device_manager.devices.items():
            if device.get('id') == device_id:  # 假设设备数据中有id字段
                device['status'] = status
                self.device_manager.device_updated.emit(device)
                break
    def load_initial_devices(self, devices):
        """初始化加载设备"""
        for serial, device in devices.items():
            self.add_device_card(device)

    def create_nav_widget(self):  
        """创建导航栏"""  
        nav_widget = QWidget()  
        nav_widget.setObjectName("navWidget")  
        nav_widget.setFixedWidth(200)  
        
        layout = QVBoxLayout(nav_widget)  
        layout.setSpacing(10)  
        layout.setContentsMargins(10, 20, 10, 20)  
        
        logo_label = QLabel("UAV SYSTEM")  
        logo_label.setObjectName("logoLabel")  
        logo_label.setAlignment(Qt.AlignCenter)  
        layout.addWidget(logo_label)  
        
        line = QFrame()  
        line.setFrameShape(QFrame.HLine)  
        line.setObjectName("separatorLine")  
        layout.addWidget(line)  
        
        self.nav_buttons = []  
        nav_items = [  
            ("总览", "overview"),  
            ("任务规划", "tasks"),  
            ("实时监控", "monitor"),  
            ("地图规划", "map"),  
            ("AI唐手", "assistant")  
        ]  
        
        for text, icon_type in nav_items:  
            btn = NavigationButton(text, icon_type)  
            btn.clicked.connect(lambda checked, index=len(self.nav_buttons):  
                              self.switch_page(index))  
            layout.addWidget(btn)  
            self.nav_buttons.append(btn)  
        
        layout.addStretch()  

        # 修改设置按钮的创建和添加  
        settings_btn = NavigationButton("设置", "settings")  
        settings_btn.setObjectName("settingsButton")  
        settings_btn.clicked.connect(self.show_settings)  
        layout.addWidget(settings_btn)  
        
        self.nav_buttons[0].setChecked(True)  
        
        return nav_widget
    def create_content_widget(self):  
        """创建内容区"""  
        content_widget = QWidget()  
        content_widget.setObjectName("contentWidget")  
        
        layout = QVBoxLayout(content_widget)  
        layout.setContentsMargins(20, 20, 20, 20)  
        
        title_widget = QWidget()  
        title_layout = QHBoxLayout(title_widget)  
        
        self.page_title = QLabel("总览")  
        self.page_title.setObjectName("pageTitle")  
        title_layout.addWidget(self.page_title)  
        
        title_layout.addStretch()  
        
        user_info = QLabel("冒险者")  
        user_info.setObjectName("userInfo")  
        title_layout.addWidget(user_info)  
        
        layout.addWidget(title_widget)  
        
        self.stack_widget = SlideStackedWidget()  
        
        # 添加各个页面  
        self.stack_widget.addWidget(OverviewPage())    
        self.stack_widget.addWidget(TaskPlanningPage())  
        self.stack_widget.addWidget(MonitoringPage())  
        self.stack_widget.addWidget(MappingPage())  
        
        # 添加AI助手页面  
        self.ai_assistant = AIAssistant()  
        self.ai_assistant.task_created.connect(self.handle_ai_task_creation)  
        self.stack_widget.addWidget(self.ai_assistant)  
        
        layout.addWidget(self.stack_widget)  
        
        return content_widget  

    def handle_ai_task_creation(self, task_data):  
        """处理AI助手创建的任务"""  
        try:  
            # 切换到任务规划页面  
            task_page_index = 2  # 任务规划页面的索引  
            self.switch_page(task_page_index)  
            
            # 获取任务规划页面实例  
            task_page = self.stack_widget.widget(task_page_index)  
            if isinstance(task_page, TaskPlanningPage):  
                if hasattr(task_page, 'create_task_from_ai'):  
                    success = task_page.create_task_from_ai(task_data)  
                    if not success:  
                        raise Exception("任务创建失败")  
                else:  
                    raise Exception("任务规划页面不支持AI任务创建")  
        except Exception as e:  
            print(f"处理AI任务创建失败：{str(e)}")  
            QMessageBox.warning(self, "错误", f"创建任务失败：{str(e)}")  

    def switch_page(self, index):  
        """切换页面"""  
        self.stack_widget.slide_in(index)  
        self.page_title.setText(self.nav_buttons[index].text())  
        self.nav_buttons[index].setChecked(True)  

    def show_settings(self):
        """显示设置页面（安全版）"""
        try:
            # 创建设置页面前检查现有实例
            existing_index = None
            for i in range(self.stack_widget.count()):
                if isinstance(self.stack_widget.widget(i), SettingsPage):
                    existing_index = i
                    break

            if existing_index is None:
                settings_page = SettingsPage(self)
                settings_page.settingsChanged.connect(self.handle_settings_changed)
                existing_index = self.stack_widget.addWidget(settings_page)

            # 更新界面状态
            self.page_title.setText("设置")
            for btn in self.nav_buttons:
                btn.setChecked(False)
            self.nav_widget.findChild(NavigationButton, "settingsButton").setChecked(True)
        
            # 安全切换
            if 0 <= existing_index < self.stack_widget.count():
                self.stack_widget.slide_in(existing_index)
            else:
                raise IndexError("设置页面索引无效")

        except Exception as e:
            print(f"打开设置失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"无法打开设置: {str(e)}")  

    def handle_settings_changed(self, settings):  
        """处理设置变更"""  
        if 'theme' in settings:  
            self.apply_theme(settings['theme'])  
        
        if 'language' in settings:  
            self.change_language(settings['language'])  
        
        # 其他设置的处理  
        print("Settings applied:", settings)  

    def apply_theme(self, theme):  
        """应用主题设置"""  
        try:  
            base_dir = self.get_base_dir()  
            if theme == "深色":  
                style_path = os.path.join(base_dir, 'resource', 'styles', 'dark_theme.qss')  
            elif theme == "浅色":  
                style_path = os.path.join(base_dir, 'resource', 'styles', 'light_theme.qss')  
            else:  # 跟随系统  
                style_path = os.path.join(base_dir, 'resource', 'styles', 'styles.qss')  
                
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"应用主题失败：{str(e)}")  

    def change_language(self, language):  
        """切换语言"""  
        # TODO: 实现语言切换逻辑  
        print(f"切换语言到：{language}")  

    def init_status_update(self):  
        """初始化状态更新"""  
        self.status_timer = QTimer()  
        self.status_timer.timeout.connect(self.update_status)  
        self.status_timer.start(1000)  

    def update_status(self):  
        """更新状态"""  
        pass  

    def load_stylesheet(self):  
        """加载样式表"""  
        try:  
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
            # 加载主样式表  
            style_path = os.path.join(base_dir, 'resource', 'styles', 'styles.qss')  
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"加载样式表失败：{str(e)}")
    def closeEvent(self, event):  
        """窗口关闭事件"""  
        try:  
            # 停止状态更新定时器  
            if hasattr(self, 'status_timer'):  
                self.status_timer.stop()  
            
            # 清理各个页面资源  
            for i in range(self.stack_widget.count()):  
                page = self.stack_widget.widget(i)  
                if hasattr(page, 'cleanup'):  
                    try:  
                        page.cleanup()  
                    except Exception as e:  
                        print(f"清理页面 {type(page).__name__} 时发生错误: {str(e)}")  
            
            event.accept()  
        except Exception as e:  
            print(f"窗口关闭时发生错误：{str(e)}")  
            event.accept()  

    def resizeEvent(self, event):  
        """窗口大小改变事件"""  
        super().resizeEvent(event)  
        # 更新堆叠窗口中所有页面的大小  
        for i in range(self.stack_widget.count()):  
            widget = self.stack_widget.widget(i)  
            if widget:  
                widget.setGeometry(0, 0, self.stack_widget.width(), self.stack_widget.height())  

    def showEvent(self, event):  
        """窗口显示事件"""  
        super().showEvent(event)  
        # 初始化显示第一个页面  
        self.switch_page(0)  

    def changeEvent(self, event):  
        """窗口状态改变事件"""  
        super().changeEvent(event)  
        if event.type() == event.WindowStateChange:  
            # 窗口最大化或恢复时更新页面大小  
            self.resizeEvent(None)  

    @staticmethod  
    def get_base_dir():  
        """获取基础目录"""  
        return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  


if __name__ == '__main__':  
    import sys  
    from PyQt5.QtWidgets import QApplication  
    
    app = QApplication(sys.argv)  
    
    # 设置应用程序图标  
    try:  
        base_dir = MainWindow.get_base_dir()  
        icon_path = os.path.join(base_dir, 'resource', 'icons', 'app_icon.png')  
        app.setWindowIcon(QIcon(icon_path))  
    except Exception as e:  
        print(f"设置应用程序图标失败：{str(e)}")  
    
    # 设置应用程序样式  
    app.setStyle('Fusion')  
    
    # 创建并显示主窗口  
    window = MainWindow()  
    window.show()  
    
    sys.exit(app.exec_())