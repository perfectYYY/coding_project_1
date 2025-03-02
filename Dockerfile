# 使用Python 3.12.8作为基础镜像  
FROM python:3.12.8-slim  

# 设置工作目录  
WORKDIR /app  

# 复制依赖文件  
COPY requirements.txt .  

# 安装依赖  
RUN pip install --no-cache-dir -r requirements.txt  

# 复制项目文件到容器中  
COPY . .  

# 设置容器启动命令（请根据您的入口文件修改）  
CMD ["python", "main.py"]