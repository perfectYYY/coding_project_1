import asyncio  
import websockets  
from typing import Callable, Dict, Any  
from .protocols import Message, MessageType  
from utils.logger import Logger  

class DeviceClient:  
    def __init__(self, device_id: str, server_url: str = "ws://localhost:8765"):  
        self.device_id = device_id  
        self.server_url = server_url  
        self.logger = Logger(__name__)  
        self.websocket = None  
        self.connected = False  
        self.command_handlers: Dict[str, Callable] = {}  

    async def connect(self):  
        """连接到服务器"""  
        try:  
            self.websocket = await websockets.connect(self.server_url)  
            self.connected = True  
            self.logger.info(f"设备 {self.device_id} 已连接到服务器")  
            
            # 发送初始化消息  
            await self._send_status("online")  
            
            # 启动心跳包发送  
            asyncio.create_task(self._heartbeat_loop())  
            
            # 开始消息处理循环  
            await self._message_loop()  
            
        except Exception as e:  
            self.logger.error(f"连接失败: {str(e)}")  
            self.connected = False  
            raise  

    async def disconnect(self):  
        """断开连接"""  
        if self.websocket:  
            await self._send_status("offline")  
            await self.websocket.close()  
            self.connected = False  
            self.logger.info(f"设备 {self.device_id} 已断开连接")  

    async def _heartbeat_loop(self):  
        """定期发送心跳包"""  
        while self.connected:  
            try:  
                message = Message(  
                    type=MessageType.HEARTBEAT,  
                    device_id=self.device_id,  
                    payload={  
                        "battery": 100,  # 这里可以添加实际的电池状态  
                        "signal": 100    # 这里可以添加实际的信号强度  
                    }  
                )  
                await self.websocket.send(message.to_json())  
                await asyncio.sleep(30)  # 30秒发送一次心跳包  
            except Exception as e:  
                self.logger.error(f"发送心跳包失败: {str(e)}")  
                break  

    async def _message_loop(self):  
        """消息处理循环"""  
        try:  
            async for message in self.websocket:  
                try:  
                    msg = Message.from_json(message)  
                    await self._handle_message(msg)  
                except Exception as e:  
                    self.logger.error(f"消息处理错误: {str(e)}")  
        except websockets.exceptions.ConnectionClosed:  
            self.logger.info("连接已关闭")  
            self.connected = False  

    async def _handle_message(self, message: Message):  
        """处理接收到的消息"""  
        if message.type == MessageType.COMMAND:  
            command = message.payload.get("command")  
            params = message.payload.get("params", {})  
            
            handler = self.command_handlers.get(command)  
            if handler:  
                try:  
                    await handler(params)  
                except Exception as e:  
                    await self._send_error(f"命令执行失败: {str(e)}")  
            else:  
                await self._send_error(f"未知命令: {command}")  

    async def _send_status(self, status: str):  
        """发送状态消息"""  
        message = Message(  
            type=MessageType.STATUS,  
            device_id=self.device_id,  
            payload={"status": status}  
        )  
        await self.websocket.send(message.to_json())  

    async def _send_error(self, error_msg: str):  
        """发送错误消息"""  
        message = Message(  
            type=MessageType.ERROR,  
            device_id=self.device_id,  
            payload={"error": error_msg}  
        )  
        await self.websocket.send(message.to_json())  

    async def send_data(self, data: Any):  
        """发送数据到服务器"""  
        message = Message(  
            type=MessageType.DATA,  
            device_id=self.device_id,  
            payload={"data": data}  
        )  
        await self.websocket.send(message.to_json())  

    def register_command_handler(self, command: str, handler: Callable):  
        """注册命令处理器"""  
        self.command_handlers[command] = handler