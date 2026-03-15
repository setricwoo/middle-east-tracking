@echo off
chcp 65001
echo ==========================================
echo  GitHub 连接诊断工具
echo ==========================================
echo.

echo [1/4] 检查网络连接...
ping github.com -n 3
echo.

echo [2/4] 检查Git配置...
echo 当前远程仓库地址：
git remote -v
echo.
echo 当前代理设置：
git config --global --get http.proxy 2>nul || echo   http.proxy: 未设置
git config --global --get https.proxy 2>nul || echo   https.proxy: 未设置
echo.

echo [3/4] 测试GitHub HTTPS连接...
curl -I --connect-timeout 10 https://github.com 2>nul && echo GitHub HTTPS 可访问 || echo GitHub HTTPS 连接失败
echo.

echo [4/4] 测试Git推送（干运行）...
git push --dry-run origin main 2>&1 | findstr /C:"Everything up-to-date" >nul && echo Git推送测试: 正常 || echo Git推送测试: 可能存在问题
echo.

echo ==========================================
echo 诊断完成！
echo ==========================================
echo.
echo 解决方案：
echo   1. 如果有代理软件(Clash/v2rayN等)，运行 setup_github_proxy.bat 配置代理
echo   2. 或者改用SSH方式连接（参考switch_to_ssh.bat）
echo   3. 如果没有代理，可尝试多次重试，脚本已内置重试机制
echo.
pause
