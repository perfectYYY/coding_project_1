class Config:  
    APP_NAME = "无人机控制系统"  
    APP_VERSION = "1.0.0"  
    
    # 数据库配置  
    DB_PATH = "data/auth.db"  
    
    # 日志配置  
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  
    LOG_FILE = "logs/app.log"  
    
    @classmethod  
    def initialize(cls):  
        """初始化配置"""  
        import os  
        
        # 创建必要的目录  
        os.makedirs("data", exist_ok=True)  
        os.makedirs("logs", exist_ok=True)