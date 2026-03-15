@echo off
chcp 65001
echo ==========================================
echo  GitHub 代理配置工具
echo ==========================================
echo.
echo 说明：国内网络访问GitHub不稳定，配置代理可提高成功率
echo.
echo 请选择代理类型：
echo   1. Clash (默认端口 7890)
echo   2. v2rayN (默认端口 10808)
echo   3. 自定义代理
echo   4. 取消代理设置
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 正在配置 Clash 代理 (127.0.0.1:7890)...
    git config --global http.proxy http://127.0.0.1:7890
    git config --global https.proxy http://127.0.0.1:7890
    echo 配置完成！
)

if "%choice%"=="2" (
    echo.
    echo 正在配置 v2rayN 代理 (127.0.0.1:10808)...
    git config --global http.proxy http://127.0.0.1:10808
    git config --global https.proxy http://127.0.0.1:10808
    echo 配置完成！
)

if "%choice%"=="3" (
    echo.
    set /p proxy_addr="请输入代理地址 (如 127.0.0.1:7890): "
    git config --global http.proxy http://%proxy_addr%
    git config --global https.proxy http://%proxy_addr%
    echo 配置完成！
)

if "%choice%"=="4" (
    echo.
    echo 正在取消代理设置...
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    echo 代理已取消！
)

echo.
echo 当前Git代理设置：
git config --global --get http.proxy
git config --global --get https.proxy
echo.
pause
