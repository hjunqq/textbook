@echo off
echo 启动智慧水利平台架构与开发教材 MkDocs
echo =====================================

echo 激活虚拟环境...
call .venv\Scripts\activate

echo 启动 MkDocs 服务...
echo 请在浏览器中访问 http://127.0.0.1:8000
uv run mkdocs serve
