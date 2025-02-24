# utils/style_manager.py  

from pathlib import Path  

class StyleManager:  
    @staticmethod  
    def load_style(style_name: str) -> str:  
        """  
        加载指定的样式表文件  
        
        Args:  
            style_name: 样式文件名(不包含.qss扩展名)  
            
        Returns:  
            str: 样式表内容  
        """  
        try:  
            style_path = Path(__file__).parent.parent / 'resources' / 'styles' / f'{style_name}.qss'  
            with open(style_path, 'r', encoding='utf-8') as f:  
                return f.read()  
        except Exception as e:  
            print(f"加载样式表失败: {e}")  
            return ""