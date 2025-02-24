from datetime import datetime  
from .database import TaskDatabase  
from utils.logger import Logger  
import uuid  

class TaskManager:  
    def __init__(self):  
        self.logger = Logger(__name__)  
        self.db = TaskDatabase()  

    def create_task(self, name: str, task_type: str, device_id: str = None,   
                   description: str = None, priority: int = 0, params: dict = None) -> str:  
        """创建新任务"""  
        try:  
            task_id = str(uuid.uuid4())  
            
            # 插入任务基本信息  
            self.db.cursor.execute("""  
                INSERT INTO tasks (task_id, name, type, device_id, description, priority)  
                VALUES (?, ?, ?, ?, ?, ?)  
            """, (task_id, name, task_type, device_id, description, priority))  

            # 插入任务参数  
            if params:  
                param_values = [(task_id, k, str(v)) for k, v in params.items()]  
                self.db.cursor.executemany("""  
                    INSERT INTO task_params (task_id, param_name, param_value)  
                    VALUES (?, ?, ?)  
                """, param_values)  

            self.db.conn.commit()  
            self.logger.info(f"任务创建成功: {task_id}")  
            return task_id  
        except Exception as e:  
            self.logger.error(f"创建任务失败: {str(e)}")  
            return None  

    def update_task_status(self, task_id: str, status: str, progress: int = None):  
        """更新任务状态"""  
        try:  
            update_fields = ["status = ?"]  
            params = [status]  

            if progress is not None:  
                update_fields.append("progress = ?")  
                params.append(progress)  

            if status == 'running' and progress == 0:  
                update_fields.append("start_time = CURRENT_TIMESTAMP")  
            elif status in ['completed', 'failed']:  
                update_fields.append("end_time = CURRENT_TIMESTAMP")  

            query = f"""  
                UPDATE tasks   
                SET {', '.join(update_fields)}  
                WHERE task_id = ?  
            """  
            params.append(task_id)  

            self.db.cursor.execute(query, tuple(params))  
            self.db.conn.commit()  
            
            # 添加状态变更日志  
            self.add_task_log(task_id, "status_change", f"Task status changed to {status}")  
            
            self.logger.info(f"任务状态更新成功: {task_id}")  
            return True  
        except Exception as e:  
            self.logger.error(f"更新任务状态失败: {str(e)}")  
            return False  

    def get_task(self, task_id: str) -> dict:  
        """获取任务完整信息"""  
        try:  
            # 获取任务基本信息  
            task = self.db.cursor.execute("""  
                SELECT * FROM tasks WHERE task_id = ?  
            """, (task_id,)).fetchone()  

            if not task:  
                return None  

            task_dict = dict(task)  

            # 获取任务参数  
            params = self.db.cursor.execute("""  
                SELECT param_name, param_value   
                FROM task_params   
                WHERE task_id = ?  
            """, (task_id,)).fetchall()  
            
            task_dict['params'] = {row['param_name']: row['param_value'] for row in params}  

            # 获取最近的日志  
            logs = self.db.cursor.execute("""  
                SELECT * FROM task_logs   
                WHERE task_id = ?  
                ORDER BY created_at DESC  
                LIMIT 10  
            """, (task_id,)).fetchall()  
            
            task_dict['logs'] = [dict(row) for row in logs]  
            
            return task_dict  
        except Exception as e:  
            self.logger.error(f"获取任务信息失败: {str(e)}")  
            return None  

    def get_device_tasks(self, device_id: str, status: str = None) -> list:  
        """获取设备的任务列表"""  
        try:  
            query = "SELECT * FROM tasks WHERE device_id = ?"  
            params = [device_id]  

            if status:  
                query += " AND status = ?"  
                params.append(status)  

            query += " ORDER BY priority DESC, created_at DESC"  

            result = self.db.cursor.execute(query, tuple(params)).fetchall()  
            return [dict(row) for row in result]  
        except Exception as e:  
            self.logger.error(f"获取设备任务列表失败: {str(e)}")  
            return []  

    def add_task_log(self, task_id: str, log_type: str, message: str):  
        """添加任务日志"""  
        try:  
            self.db.cursor.execute("""  
                INSERT INTO task_logs (task_id, log_type, message)  
                VALUES (?, ?, ?)  
            """, (task_id, log_type, message))  
            self.db.conn.commit()  
            return True  
        except Exception as e:  
            self.logger.error(f"添加任务日志失败: {str(e)}")  
            return False  

    def get_task_logs(self, task_id: str, limit: int = 100) -> list:  
        """获取任务日志"""  
        try:  
            result = self.db.cursor.execute("""  
                SELECT * FROM task_logs   
                WHERE task_id = ?  
                ORDER BY created_at DESC  
                LIMIT ?  
            """, (task_id, limit)).fetchall()  
            return [dict(row) for row in result]  
        except Exception as e:  
            self.logger.error(f"获取任务日志失败: {str(e)}")  
            return []  

    def delete_task(self, task_id: str) -> bool:  
        """删除任务"""  
        try:  
            # 首先删除任务相关的参数和日志  
            self.db.cursor.execute("DELETE FROM task_params WHERE task_id = ?", (task_id,))  
            self.db.cursor.execute("DELETE FROM task_logs WHERE task_id = ?", (task_id,))  
            # 最后删除任务本身  
            self.db.cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))  
            
            self.db.conn.commit()  
            self.logger.info(f"任务删除成功: {task_id}")  
            return True  
        except Exception as e:  
            self.logger.error(f"删除任务失败: {str(e)}")  
            return False