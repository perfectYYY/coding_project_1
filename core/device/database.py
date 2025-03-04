import sqlite3
import threading
from pathlib import Path
from utils.logger import Logger
from utils.config import Config
import time
import random

class DeviceDatabase:
    def __init__(self):
        self.logger = Logger(__name__)
        self.db_path = Path(Config.DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.cursor = None
        self.lock = threading.Lock()  # 线程锁，防止并发问题
        self.connect()
        self.init_database()

    def connect(self):
        """连接到数据库，支持多线程"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)  # 允许多线程
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA journal_mode=WAL;")  # 开启 WAL 模式，提高并发性能
        except Exception as e:
            self.logger.error(f"设备数据库连接失败: {str(e)}")
            raise

    def init_database(self):
        """初始化设备数据库表"""
        try:
            with self.conn:
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
        except Exception as e:
            self.logger.error(f"设备数据库初始化失败: {str(e)}")
            raise

    def insert_log(self, device_id, log_type, message):
        """插入设备日志"""
        try:
            with self.lock:  # 保证多线程安全
                with self.conn:
                    self.cursor.execute("""
                        INSERT INTO device_logs (device_id, log_type, message) 
                        VALUES (?, ?, ?)
                    """, (device_id, log_type, message))
        except Exception as e:
            self.logger.error(f"设备 {device_id} 日志插入失败: {str(e)}")

    def close(self):
        """手动关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.logger.info("数据库连接已关闭")

    def __del__(self):
        """自动关闭数据库连接"""
        self.close()
