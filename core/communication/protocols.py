from enum import Enum  
from dataclasses import dataclass  
from datetime import datetime  
import json  

class MessageType(Enum):  
    """消息类型枚举"""  
    HEARTBEAT = "heartbeat"          # 心跳包  
    COMMAND = "command"              # 命令  
    DATA = "data"                    # 数据  
    STATUS = "status"                # 状态  
    ERROR = "error"                  # 错误  
    RESPONSE = "response"            # 响应  

@dataclass  
class Message:  
    """通信消息基类"""  
    type: MessageType  
    device_id: str  
    timestamp: datetime = None  
    payload: dict = None  

    def __post_init__(self):  
        if self.timestamp is None:  
            self.timestamp = datetime.now()  
        if self.payload is None:  
            self.payload = {}  

    def to_json(self) -> str:  
        """转换为JSON字符串"""  
        data = {  
            "type": self.type.value,  
            "device_id": self.device_id,  
            "timestamp": self.timestamp.isoformat(),  
            "payload": self.payload  
        }  
        return json.dumps(data)  

    @classmethod  
    def from_json(cls, json_str: str) -> 'Message':  
        """从JSON字符串创建消息对象"""  
        data = json.loads(json_str)  
        return cls(  
            type=MessageType(data["type"]),  
            device_id=data["device_id"],  
            timestamp=datetime.fromisoformat(data["timestamp"]),  
            payload=data["payload"]  
        )