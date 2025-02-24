import sqlite3  
from pathlib import Path  
from utils.logger import Logger  
from utils.config import Config  

class AuthDatabase:  
    def __init__(self):  
        self.logger = Logger(__name__)  
        self.db_path = Path(Config.DB_PATH)  
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  
        self.conn = None  
        self.cursor = None  
        self.connect()  
        self.init_database()  
    
    def connect(self):  
        """连接到数据库"""  
        try:  
            self.conn = sqlite3.connect(str(self.db_path))  
            self.conn.row_factory = sqlite3.Row  
            self.cursor = self.conn.cursor()  
        except Exception as e:  
            self.logger.error(f"数据库连接失败: {str(e)}")  
            raise  
    
    def execute_query(self, query: str, params: tuple = None) -> sqlite3.Row:  
        """执行查询并返回结果"""  
        try:  
            if params:  
                self.cursor.execute(query, params)  
            else:  
                self.cursor.execute(query)  
            
            result = self.cursor.fetchone()  
            return result  
            
        except Exception as e:  
            self.logger.error(f"查询执行失败: {str(e)}")  
            raise  
    
    def init_database(self):  
        """初始化数据库表"""  
        try:  
            # 创建用户表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS users (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    username TEXT UNIQUE NOT NULL,  
                    password TEXT NOT NULL,  
                    email TEXT,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
                )  
            """)  
            
            # 检查是否需要插入测试用户  
            self.cursor.execute("SELECT COUNT(*) FROM users")  
            if self.cursor.fetchone()[0] == 0:  
                self.cursor.execute("""  
                    INSERT INTO users (username, password, email)  
                    VALUES (?, ?, ?)  
                """, ('leon', 'Theleon13465', 'yuanyangyao790@gmail.com'))  
            
            self.conn.commit()  
            
        except Exception as e:  
            self.logger.error(f"数据库初始化失败: {str(e)}")  
            raise  


    
    def register_user(self, username: str, password: str, email: str = None) -> bool:  
        """  
        注册新用户  
        
        Args:  
            username: 用户名  
            password: 密码  
            email: 邮箱地址（可选）  
            
        Returns:  
            bool: 注册成功返回True，失败返回False  
            
        Raises:  
            Exception: 数据库操作错误  
        """  
        try:  
            # 检查用户名是否已存在  
            check_query = "SELECT username FROM users WHERE username = ?"  
            self.cursor.execute(check_query, (username,))  
            if self.cursor.fetchone():  
                self.logger.warning(f"用户名 {username} 已存在")  
                return False  
            
            # 验证输入数据  
            if not username or not password:  
                self.logger.error("用户名和密码不能为空")  
                return False  
                
            if len(username) < 3:  
                self.logger.error("用户名长度必须大于3个字符")  
                return False  
                
            if len(password) < 6:  
                self.logger.error("密码长度必须大于6个字符")  
                return False  
            
            # 插入新用户  
            insert_query = """  
                INSERT INTO users (username, password, email)  
                VALUES (?, ?, ?)  
            """  
            self.cursor.execute(insert_query, (username, password, email))  
            self.conn.commit()  
            
            self.logger.info(f"用户 {username} 注册成功")  
            return True  
            
        except sqlite3.IntegrityError as e:  
            self.logger.error(f"用户注册失败(完整性错误): {str(e)}")  
            return False  
        except Exception as e:  
            self.logger.error(f"用户注册失败: {str(e)}")  
            raise  
    
    def __del__(self):  
        """析构函数，确保关闭数据库连接"""  
        if self.conn:  
            self.conn.close()