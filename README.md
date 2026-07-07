# AI JD简历适配系统

本地私有化AI JD简历适配系统 — 智能解析、简历定制、Boss直聘自动投递

## 核心功能

| 模块 | 功能 |
|------|------|
| 📂 个人素材库 | PDF/Word简历解析入库、经历STAR量化、标签管理 |
| 📄 JD智能解析 | 岗位能力拆解、权重打分、能力缺口报告 |
| 📝 简历生成 | 岗位定制化简历、ATS标准PDF导出、实时预览 |
| 🎯 招呼语生成 | 应届生/社招双风格、一对一定制 |
| 🔍 Boss岗位检索 | 按城市/薪资/岗位搜索、0-100匹配度打分 |
| 📬 投递管理 | 手动单投/批量投递、严格风控策略 |
| 📊 数据看板 | 投递记录、已读/回复统计 |

## 技术栈

- **前端**: Vue3 + Vite + Element Plus + Pinia
- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **AI**: Ollama 本地大模型（支持 Qwen2.5/Llama3 等）
- **自动化**: Selenium + Chrome 可视化操作

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Chrome 浏览器
- Ollama（可选，推荐 qwen2.5:7b）

### 一键启动

```bash
scripts\start.bat
```

### 手动部署

详见 [部署文档](docs/部署文档.md)

## 安全说明

- ✅ 所有数据本地SQLite存储，不上传云端
- ✅ AI仅做STAR量化、关键词包装，不虚构经历
- ✅ 投递默认关闭全自动，需开启审核开关
- ✅ 严格风控：可视化浏览器、随机间隔、每日限制

## 项目结构

```
ai-jd-resume/
├── backend/          # Python FastAPI 后端
│   ├── app/
│   │   ├── models/   # 数据库模型
│   │   ├── schemas/  # Pydantic 数据模型
│   │   ├── routers/  # API 路由
│   │   ├── services/ # 业务逻辑
│   │   └── utils/    # 工具类(Ollama/Selenium/文件解析)
│   └── requirements.txt
├── frontend/         # Vue3 前端
│   └── src/
│       ├── views/    # 页面组件
│       ├── api/      # API客户端
│       ├── router/   # 路由配置
│       └── store/    # 状态管理
├── scripts/          # 启动脚本
└── docs/             # 文档
```

## 操作流程

1. **素材准备** → 上传简历/AI解析入库
2. **JD解析** → 添加岗位描述/AI能力拆解
3. **简历生成** → 一键生成/导出PDF/招呼语
4. **Boss检索** → 启动浏览器/搜索岗位/匹配打分
5. **投递执行** → 单投/批量（需开启审核）
