ARG BUILDER=ubuntu  
   
FROM ubuntu:20.04  
   
ARG BUILDER  
   
# 设置时区和前端  
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt install -y tzdata \
    && rm -rf /var/lib/apt/lists/*  
   
# 添加图形界面和 X11 相关依赖  
RUN apt-get update && apt-get install -y \
        build-essential \
        locales \
        python3 \
        python3-pip \
        libxml2-dev \
        libxml2-utils \
        libxslt1-dev \
        zlib1g-dev \
        net-tools \
        wget \
        # 新增的图形界面依赖  
        x11-apps \
        libgl1-mesa-glx \
        libxcb-xinerama0 \
        libxkbcommon-x11-0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shape0 \
    && rm -rf /var/lib/apt/lists/*  
   
# 原有的安装步骤保持不变  
RUN apt-get update && apt-get install -y gcc g++ cmake make autoconf automake libtool vim git sudo tree unzip \
    python3-lxml python3-jinja2 \
    libmount-dev pkg-config libsqlite3-dev libcgroup-dev libbz2-dev pkg-config libpcre3-dev libsqlite3-dev libcgroup-dev \
    && rm -rf /var/lib/apt/lists/*  
   
RUN apt-get update && apt-get install -y python-dev python-lxml python-jinja2 \
    && rm -rf /var/lib/apt/lists/*  
   
# PyCharm 安装保持不变  
ARG PYCHARM_VERSION=2024.3.4  
RUN wget -q https://download.jetbrains.com/python/pycharm-community-${PYCHARM_VERSION}.tar.gz -O /tmp/pycharm.tar.gz \
    && tar -xzf /tmp/pycharm.tar.gz -C /opt/ \
    && mv /opt/pycharm-* /opt/pycharm \
    && rm /tmp/pycharm.tar.gz \
    && chmod +x /opt/pycharm/bin/pycharm.sh  
   
# 创建用户  
RUN useradd --create-home --no-log-init --shell /bin/bash ${BUILDER} && \
	sudo echo ${BUILDER}:${BUILDER} | chpasswd && \
	sudo usermod -aG sudo ${BUILDER}  
   
WORKDIR /home/${BUILDER}  
USER ${BUILDER}  
   
# 安装 Python GUI 依赖  
RUN pip3 install PyQt5 PyQtWebEngine  

# 设置 DISPLAY 环境变量  
ENV DISPLAY=:0  

COPY ../ /home/${BUILDER}