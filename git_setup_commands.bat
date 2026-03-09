@echo off
chcp 65001
echo 请在创建 GitHub 仓库后，复制并执行以下命令：
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
echo git branch -M main
echo git push -u origin main
echo.
echo 替换 YOUR_USERNAME 和 YOUR_REPO_NAME 为你实际的用户名和仓库名
pause
