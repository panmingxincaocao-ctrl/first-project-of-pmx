# 网校系统示例实现

本仓库提供网校系统的前后端代码示例与数据库设计。

## 目录结构

- `backend/` Flask + SQLAlchemy 后端
- `frontend/` 简易前端页面
- `database/` 数据库建表脚本
- `docs/` 系统设计说明

## 快速启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.app
```

## 前端预览

直接打开 `frontend/index.html`，并确保后端运行在 `http://localhost:8000`。
