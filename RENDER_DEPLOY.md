# Render 部署指南（免费）

## 步骤 1：注册 Render 账号
访问 https://render.com 使用 GitHub 账号登录

## 步骤 2：创建 Web Service
1. 点击 Dashboard 右上角 **New** → **Web Service**
2. 选择 **Build and deploy from a Git repository**
3. 连接 GitHub 仓库 `youngyang1113/tutor_platform`

## 步骤 3：配置应用
填写以下信息：

| 字段 | 值 |
|------|-----|
| Name | `tutor-platform` |
| Region | `Singapore` (离中国最近) |
| Branch | `master` |
| Runtime | `Python` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn run:app` |
| Instance Type | `Free` |

## 步骤 4：添加环境变量
点击 **Environment** 标签，添加：

```
SECRET_KEY = yuanbo-jiajiao-2024-secret
ADMIN_PASSWORD = admin123
```

## 步骤 5：部署
点击 **Create Web Service**，等待 2-3 分钟部署完成

## 步骤 6：初始化数据库
部署完成后，在 Render 的 **Shell** 中执行：
```bash
python seed_data.py
```

## 访问应用
Render 会分配一个免费域名，格式为：`https://tutor-platform.onrender.com`

## 注意事项
- 免费方案在 15 分钟无请求后会休眠，首次访问需等待 30 秒冷启动
- 每月 750 小时免费额度，足够个人使用
