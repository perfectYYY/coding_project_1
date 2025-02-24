import sqlite3  
from pathlib import Path  
from utils.logger import Logger  
from utils.config import Config  

class DeviceDatabase:  
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
            self.logger.error(f"设备数据库连接失败: {str(e)}")  
            raise  

    def init_database(self):  
        """初始化设备数据库表"""  
        try:  
            # 创建设备表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS devices (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    device_id TEXT UNIQUE NOT NULL,  
                    name TEXT NOT NULL,  
                    type TEXT NOT NULL,  
                    status TEXT DEFAULT 'offline',  
                    battery INTEGER DEFAULT 0,  
                    signal INTEGER DEFAULT 0,  
                    last_online TIMESTAMP,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
                )  
            """)  

            # 创建设备日志表  
            self.cursor.execute("""  
                CREATE TABLE IF NOT EXISTS device_logs (  
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    device_id TEXT NOT NULL,  
                    log_type TEXT NOT NULL,  
                    message TEXT NOT NULL,  
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (device_id) REFERENCES devices (device_id)  
                )  
            """)  

            self.conn.commit()  
        except Exception as e:  
            self.logger.error(f"设备数据库初始化失败: {str(e)}")  
            raise  

    def __del__(self):  
        """确保关闭数据库连接"""  
        if self.conn:  
            self.conn.close()