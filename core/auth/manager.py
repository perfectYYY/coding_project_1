from PyQt5.QtCore import QObject, pyqtSignal  
from utils.logger import Logger  
from core.auth.database import AuthDatabase  

class AuthManager(QObject):  
    login_successful = pyqtSignal(dict)  
    login_failed = pyqtSignal(str)  
    register_successful = pyqtSignal()  # 添加注册成功信号  
    register_failed = pyqtSignal(str)   # 添加注册失败信号  
    
    def __init__(self):  
        super().__init__()  
        self.logger = Logger(__name__)  
        self.db = AuthDatabase()  
    
    def login(self, username: str, password: str) -> bool:  
        try:  
            # 查询用户  
            query = "SELECT * FROM users WHERE username = ? AND password = ?"  
            result = self.db.execute_query(query, (username, password))  
            
            if result:  
                # 将 sqlite3.Row 转换为字典  
                user_data = dict(zip([col[0] for col in self.db.cursor.description], result))  
                self.logger.info(f"用户 {username} 登录成功")  
                self.login_successful.emit(user_data)  
                return True  
            else:  
                error_msg = "用户名或密码错误"  
                self.logger.warning(f"登录失败: {error_msg}")  
                self.login_failed.emit(error_msg)  
                return False  
                
        except Exception as e:  
            error_msg = f"登录过程出错: {str(e)}"  
            self.logger.error(error_msg)  
            self.login_failed.emit(error_msg)  
            return False  
    
    def register(self, username: str, password: str, email: str = None) -> bool:  
        """  
        注册新用户  
        
        Args:  
            username: 用户名  
            password: 密码  
            email: 邮箱地址（可选）  
            
        Returns:  
            bool: 注册是否成功  
        """  
        try:  
            # 检查用户名是否已存在  
            check_query = "SELECT username FROM users WHERE username = ?"  
            result = self.db.execute_query(check_query, (username,))  
            
            if result:  
                error_msg = f"用户名 {username} 已存在"  
                self.logger.warning(error_msg)  
                self.register_failed.emit(error_msg)  
                return False  
            
            # 验证输入  
            if len(username) < 3:  
                error_msg = "用户名长度必须至少为3个字符"  
                self.register_failed.emit(error_msg)  
                return False  
                
            if len(password) < 6:  
                error_msg = "密码长度必须至少为6个字符"  
                self.register_failed.emit(error_msg)  
                return False  
            
            # 插入新用户  
            insert_query = """  
                INSERT INTO users (username, password, email)  
                VALUES (?, ?, ?)  
            """  
            self.db.cursor.execute(insert_query, (username, password, email))  
            self.db.conn.commit()  
            
            self.logger.info(f"用户 {username} 注册成功")  
            self.register_successful.emit()  
            return True  
            
        except Exception as e:  
            error_msg = f"注册过程出错: {str(e)}"  
            self.logger.error(error_msg)  
            self.register_failed.emit(error_msg)  
            return False  
    
    def check_username_exists(self, username: str) -> bool:  
        """  
        检查用户名是否已存在  
        
        Args:  
            username: 要检查的用户名  
            
        Returns:  
            bool: 用户名是否已存在  
        """  
        try:  
            query = "SELECT username FROM users WHERE username = ?"  
            result = self.db.execute_query(query, (username,))  
            return bool(result)  
        except Exception as e:  
            self.logger.error(f"检查用户名时出错: {str(e)}")  
            return False