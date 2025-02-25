from PyQt5.QtWidgets import (  
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  
    QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget  
)  
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint  
from PyQt5.QtGui import QFont, QColor  
from core.auth.manager import AuthManager  
from utils.logger import Logger  
from utils.style_manager import StyleManager  


class LoginWindow(QMainWindow):  
    login_successful = pyqtSignal()  
    
    def __init__(self):  
        super().__init__()  
        self.logger = Logger(__name__)  
        self.auth_manager = AuthManager()  
        self.init_ui()  
        self.setup_connections()  
        
        # 加载样式表  
        self.setStyleSheet(StyleManager.load_style('login'))  
    
    def init_ui(self):  
        """初始化UI"""  
        self.setWindowTitle('登录/注册')  
        self.setFixedSize(500,800)  
        
        # 创建中心部件  
        central_widget = QWidget()  
        self.setCentralWidget(central_widget)  
        
        # 主布局  
        self.main_layout = QVBoxLayout(central_widget)  
        self.main_layout.setSpacing(35)  
        self.main_layout.setContentsMargins(60, 70, 60, 70)  
        
        # 创建堆叠窗口部件  
        self.stacked_widget = QStackedWidget()  
        self.main_layout.addWidget(self.stacked_widget)  
        
        # 创建登录页面和注册页面  
        self.login_page = self.create_login_page()  
        self.register_page = self.create_register_page()  
        
        # 添加页面到堆叠窗口  
        self.stacked_widget.addWidget(self.login_page)  
        self.stacked_widget.addWidget(self.register_page)  

        # 添加加载动画容器  
        self.loading_container = QWidget(self)  
        self.loading_container.setObjectName("loadingContainer")  
        self.loading_container.setFixedSize(200, 200)  
        self.loading_container.hide()  
        
        loading_layout = QVBoxLayout(self.loading_container)  
        
        # 加载中标签  
        self.loading_label = QLabel("登录中...")  
        self.loading_label.setAlignment(Qt.AlignCenter)  
        loading_layout.addWidget(self.loading_label)  
        
        # 成功标签  
        self.success_label = QLabel("登录成功!")  
        self.success_label.setObjectName("successLabel")  
        self.success_label.setAlignment(Qt.AlignCenter)  
        self.success_label.hide()  
        loading_layout.addWidget(self.success_label)  
    
    def create_login_page(self):  
        """创建登录页面"""  
        page = QWidget()  
        layout = QVBoxLayout(page)  
        layout.setSpacing(35)  
        
        # 标题容器  
        title_container = QWidget()  
        title_layout = QVBoxLayout(title_container)  
        
        # 标题  
        title = QLabel('Genshin Impact Fly')
        title.setObjectName("title")  
        title.setAlignment(Qt.AlignCenter)  
        title_layout.addWidget(title)  
        
        # 副标题  
        subtitle = QLabel('不一定专业的无人机管理平台')  
        subtitle.setObjectName("subtitle")  
        subtitle.setAlignment(Qt.AlignCenter)  
        title_layout.addWidget(subtitle)  
        
        layout.addWidget(title_container)  
        layout.addSpacing(20)  
        
        # 表单容器  
        form_container = QWidget()  
        form_container.setObjectName("formContainer")  
        form_layout = QVBoxLayout(form_container)  
        form_layout.setSpacing(20)  
        form_layout.setContentsMargins(20, 30, 20, 30)  
        
        # 用户名输入  
        username_layout = QVBoxLayout()  
        username_label = QLabel('用户名')  
        self.username_input = QLineEdit()  
        self.username_input.setPlaceholderText('请输入用户名')  
        username_layout.addWidget(username_label)  
        username_layout.addWidget(self.username_input)  
        form_layout.addLayout(username_layout)  
        
        # 密码输入  
        password_layout = QVBoxLayout()  
        password_label = QLabel('密码')  
        self.password_input = QLineEdit()  
        self.password_input.setPlaceholderText('请输入密码')  
        self.password_input.setEchoMode(QLineEdit.Password)  
        password_layout.addWidget(password_label)  
        password_layout.addWidget(self.password_input)  
        form_layout.addLayout(password_layout)  
        
        # 按钮布局  
        button_layout = QVBoxLayout()  
        button_layout.setSpacing(15)  
        
        # 登录按钮  
        login_btn = QPushButton('登 录')  
        login_btn.setFixedHeight(45)  
        login_btn.clicked.connect(self.login)  
        
        # 注册按钮  
        register_btn = QPushButton('注 册 账 号')  
        register_btn.setObjectName("transparentButton")  
        register_btn.setFixedHeight(45)  
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))  
        
        button_layout.addWidget(login_btn)  
        button_layout.addWidget(register_btn)  
        form_layout.addLayout(button_layout)  
        
        layout.addWidget(form_container)  
        return page  
    
    def create_register_page(self):  
        """创建注册页面"""  
        page = QWidget()  
        layout = QVBoxLayout(page)  
        layout.setSpacing(25)  
        
        # 标题  
        title = QLabel('注册新账号')  
        title.setObjectName("title")  
        title.setAlignment(Qt.AlignCenter)  
        layout.addWidget(title)  
        layout.addSpacing(20)  
        
        # 表单容器  
        form_container = QWidget()  
        form_container.setObjectName("formContainer")  
        form_layout = QVBoxLayout(form_container)  
        form_layout.setSpacing(20)  
        form_layout.setContentsMargins(20, 30, 20, 30)  
        
        # 用户名输入  
        username_layout = QVBoxLayout()  
        username_label = QLabel('用户名')  
        self.register_username = QLineEdit()  
        self.register_username.setPlaceholderText('请输入用户名(至少3个字符)')  
        username_layout.addWidget(username_label)  
        username_layout.addWidget(self.register_username)  
        form_layout.addLayout(username_layout)  
        
        # 密码输入  
        password_layout = QVBoxLayout()  
        password_label = QLabel('密码')  
        self.register_password = QLineEdit()  
        self.register_password.setPlaceholderText('请输入密码(至少6个字符)')  
        self.register_password.setEchoMode(QLineEdit.Password)  
        password_layout.addWidget(password_label)  
        password_layout.addWidget(self.register_password)  
        form_layout.addLayout(password_layout)  
        
        # 确认密码  
        confirm_layout = QVBoxLayout()  
        confirm_label = QLabel('确认密码')  
        self.confirm_password = QLineEdit()  
        self.confirm_password.setPlaceholderText('请再次输入密码')  
        self.confirm_password.setEchoMode(QLineEdit.Password)  
        confirm_layout.addWidget(confirm_label)  
        confirm_layout.addWidget(self.confirm_password)  
        form_layout.addLayout(confirm_layout)  
        
        # 邮箱输入  
        email_layout = QVBoxLayout()  
        email_label = QLabel('邮箱')  
        self.register_email = QLineEdit()  
        self.register_email.setPlaceholderText('请输入邮箱(可选)')  
        email_layout.addWidget(email_label)  
        email_layout.addWidget(self.register_email)  
        form_layout.addLayout(email_layout)  
        
        # 按钮布局  
        button_layout = QVBoxLayout()  
        button_layout.setSpacing(20)  
        
        # 注册按钮  
        register_btn = QPushButton('注 册')  
        register_btn.setFixedHeight(45)  
        register_btn.clicked.connect(self.register)  
        
        # 返回登录按钮  
        back_btn = QPushButton('返 回 登 录')  
        back_btn.setObjectName("transparentButton")  
        back_btn.setFixedHeight(45)  
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))  
        
        button_layout.addWidget(register_btn)  
        button_layout.addWidget(back_btn)  
        form_layout.addLayout(button_layout)  
        
        layout.addWidget(form_container)  
        return page  

    def center_loading_container(self):  
        """将加载容器居中显示"""  
        qr = self.loading_container.frameGeometry()  
        cp = self.geometry().center()  
        qr.moveCenter(cp)  
        self.loading_container.move(qr.topLeft())  

    def start_loading_animation(self):  
        """开始加载动画"""  
        self.loading_container.show()  
        self.center_loading_container()  
        
        # 创建淡入动画  
        self.fade_in = QPropertyAnimation(self.loading_container, b"windowOpacity")  
        self.fade_in.setDuration(300)  
        self.fade_in.setStartValue(0)  
        self.fade_in.setEndValue(1)  
        self.fade_in.setEasingCurve(QEasingCurve.InOutQuad)  
        self.fade_in.start()  

    def show_success_animation(self):  
        """显示成功动画"""  
        self.loading_label.hide()  
        self.success_label.show()  
        
        # 创建成功标签的弹跳动画  
        self.bounce = QPropertyAnimation(self.success_label, b"pos")  
        self.bounce.setDuration(500)  
        self.bounce.setStartValue(QPoint(0, 20))  
        self.bounce.setEndValue(QPoint(0, 0))  
        self.bounce.setEasingCurve(QEasingCurve.OutBounce)  
        self.bounce.start()  
        
        # 设置定时器在动画结束后关闭窗口  
        QTimer.singleShot(800, self.finish_login)  

    def finish_login(self):  
        """完成登录过程"""  
        # 创建淡出动画  
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")  
        self.fade_out.setDuration(300)  
        self.fade_out.setStartValue(1)  
        self.fade_out.setEndValue(0)  
        self.fade_out.setEasingCurve(QEasingCurve.InOutQuad)  
        self.fade_out.finished.connect(self.login_successful.emit)  
        self.fade_out.finished.connect(self.close)  
        self.fade_out.start()  
    
    def setup_connections(self):  
        """设置信号连接"""  
        self.auth_manager.login_successful.connect(self.on_login_successful)  
        self.auth_manager.login_failed.connect(self.on_login_failed)  
        self.auth_manager.register_successful.connect(self.on_register_successful)  
        self.auth_manager.register_failed.connect(self.on_register_failed)  
    
    def login(self):  
        """处理登录"""  
        username = self.username_input.text().strip()  
        password = self.password_input.text().strip()  
        
        if not username or not password:  
            QMessageBox.warning(  
                self,  
                "输入错误",  
                "用户名和密码不能为空！",  
                QMessageBox.StandardButton.Ok  
            )  
            return  
        
        # 显示加载动画  
        self.start_loading_animation()  
        
        # 使用QTimer模拟网络请求延迟  
        QTimer.singleShot(150, lambda: self.auth_manager.login(username, password))  
    
    def register(self):  
        """处理注册"""  
        username = self.register_username.text().strip()  
        password = self.register_password.text().strip()  
        confirm_pwd = self.confirm_password.text().strip()  
        email = self.register_email.text().strip()  
        
        # 输入验证  
        if not username or not password or not confirm_pwd:  
            QMessageBox.warning(  
                self,  
                "输入错误",  
                "用户名和密码不能为空！",  
                QMessageBox.StandardButton.Ok  
            )  
            return  
        
        if len(username) < 3:  
            QMessageBox.warning(  
                self,  
                "输入错误",  
                "用户名长度必须至少为3个字符！",  
                QMessageBox.StandardButton.Ok  
            )  
            return  
            
        if len(password) < 6:  
            QMessageBox.warning(  
                self,  
                "输入错误",  
                "密码长度必须至少为6个字符！",  
                QMessageBox.StandardButton.Ok  
            )  
            return  
            
        if password != confirm_pwd:  
            QMessageBox.warning(  
                self,  
                "输入错误",  
                "两次输入的密码不一致！",  
                QMessageBox.StandardButton.Ok  
            )  
            return  
            
        self.auth_manager.register(username, password, email)  
    
    def on_login_successful(self, user_data):  
        """登录成功处理"""  
        self.logger.info("登录成功")  
        self.show_success_animation()  

    def on_login_failed(self, error_msg):  
        """登录失败处理"""  
        self.logger.error(f"登录失败: {error_msg}")  
        # 隐藏加载动画  
        self.loading_container.hide()  
        
        QMessageBox.critical(  
            self,  
            "登录失败",  
            error_msg,  
            QMessageBox.StandardButton.Ok  
        )  
    
    def on_register_successful(self):  
        """注册成功处理"""  
        self.logger.info("注册成功")  
        QMessageBox.information(  
            self,  
            "注册成功",  
            "注册成功！请返回登录。",  
            QMessageBox.StandardButton.Ok  
        )  
        # 清空注册表单  
        self.register_username.clear()  
        self.register_password.clear()  
        self.confirm_password.clear()  
        self.register_email.clear()  
        # 切换回登录页面  
        self.stacked_widget.setCurrentIndex(0)  
    
    def on_register_failed(self, error_msg):  
        """注册失败处理"""  
        self.logger.error(f"注册失败: {error_msg}")