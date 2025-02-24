from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,   
                            QPushButton, QLabel, QScrollArea, QFrame, QApplication,QGraphicsDropShadowEffect)  
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QObject, QThread, QPropertyAnimation, QEasingCurve  
from PyQt5.QtGui import QFont, QTextCursor, QPainter, QColor, QPen  
import json  
import os  
import math  
from openai import OpenAI  

class LoadingWidget(QWidget):  
    """加载动画组件"""  
    def __init__(self, parent=None):  
        super().__init__(parent)  
        self.angle = 0  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_angle)  
        self.setFixedSize(40, 40)  
        self.hide()  

    def update_angle(self):  
        self.angle = (self.angle + 10) % 360  
        self.update()  

    def start_animation(self):  
        self.show()  
        self.timer.start(50)  

    def stop_animation(self):  
        self.timer.stop()  
        self.hide()  

    def paintEvent(self, event):  
        painter = QPainter(self)  
        painter.setRenderHint(QPainter.Antialiasing)  
        
        pen = QPen()  
        pen.setWidth(3)  
        pen.setColor(QColor("#007AFF"))  
        painter.setPen(pen)  
        
        center = self.rect().center()  
        radius = min(self.width(), self.height()) / 2 - 5  
        
        # 画一个不完整的圆，使用渐变透明效果  
        for i in range(0, 360, 10):  
            alpha = int(255 * (1 - i / 360))  
            pen.setColor(QColor(0, 122, 255, alpha))  
            painter.setPen(pen)  
            
            start_angle = (self.angle + i) % 360  
            rad = math.radians(start_angle)  
            x = center.x() + radius * math.cos(rad)  
            y = center.y() + radius * math.sin(rad)  
            
            painter.drawPoint(int(x), int(y))  

class AIWorker(QObject):  
    """AI工作线程"""  
    response_ready = pyqtSignal(str)  
    error_occurred = pyqtSignal(str)  
    started = pyqtSignal()  
    finished = pyqtSignal()  

    def __init__(self, client):  
        super().__init__()  
        self.client = client  
        self.conversation_history = []  

    def process_message(self, message, history):  
        self.started.emit()  
        try:  
            self.conversation_history = history.copy()  
            response = self.client.chat.completions.create(  
                model="deepseek-chat",  
                messages=self.conversation_history,  
                stream=False  
            )  
            ai_response = response.choices[0].message.content  
            self.response_ready.emit(ai_response)  
        except Exception as e:  
            self.error_occurred.emit(str(e))  
        finally:  
            self.finished.emit()  

class MessageWidget(QFrame):  
    """单条消息组件"""  
    def __init__(self, content, is_user=True, parent=None):  
        super().__init__(parent)  
        self.init_ui(content, is_user)  

    def init_ui(self, content, is_user):  
        # 创建主布局  
        main_layout = QHBoxLayout(self)  
        main_layout.setContentsMargins(10, 5, 10, 5)  
        
        # 创建消息气泡  
        message_bubble = QFrame()  
        bubble_layout = QVBoxLayout(message_bubble)  
        bubble_layout.setContentsMargins(10, 10, 10, 10)  

        # 添加阴影效果  
        shadow = QGraphicsDropShadowEffect()  
        shadow.setBlurRadius(10)  
        shadow.setXOffset(0)  
        shadow.setYOffset(2)  
        shadow.setColor(QColor(0, 0, 0, 30))  
        message_bubble.setGraphicsEffect(shadow)  
        
        # 创建文本显示区域  
        message_text = QLabel(content)  
        message_text.setWordWrap(True)  
        message_text.setTextFormat(Qt.AutoText)  
        message_text.setOpenExternalLinks(True)  
        
        # 设置字体  
        font = QFont()  
        font.setPointSize(10)  
        message_text.setFont(font)  
        
        # 计算文本大小并调整气泡大小  
        metrics = message_text.fontMetrics()  
        text_width = min(400, metrics.boundingRect(0, 0, 400, 1000,   
                        Qt.TextWordWrap | Qt.AlignLeft, content).width())  
        message_bubble.setFixedWidth(text_width + 40)  
        
        # 设置样式和布局位置  
        if is_user:  
            # 用户消息靠右  
            main_layout.addStretch()  
            message_bubble.setStyleSheet("""  
                QFrame {  
                    background-color: #007AFF;  
                    border-radius: 15px;  
                    border-top-right-radius: 5px;  
                }  
            """)  
            message_text.setStyleSheet("color: white; padding: 5px;")  
        else:  
            # AI消息靠左  
            message_bubble.setStyleSheet("""  
                QFrame {  
                    background-color: #E9E9E9;  
                    border-radius: 15px;  
                    border-top-left-radius: 5px;  
                }  
            """)  
            message_text.setStyleSheet("color: black; padding: 5px;")  
            main_layout.insertStretch(1, 1)  
        
        # 添加文本到气泡  
        bubble_layout.addWidget(message_text)  
        
        # 根据消息来源添加到布局  
        if is_user:  
            main_layout.addWidget(message_bubble)  
        else:  
            main_layout.insertWidget(0, message_bubble)
