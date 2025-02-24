import asyncio  
import websockets  
from typing import Dict, Callable, Any  
from .protocols import Message, MessageType  
from utils.logger import Logger  
from core.device.manager import DeviceManager  

class CommunicationManager:  
    def __init__(self, host: str = "localhost", port: int = 8765):  
        self.logger = Logger(__name__)  
        self.host = host  
        self.port = port  
        self.device_manager = DeviceManager()  
        self.connected_devices: Dict[str, websockets.WebSocketServerProtocol] = {}  
        self.message_handlers: Dict[MessageType, Callable] = {  
            MessageType.HEARTBEAT: self._handle_heartbeat,  
            MessageType.DATA: self._handle_data,  
            MessageType.STATUS: self._handle_status,  
            MessageType.ERROR: self._handle_error,  
        }  
        self.server = None  

    async def start(self):  
        """启动WebSocket服务器"""  
        try:  
            self.server = await websockets.serve(  
                self._handle_connection,  
                self.host,  
                self.port  
            )  
            self.logger.info(f"通信服务器启动成功 - {self.host}:{self.port}")  
            await self.server.wait_closed()  
        except Exception as e:  
            self.logger.error(f"通信服务器启动失败: {str(e)}")  
            raise  

    async def stop(self):  
        """停止服务器"""  
        if self.server:  
            self.server.close()  
            await self.server.wait_closed()  
            self.logger.info("通信服务器已停止")  

    async def _handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):  
        """处理新的WebSocket连接"""  
        device_id = None  
        try:  
            # 等待设备发送身份识别消息  
            async for message in websocket:  
                try:  
                    msg = Message.from_json(message)  
                    if not device_id:  
                        # 首次连接，记录设备ID  
                        device_id = msg.device_id  
                        self.connected_devices[device_id] = websocket  
                        self.logger.info(f"设备连接成功: {device_id}")  
                        
                        # 更新设备状态为在线  
                        self.device_manager.update_device_status(device_id, "online")  
                    
                    # 处理消息  
                    await self._process_message(msg)  
                except Exception as e:  
                    self.logger.error(f"消息处理错误: {str(e)}")  
                    await self._send_error(websocket, str(e))  

        except websockets.exceptions.ConnectionClosed:  
            self.logger.info(f"设备连接断开: {device_id}")  
        finally:  
            if device_id:  
                self.connected_devices.pop(device_id, None)  
                # 更新设备状态为离线  
                self.device_manager.update_device_status(device_id, "offline")  

    async def _process_message(self, message: Message):  
        """处理接收到的消息"""  
        handler = self.message_handlers.get(message.type)  
        if handler:  
            await handler(message)  
        else:  
            self.logger.warning(f"未知的消息类型: {message.type}")  

    async def _handle_heartbeat(self, message: Message):  
        """处理心跳包"""  
        device_id = message.device_id  
        if device_id in self.connected_devices:  
            # 更新设备状态  
            self.device_manager.update_device_status(  
                device_id,  
                "online",  
                battery=message.payload.get("battery"),  
                signal=message.payload.get("signal")  
            )  

    async def _handle_data(self, message: Message):  
        """处理数据消息"""  
        device_id = message.device_id  
        # 记录数据日志  
        self.device_manager.add_device_log(  
            device_id,  
            "data",  
            f"Received data: {message.payload}"  
        )  
        # 这里可以添加数据处理逻辑  

    async def _handle_status(self, message: Message):  
        """处理状态消息"""  
        device_id = message.device_id  
        status = message.payload.get("status")  
        if status:  
            self.device_manager.update_device_status(device_id, status)  

    async def _handle_error(self, message: Message):  
        """处理错误消息"""  
        device_id = message.device_id  
        error_msg = message.payload.get("error")  
        self.device_manager.add_device_log(device_id, "error", error_msg)  

    async def _send_error(self, websocket: websockets.WebSocketServerProtocol, error_msg: str):  
        """发送错误消息"""  
        try:  
            message = Message(  
                type=MessageType.ERROR,  
                device_id="server",  
                payload={"error": error_msg}  
            )  
            await websocket.send(message.to_json())  
        except Exception as e:  
            self.logger.error(f"发送错误消息失败: {str(e)}")  

    async def send_command(self, device_id: str, command: str, params: dict = None):  
        """发送命令到设备"""  
        if device_id not in self.connected_devices:  
            raise ValueError(f"设备未连接: {device_id}")  
        
        message = Message(  
            type=MessageType.COMMAND,  
            device_id=device_id,  
            payload={  
                "command": command,  
                "params": params or {}  
            }  
        )  
        
        try:  
            await self.connected_devices[device_id].send(message.to_json())  
            self.logger.info(f"命令已发送到设备 {device_id}: {command}")  
        except Exception as e:  
            self.logger.error(f"发送命令失败: {str(e)}")  
            raise