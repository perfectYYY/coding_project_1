import sqlite3  
from datetime import datetime
from .database import DeviceDatabase  
from utils.logger import Logger  

class DeviceManager:  
    def __init__(self):  
        self.logger = Logger(__name__)  
        self.db = DeviceDatabase()  

    def add_device(self, device_id: str, name: str, device_type: str) -> bool:  
        """添加新设备"""  
        try:  
            self.db.cursor.execute("""  
                INSERT INTO devices (device_id, name, type)  
                VALUES (?, ?, ?)  
            """, (device_id, name, device_type))  
            self.db.conn.commit()  
            self.logger.info(f"设备添加成功: {device_id}")  
            return True  
        except sqlite3.IntegrityError:  
            self.logger.warning(f"设备已存在: {device_id}")  
            return False  
        except Exception as e:  
            self.logger.error(f"添加设备失败: {str(e)}")  
            return False  

    def update_device_status(self, device_id: str, status: str, battery: int = None, signal: int = None):  
        """更新设备状态"""  
        try:  
            update_fields = ["status = ?"]  
            params = [status]  
            
            if battery is not None:  
                update_fields.append("battery = ?")  
                params.append(battery)  
            
            if signal is not None:  
                update_fields.append("signal = ?")  
                params.append(signal)  
            
            update_fields.append("last_online = CURRENT_TIMESTAMP")  
            
            query = f"""  
                UPDATE devices   
                SET {', '.join(update_fields)}  
                WHERE device_id = ?  
            """  
            params.append(device_id)  
            
            self.db.cursor.execute(query, tuple(params))  
            self.db.conn.commit()  
            self.logger.info(f"设备状态更新成功: {device_id}")  
            return True  
        except Exception as e:  
            self.logger.error(f"更新设备状态失败: {str(e)}")  
            return False  

    def get_device(self, device_id: str) -> dict:  
        """获取设备信息"""  
        try:  
            result = self.db.cursor.execute("""  
                SELECT * FROM devices WHERE device_id = ?  
            """, (device_id,)).fetchone()  
            
            if result:  
                return dict(result)  
            return None  
        except Exception as e:  
            self.logger.error(f"获取设备信息失败: {str(e)}")  
            return None  

    def get_all_devices(self) -> list:  
        """获取所有设备信息"""  
        try:  
            result = self.db.cursor.execute("SELECT * FROM devices").fetchall()  
            return [dict(row) for row in result]  
        except Exception as e:  
            self.logger.error(f"获取设备列表失败: {str(e)}")  
            return []  

    def add_device_log(self, device_id: str, log_type: str, message: str):  
        """添加设备日志"""  
        try:  
            self.db.cursor.execute("""  
                INSERT INTO device_logs (device_id, log_type, message)  
                VALUES (?, ?, ?)  
            """, (device_id, log_type, message))  
            self.db.conn.commit()  
            self.logger.info(f"设备日志添加成功: {device_id}")  
            return True  
        except Exception as e:  
            self.logger.error(f"添加设备日志失败: {str(e)}")  
            return False  

    def get_device_logs(self, device_id: str, limit: int = 100) -> list:  
        """获取设备日志"""  
        try:  
            result = self.db.cursor.execute("""  
                SELECT * FROM device_logs   
                WHERE device_id = ?  
                ORDER BY created_at DESC  
                LIMIT ?  
            """, (device_id, limit)).fetchall()  
            return [dict(row) for row in result]  
        except Exception as e:  
            self.logger.error(f"获取设备日志失败: {str(e)}")  
            return []