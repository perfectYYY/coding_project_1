import sqlite3  
from pathlib import Path  
from utils.logger import Logger  
from utils.config import Config  

class TaskDatabase:  
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
            self.logger.error(f"任务数据库连接失败: {str(e)}")  
            raise  

    def init_database(self):  
        """初始化任务数据库表"""  
        try:  
            # 创建任务表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS tasks (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    task_id TEXT UNIQUE NOT NULL,  
                    name TEXT NOT NULL,  
                    type TEXT NOT NULL,  
                    status TEXT DEFAULT 'pending',  
                    priority INTEGER DEFAULT 0,  
                    progress INTEGER DEFAULT 0,  
                    device_id TEXT,  
                    description TEXT,  
                    start_time TIMESTAMP,  
                    end_time TIMESTAMP,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)  
                )  
            """)  

            # 创建任务参数表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS task_params (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    task_id TEXT NOT NULL,  
                    param_name TEXT NOT NULL,  
                    param_value TEXT NOT NULL,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)  
                )  
            """)  

            # 创建任务日志表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS task_logs (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    task_id TEXT NOT NULL,  
                    log_type TEXT NOT NULL,  
                    message TEXT NOT NULL,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)  
                )  
            """)  

            self.conn.commit()  
        except Exception as e:  
            self.logger.error(f"任务数据库初始化失败: {str(e)}")  
            raise  

    def __del__(self):  
        """确保关闭数据库连接"""  
        if self.conn:  
            self.conn.close()