import logging  
from utils.config import Config  

class Logger:  
    def __init__(self, name):  
        self.logger = logging.getLogger(name)  
        
        if not self.logger.handlers:  
            self.logger.setLevel(logging.INFO)  
            
            # 创建文件处理器  
            fh = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')  
            fh.setLevel(logging.INFO)  
            
            # 创建控制台处理器  
            ch = logging.StreamHandler()  
            ch.setLevel(logging.INFO)  
            
            # 创建格式器  
            formatter = logging.Formatter(Config.LOG_FORMAT)  
            fh.setFormatter(formatter)  
            ch.setFormatter(formatter)  
            
            # 添加处理器  
            self.logger.addHandler(fh)  
            self.logger.addHandler(ch)  
    
    def info(self, message):  
        self.logger.info(message)  
    
    def error(self, message):  
        self.logger.error(message)  
    
    def warning(self, message):  
        self.logger.warning(message)  
    
    def debug(self, message):  
        self.logger.debug(message)