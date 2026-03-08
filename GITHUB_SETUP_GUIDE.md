# GitHub + Netlify 自动部署设置指南

## ✅ 已完成步骤

### 1. Git 仓库初始化 ✓
- 已在本地初始化 Git 仓库
- 创建了 .gitignore 文件（排除了 Python 脚本和临时文件）
- 已提交初始版本

## 📋 剩余步骤

### 步骤 1：创建 GitHub 仓库

1. 打开 https://github.com/new
2. 填写信息：
   - **Repository name**: `middle-east-tracking`（建议）
   - **Description**: 华泰固收中东地缘跟踪系统
   - 选择 **Public**
   - **不要勾选** "Add a README file"
3. 点击 **Create repository**

### 步骤 2：推送代码到 GitHub

创建仓库后，GitHub 会显示以下命令，**在 PowerShell 中执行**（替换你的用户名）：

```bash
git remote add origin https://github.com/YOUR_USERNAME/middle-east-tracking.git
git branch -M main
git push -u origin main
```

> 首次推送会要求登录 GitHub，按提示操作即可。

### 步骤 3：连接 Netlify

1. 登录 https://app.netlify.com/
2. 点击 **Add new site** → **Import an existing project**
3. 选择 **GitHub**，授权访问
4. 找到你刚创建的仓库 `middle-east-tracking`
5. 配置：
   - **Branch to deploy**: `main`
   - **Build command**: （留空，因为是纯静态 HTML）
   - **Publish directory**: `.` （根目录）
6. 点击 **Deploy site**

等待部署完成，Netlify 会给你一个网址（如 `https://middle-east-tracking-xxx.netlify.app`）

## 🔄 后续更新操作

以后每次更新网页后，只需执行：

```bash
git add .
git commit -m "更新说明"
git push
```

Netlify 会自动重新部署！

## 📝 常用 Git 命令参考

```bash
# 查看状态
git status

# 查看修改内容
git diff

# 添加所有修改
git add .

# 提交（带说明）
git commit -m "更新简报内容"

# 推送到 GitHub（自动触发 Netlify 部署）
git push

# 查看提交历史
git log --oneline
```

## ⚠️ 注意事项

1. **config.json 中的 API 密钥**：确保不要包含敏感信息，或将其添加到 .gitignore
2. **大文件**：PDF 文件如果太大（>50MB），可能需要使用 Git LFS
3. **自动更新脚本**：`update_briefing_grok.py` 等脚本留在本地运行，不要上传密钥