class AIAssistant(QWidget):  
    """AI助手组件"""  
    task_created = pyqtSignal(dict)  
    
    def __init__(self, parent=None):  
        super().__init__(parent)  
        
        # 初始化OpenAI客户端  
        self.client = OpenAI(  
            api_key="sk-58b389403c9f4fb7b06409d9be124f55",  
            base_url="https://api.deepseek.com"  
        )  
        
        # 初始化对话历史  
        self.conversation_history = [  
            {"role": "system", "content": self.get_system_prompt()}  
        ]  
        
        # 设置AI工作线程  
        self.thread = QThread()  
        self.worker = AIWorker(self.client)  
        self.worker.moveToThread(self.thread)  
        self.worker.response_ready.connect(self.handle_ai_response)  
        self.worker.error_occurred.connect(self.handle_error)  
        self.worker.started.connect(self.on_processing_started)  
        self.worker.finished.connect(self.on_processing_finished)  
        self.thread.start()  

        # 初始化加载动画组件  
        self.loading_widget = LoadingWidget(self)  
        self.loading_widget.hide()  
        
        # 初始化UI  
        self.init_ui()  
        self.load_stylesheet()
    def load_stylesheet(self):  
        """加载样式表"""  
        try:  
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
            style_path = os.path.join(base_dir, 'resource', 'styles', 'ai_assistant.qss')  
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"加载样式表失败：{str(e)}")  
        
    def init_ui(self):  
        """初始化UI"""  
        layout = QVBoxLayout(self)  
        layout.setSpacing(20)  
        layout.setContentsMargins(20, 20, 20, 20)  
        
        # 对话历史区域  
        self.scroll_area = QScrollArea(self)  
        self.scroll_area.setWidgetResizable(True)  
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  
        self.scroll_area.setStyleSheet("""  
            QScrollArea {  
                border: none;  
                background-color: #F0F0F0;  
            }  
            QScrollBar:vertical {  
                border: none;  
                background: #F0F0F0;  
                width: 8px;  
                margin: 0px;  
            }  
            QScrollBar::handle:vertical {  
                background: #CCCCCC;  
                border-radius: 4px;  
                min-height: 20px;  
            }  
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {  
                height: 0px;  
            }  
        """)  
        
        # 消息容器  
        self.message_container = QWidget()  
        self.message_container.setStyleSheet("background-color: #F0F0F0;")  
        self.message_layout = QVBoxLayout(self.message_container)  
        self.message_layout.setSpacing(15)  
        self.message_layout.setContentsMargins(10, 10, 10, 10)  
        self.message_layout.addStretch()  
        
        self.scroll_area.setWidget(self.message_container)  
        layout.addWidget(self.scroll_area)  
        
        # 输入区域  
        input_container = QWidget()  
        input_container.setStyleSheet("""  
            QWidget {  
                background-color: white;  
                border-radius: 10px;  
            }  
        """)  
        input_layout = QHBoxLayout(input_container)  
        input_layout.setSpacing(10)  
        input_layout.setContentsMargins(10, 10, 10, 10)  
        
        self.input_box = QTextEdit()  
        self.input_box.setPlaceholderText("请输入您的问题...")  
        self.input_box.setMinimumHeight(50)  
        self.input_box.setMaximumHeight(100)  
        self.input_box.setStyleSheet("""  
            QTextEdit {  
                border: none;  
                background-color: white;  
                font-size: 14px;  
            }  
        """)  
        
        send_button = QPushButton("发送")  
        send_button.setFixedSize(60, 35)  
        send_button.setCursor(Qt.PointingHandCursor)  
        send_button.setStyleSheet("""  
            QPushButton {  
                background-color: #007AFF;  
                color: white;  
                border-radius: 5px;  
                font-size: 14px;  
            }  
            QPushButton:hover {  
                background-color: #0056b3;  
            }  
        """)  
        send_button.clicked.connect(self.send_message)  
        
        input_layout.addWidget(self.input_box)  
        input_layout.addWidget(send_button)  
        
        layout.addWidget(input_container)
        # 添加欢迎消息  
        welcome_message = (  
            "您好！我是您的无人机助手。我可以帮您：\n"  
            "1. 回答关于无人机的技术问题\n"  
            "2. 协助创建和规划飞行任务\n"  
            "3. 解答系统使用相关问题\n"  
            "4. 提供安全建议和最佳实践\n\n"  
            "请问有什么可以帮您？"  
        )  
        self.add_message(welcome_message, False)  
        self.conversation_history.append({"role": "assistant", "content": welcome_message})  

        # 设置加载动画的位置  
        self.loading_widget.setGeometry(  
            self.width() - 60, self.height() - 140, 40, 40  
        )  

    def resizeEvent(self, event):  
        """处理窗口大小改变事件"""  
        super().resizeEvent(event)  
        # 更新加载动画的位置  
        self.loading_widget.setGeometry(  
            self.width() - 60, self.height() - 140, 40, 40  
        )  

    def on_processing_started(self):  
        """开始处理消息时的回调"""  
        self.input_box.setEnabled(False)  
        self.loading_widget.start_animation()  

    def on_processing_finished(self):  
        """处理完成时的回调"""  
        self.input_box.setEnabled(True)  
        self.loading_widget.stop_animation()  
    
    def add_message(self, content, is_user=True):  
        """添加新消息"""  
        message = MessageWidget(content, is_user)  
        self.message_layout.insertWidget(self.message_layout.count() - 1, message)  
        
        # 滚动到底部  
        QTimer.singleShot(100, self.scroll_to_bottom)  

    def scroll_to_bottom(self):  
        """滚动到对话底部"""  
        scrollbar = self.scroll_area.verticalScrollBar()  
        scrollbar.setValue(scrollbar.maximum())  
    
    def handle_ai_response(self, response):  
        """处理AI响应"""  
        try:  
            if "CREATE_TASK:" in response:  
                self.handle_task_creation(response)  
            else:  
                self.add_message(response, False)  
                self.conversation_history.append({"role": "assistant", "content": response})  
                self.scroll_to_bottom()  
        except Exception as e:  
            print(f"处理AI响应时出错: {str(e)}")  
            self.add_message("抱歉，处理响应时出现错误。", False)  
            
    def handle_error(self, error_message):  
        """处理错误"""  
        self.add_message(f"抱歉，发生了错误：{error_message}", False)  
    
    def get_system_prompt(self):  
        """获取系统提示词"""  
        return """你是一个专业的无人机系统助手，专门负责帮助用户了解和操作无人机系统。  

你的主要职责包括：  
1. 回答关于公司无人机产品的技术问题  
2. 协助用户创建和规划飞行任务  
3. 解答系统操作相关问题  
4. 提供安全建议和最佳实践  

当用户需要创建任务时，请收集以下必要信息并按照规定格式返回：  
CREATE_TASK:  
{  
    "task_name": "任务名称",  
    "device_id": "选择的设备ID",  
    "task_type": "任务类型(巡检/测绘/监控)",  
    "parameters": {  
        "flight_height": "飞行高度(米)",  
        "flight_speed": "飞行速度(米/秒)",  
        "waypoints": [  
            {"lat": "纬度", "lng": "经度", "action": "动作"}  
        ],  
        "other_params": "其他参数"  
    }  
}"""  
    
    def send_message(self):  
        """发送消息"""  
        content = self.input_box.toPlainText().strip()  
        if not content:  
            return  
            
        self.add_message(content, True)  
        self.input_box.clear()  
        
        self.conversation_history.append({"role": "user", "content": content})  
        self.worker.process_message(content, self.conversation_history)  
    
    def handle_task_creation(self, response):  
        """处理任务创建响应"""  
        try:  
            parts = response.split("CREATE_TASK:")  
            normal_response = parts[0].strip()  
            task_json_str = parts[1].strip()  
            
            if normal_response:  
                self.add_message(normal_response, False)  
            
            task_data = json.loads(task_json_str)  
            
            required_fields = ['task_name', 'device_id', 'task_type', 'parameters']  
            if not all(field in task_data for field in required_fields):  
                raise ValueError("任务数据缺少必要字段")  
            
            self.task_created.emit(task_data)  
            
            self.add_message("任务信息已收集完成，正在为您创建任务...", False)  
            
        except json.JSONDecodeError:  
            self.add_message("任务数据格式错误，请重试。", False)  
        except Exception as e:  
            self.add_message(f"创建任务时发生错误：{str(e)}", False)  

    def keyPressEvent(self, event):  
        """处理按键事件"""  
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:  
            self.send_message()  
        else:  
            super().keyPressEvent(event)  
            
    def closeEvent(self, event):  
        """关闭事件"""  
        self.thread.quit()  
        self.thread.wait()  
        super().closeEvent(event)  

if __name__ == '__main__':  
    import sys  
    
    app = QApplication(sys.argv)  
    assistant = AIAssistant()  
    assistant.resize(800, 600)  
    assistant.show()  
    sys.exit(app.exec_())