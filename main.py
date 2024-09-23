from . import create_app  # 导入创建应用的函数

app = create_app('Ai_teacher.config.Config')  # 提供配置类路径，创建 Flask 应用实例

if __name__ == '__main__':  # 当直接运行此脚本时
    app.run(debug=True)  # 启动 Flask 应用，开启调试模式
