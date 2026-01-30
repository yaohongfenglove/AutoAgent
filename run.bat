@echo off
chcp 65001 >nul
cd /d %~dp0

echo ================================
echo AutoAgent 衣服图片分析工具
echo ================================
echo.

echo [1] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [2] 运行主程序...
echo.
python main.py

echo.
echo ================================
echo 程序执行完毕
echo ================================
pause
