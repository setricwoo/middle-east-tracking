@echo off
chcp 65001
echo ==========================================
echo  推送到 GitHub
echo ==========================================
echo.

REM 请修改下面的用户名
set USERNAME=YOUR_USERNAME

if "%USERNAME%"=="YOUR_USERNAME" (
    echo 错误：请先编辑此文件，将 YOUR_USERNAME 替换为你的 GitHub 用户名！
    pause
    exit /b 1
)

echo 正在添加远程仓库...
git remote add origin https://github.com/%USERNAME%/middle-east-tracking.git

if errorlevel 1 (
    echo 远程仓库已存在，尝试更新...
    git remote set-url origin https://github.com/%USERNAME%/middle-east-tracking.git
)

echo.
echo 正在推送到 GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo 推送失败，可能原因：
    echo 1. 网络问题
    echo 2. 需要登录 GitHub 认证
    echo 3. 仓库地址错误
    echo.
    echo 如果提示需要登录，请按提示操作。
    pause
) else (
    echo.
    echo ==========================================
    echo  推送成功！
    echo ==========================================
    echo.
    echo 仓库地址：https://github.com/%USERNAME%/middle-east-tracking
    pause
)
