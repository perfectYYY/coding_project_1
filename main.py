import sys  
from PyQt5.QtWidgets import QApplication  
from ui.login.login_window import LoginWindow  
from ui.main.main_window import MainWindow  
import os  

class Application:  
    def __init__(self):  
        self.app = QApplication(sys.argv)  
        
        # 设置应用程序样式  
        try:  
            # 修改样式表路径  
            base_dir = os.path.dirname(__file__)  
            style_path = os.path.join(base_dir, 'resources', 'styles', 'style.qss')  
            print(f"尝试加载样式表：{style_path}")  # 用于调试  
            with open(style_path, 'r', encoding='utf-8') as f:  
                self.app.setStyleSheet(f.read())  
        except Exception as e:  
            print(f"加载样式表失败：{str(e)}")  
            
        self.login_window = LoginWindow()  
        self.main_window = None  
        self.login_window.login_successful.connect(self.on_login_successful)  
        self.login_window.show()  

    def on_login_successful(self):  
        """登录成功的处理函数"""  
        self.login_window.close()  
        self.main_window = MainWindow()  
        self.main_window.show()  

    def run(self):  
        return self.app.exec_()  

if __name__ == '__main__':  
    app = Application()  
    sys.exit(app.run())