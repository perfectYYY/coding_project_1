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
        """连接到数据库，支持多线程"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA journal_mode=WAL;")  # 开启 WAL 模式，提高并发性能
        except Exception as e:
            self.logger.error(f"任务数据库连接失败: {str(e)}")
            raise

    def init_database(self):
        """初始化任务数据库表，使用事务管理"""
        try:
            with self.conn:  # 自动提交，异常时回滚
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
        except Exception as e:
            self.logger.error(f"任务数据库初始化失败: {str(e)}")
            raise

    def close(self):
        """手动关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.logger.info("数据库连接已关闭")

    def __del__(self):
        """自动关闭数据库连接"""
        self.close()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 语句时自动关闭数据库"""
        self.close()
