#!/bin/bash
 
# 容器名称和镜像名称
CONTAINER_NAME="ubuntu20.04_pyqt5_container"
IMAGE_NAME="ubuntu20.04_pyqt5"
REMOTE_IMAGE="yxb111/pyqt:latest"
 
# 获取Dockerfile所在目录的上一级目录
# 获取脚本所在目录的父目录
HOST_PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
 
# 检查传入的参数是否为空
if [ -z "$1" ]; then
    echo "请提供一个操作参数：start、stop 或 build"
    exit 1
fi
 
# 检查本地是否存在镜像
check_image() {
    if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo "本地未找到镜像 $IMAGE_NAME，正在从远程仓库拉取..."
        sudo docker pull "$REMOTE_IMAGE"
        # 将拉取的镜像重新标记为本地镜像名称
        docker tag "$REMOTE_IMAGE" "$IMAGE_NAME"
    fi
}
 
# 启动容器的函数
start_container() {
    # 检查本地是否有该镜像
    check_image
 
    # 检查容器是否已存在
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        # 检查容器是否已在运行
        if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
            echo "容器 $CONTAINER_NAME 已在运行中，进入容器终端..."
            docker exec -it "$CONTAINER_NAME" /bin/bash
        else
            echo "启动已有容器 $CONTAINER_NAME，并挂载 $HOST_PARENT_DIR 到 /app..."
            docker start "$CONTAINER_NAME"
            docker exec -it "$CONTAINER_NAME" /bin/bash
        fi
    else
        # 若容器不存在，则创建并启动新容器，挂载主机目录到容器内的 /app
        echo "创建并启动新容器 $CONTAINER_NAME，并挂载 $HOST_PARENT_DIR 到 /app..."
 
        # 设置 DISPLAY 环境变量和挂载 X11 套接字
        if [ -n "$DISPLAY" ]; then
            echo "DISPLAY=$DISPLAY"
            docker run -it --name "$CONTAINER_NAME" \
                -e DISPLAY=$DISPLAY \
                -v /tmp/.X11-unix:/tmp/.X11-unix \
                -v "$HOST_PARENT_DIR":/app "$IMAGE_NAME" /bin/bash
        else
            echo "DISPLAY 未定义，跳过 X11 套接字挂载。"
            docker run -it --name "$CONTAINER_NAME" \
                -v "$HOST_PARENT_DIR":/app "$IMAGE_NAME" /bin/bash
        fi
    fi
}
 
# 停止容器的函数
stop_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "停止容器 $CONTAINER_NAME..."
        docker stop "$CONTAINER_NAME"
        echo "容器 $CONTAINER_NAME 已停止。"
    else
        echo "容器 $CONTAINER_NAME 当前未在运行。"
    fi
}
 
# 打包容器为新镜像的函数
build_image() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        if [ -n "$2" ]; then
            NEW_IMAGE_NAME="$2"
        else
            TIMESTAMP=$(date +%Y%m%d_%H%M%S)
            NEW_IMAGE_NAME="${IMAGE_NAME}_${TIMESTAMP}"
            echo "未提供新镜像名称，使用默认命名: $NEW_IMAGE_NAME"
        fi
        echo "将容器 $CONTAINER_NAME 打包为镜像 $NEW_IMAGE_NAME..."
        docker commit "$CONTAINER_NAME" "$NEW_IMAGE_NAME"
        echo "新镜像 $NEW_IMAGE_NAME 已创建。"
    else
        echo "容器 $CONTAINER_NAME 未在运行，无法打包镜像。请先启动容器。"
        exit 1
    fi
}
 
# 根据参数执行相应的操作
case "$1" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    build)
        build_image "$@"
        ;;
    *)
        echo "无效操作。请使用 'start'、'stop' 或 'build' 参数。"
        exit 1
        ;;
esac