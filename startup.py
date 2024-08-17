import subprocess
import shutil
import os

def copy_file(filename, path):
    if not os.path.exists(path):
        print(f"目录 {path} 不存在。")
        return
    
    dst_file = os.path.join(path, filename)
    try:
        shutil.copyfile(filename, dst_file)
        print(f"成功将 {filename} 拷贝到 {path} 并替换现有文件。")
    except FileNotFoundError:
        print(f"源文件 {filename} 不存在。")
    except PermissionError:
        print(f"没有权限写入目标路径 {path}。")
    except Exception as e:
        print(f"发生错误：{e}")

def run_streamlit_app():

    # 替换index.html文件
    copy_file("./index.html", "/www/server/pyporject_evn/dict_venv/lib/python3.12/site-packages/streamlit/static/")
    
    # 启动 streamlit 服务的命令
    command = ["streamlit", "run", "streamlit_app.py"]

    # 启动子进程
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,   # 捕获标准输出
        stderr=subprocess.PIPE,   # 捕获标准错误
        text=True,                 # 将输出作为文本处理
        bufsize=1,                 # 行缓冲模式
        universal_newlines=True    # 将输出作为新行处理
    )

    # 实时读取和输出标准输出和标准错误
    try:
        for stdout_line in iter(process.stdout.readline, ''):
            print(stdout_line, end='')  # 打印标准输出

        for stderr_line in iter(process.stderr.readline, ''):
            print(stderr_line, end='', file=sys.stderr)  # 打印标准错误
    except KeyboardInterrupt:
        # 处理用户中断（例如按 Ctrl+C）
        print("Process interrupted.")
    finally:
        process.stdout.close()
        process.stderr.close()
        process.terminate()

if __name__ == "__main__":
    run_streamlit_app()