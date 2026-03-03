import sys
import os

# 将项目根目录加入到 Python 路径，使 app 模块可被找到
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app

# Vercel 通过此变量名识别 WSGI 应用
app = create_app()
