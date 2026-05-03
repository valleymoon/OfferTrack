# OfferTrack · 求职追踪软件

> 一个本地运行的个人求职追踪 Web 应用，记录投递、面试时间线与面试题复盘。

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node-18+-339933?logo=node.js&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-MVP-blue)

## ✨ 特性

- 📋 **投递记录**：公司 / 岗位 / JD（Markdown）/ 投递时间 / 渠道 / 备注，支持搜索与状态筛选
- 📅 **灵活时间线**：按实际进展手动添加面试节点（一面/二面/HR 面/笔试…），支持自定义阶段；新增节点自动联动投递状态
- 📝 **面试题复盘**：题目 / 我的回答 / 复盘 三段 Markdown 输入，含代码高亮，支持折叠展开与标签
- 📊 **轻量仪表盘**：投递总数、面试中、Offer、已结束 4 项数字；近期面试提醒（时间窗口可调）；疑似挂掉投递（阈值可调）
- 💾 **数据导入导出**：一键 JSON 备份；导入支持「覆盖」与「合并」两种模式
- 🔒 **本地优先**：数据全部存在本地 SQLite（`data/offertrack.db`），不联网、不上云、不收集

## 🛠️ 技术栈

| 层级 | 选型 |
|------|------|
| 后端语言 | Python 3.11+ |
| 后端框架 | FastAPI + SQLModel |
| 数据库 | SQLite（单文件，零配置） |
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 样式 | Tailwind CSS 4 |
| Markdown | md-editor-v3（自带代码高亮） |
| 状态管理 | Pinia |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Git

### 一键启动（推荐）

**Windows PowerShell**：
```powershell
.\start.ps1
```

**Mac / Linux**：
```bash
chmod +x start.sh
./start.sh
```

启动脚本会自动检查环境、首次运行时建虚拟环境并装好所有依赖，然后启动前后端。

启动完成后浏览器打开：<http://localhost:5173>

### 手动启动（如果想分别控制）

**后端**：
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows
# source .venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```
后端启动后访问 <http://localhost:8000/docs> 可看到所有 API 文档。

**前端**（另开终端）：
```powershell
cd frontend
npm install
npm run dev
```
前端访问 <http://localhost:5173>。

## 📂 项目结构

```
OfferTrack/
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # 应用入口、路由挂载、CORS
│   │   ├── database.py          # SQLite 引擎与会话依赖
│   │   ├── models.py            # SQLModel 数据模型（3 张表）
│   │   ├── schemas.py           # 请求/响应 Schema
│   │   └── routers/
│   │       ├── applications.py  # 投递 CRUD
│   │       ├── events.py        # 时间线节点 CRUD + 状态联动
│   │       ├── questions.py     # 面试题 CRUD
│   │       ├── dashboard.py     # 聚合接口（数字 + 近期面试 + 疑似挂掉）
│   │       └── backup.py        # 导入导出
│   └── requirements.txt
├── frontend/                    # Vue 3 前端
│   └── src/
│       ├── App.vue              # 顶部导航 + RouterView
│       ├── router/              # 4 个路由
│       ├── views/               # Dashboard / ApplicationList / ApplicationDetail / Settings
│       ├── components/          # FormModal、TimelineEventModal、QuestionFormModal、QuestionsSection、Markdown 封装
│       └── api/                 # axios 客户端 + 5 个 API 模块
├── data/                        # 本地 SQLite 文件（已 gitignore）
├── start.ps1 / start.sh         # 一键启动脚本
├── LICENSE                      # MIT
└── README.md
```

## 📋 使用流程

1. **新建投递**：在「投递记录」页点「+ 新建投递」，填公司、岗位、JD 等
2. **进入详情页**：点列表里的公司名进入投递详情
3. **添加时间线节点**：每次有进展（笔试/一面/HR 面…）点「+ 添加节点」，状态会自动联动
4. **记录面试题**：在面试类型节点下点「+ 添加面试题」，三段 Markdown 输入题目、回答、复盘
5. **查看仪表盘**：随时打开「仪表盘」看数字总览、近期要面的、疑似挂掉的
6. **备份数据**：「设置」页一键导出 JSON；换电脑时同样可一键导入

## 🗺️ Roadmap

**v1 (当前 MVP)** ✅
- 投递、时间线、面试题三层数据模型
- 基础仪表盘（含可调时间窗口）
- 一键导入导出
- 单人本地使用

**v2 (规划中)**
- [ ] 全局题库检索（跨公司搜面试题）
- [ ] 投递趋势 / 面试转化率图表
- [ ] 面试题附件（图片/手写白板）
- [ ] 移动端响应式
- [ ] 可选 Docker 一键部署
- [ ] 桌面通知 / 邮件提醒

## 🤝 贡献

这是个人开源项目，欢迎 issue / PR。

## 📄 License

[MIT](LICENSE) © 2026 OfferTrack Contributors
