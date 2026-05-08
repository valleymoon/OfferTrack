# OfferTrack · 求职追踪软件

> 一个本地运行的个人求职追踪应用，记录投递、面试时间线与面试题复盘。Windows 下作为原生桌面 app 双击运行；同时保留完整的开发模式（FastAPI + Vue），可改可扩。

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node-18+-339933?logo=node.js&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 特性

- 🖥️ **原生桌面 app**：双击 exe 即开，无黑窗、无浏览器 tab；记忆窗口大小与位置；多次双击图标自动召回已有窗口（不重复开实例）
- 📋 **投递记录**：公司 / 岗位 / JD（Markdown）/ 投递时间 / 渠道 / 备注，支持搜索与状态筛选；渠道里的 URL 可直接点开
- 📅 **灵活时间线**：按实际进展手动添加面试节点（一面/二面/HR 面/笔试…），支持自定义阶段；新增节点自动联动投递状态
- 📝 **面试题复盘**：题目 + 复盘 两段 Markdown 输入，含代码高亮，长内容不折叠
- 📊 **轻量仪表盘**：投递总数、面试中、Offer、已结束 4 项数字；近期面试提醒；疑似挂掉投递（阈值可调）
- 💾 **数据导入导出**：一键 JSON 备份；导入支持「覆盖」与「合并」两种模式
- 🔒 **本地优先**：数据全部存在本地 SQLite，不联网、不上云、不收集

## 🚀 用户使用（Windows 桌面版）

### 系统要求

- Windows 10 / 11
- WebView2 运行时（Win10 21H2+ / Win11 自带，无需单独装）

### 安装

1. 到 [Releases](https://github.com/valleymoon/OfferTrack/releases) 页下载最新的 `OfferTrack.exe`
2. 把 exe 放到任意文件夹（建议放在 `D:\Apps\OfferTrack\` 之类有写权限的位置；放到 `C:\Program Files\` 也能跑，数据会自动写到用户目录）
3. 双击运行；右键 → 发送到 → 桌面快捷方式 可放桌面

### 数据位置

| 模式 | 位置 |
|------|------|
| 默认 | `%LOCALAPPDATA%\OfferTrack\offertrack.db` |
| 便携模式 | exe 同目录建一个空文件 `portable.flag`，重启 app 后数据写到 `<exe 目录>\data\offertrack.db` |

便携模式适合放 U 盘随身携带 / 一台机器多用户隔离。换电脑时直接拷贝整个文件夹即可。

### 卸载

直接删 exe；如果想清掉数据，删 `%LOCALAPPDATA%\OfferTrack\` 目录（或便携模式下的 `data\`）。

---

## 🛠️ 开发者：从源码构建

### 环境要求

- Python 3.11+
- Node.js 18+
- Git
- 仅打包需要：Windows + PyInstaller（`build.ps1` 会自动装）

### 一键启动开发模式（前后端 + 浏览器）

**Windows**：
```powershell
.\start.ps1
```

**Mac / Linux**（仅 Web 开发模式，桌面壳是 Windows-only）：
```bash
./start.sh
```

启动脚本会建好 venv、装好依赖，然后同时启前端 + 后端：

- 前端：<http://localhost:5173>
- 后端：<http://localhost:8000>（API 文档在 `/docs`）
- 数据：项目根 `data/offertrack.db`

### 手动启动（分别控制前后端）

```powershell
# 后端
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
# 前端（另开终端）
cd frontend
npm install
npm run dev
```

### 打包成单文件 exe（Windows）

```powershell
.\build.ps1
```

流程：构建前端静态文件 → 准备后端 venv → 调 PyInstaller 把 `launcher.py` + 后端 + 前端 dist + ICO 全部塞进一个 ~22 MB 的 `dist\OfferTrack.exe`。

可选：跑 `scripts\create_shortcut.ps1` 在桌面造一个无 "- 快捷方式" 后缀、显式指向项目 ICO 的快捷方式。

### 替换图标

把新源 PNG 放到 `assets\app_source.png`（建议 1024×1024、透明底 RGBA），然后：

```powershell
backend\.venv\Scripts\python.exe scripts\build_icon.py assets\app_source.png
```

会重新生成 `assets\app.ico`（多分辨率 16/32/48/64/128 BMP + 256 PNG）。重打包 + 刷桌面图标缓存即可看到新图。

## 📂 项目结构

```
OfferTrack/
├── launcher.py                  # 桌面壳：单实例锁、uvicorn 后台、PyWebView 窗口
├── OfferTrack.spec              # PyInstaller spec
├── build.ps1                    # 打包脚本
├── start.ps1 / start.sh         # 开发模式启动脚本
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口、CORS、/api/focus
│   │   ├── database.py          # SQLite 引擎
│   │   ├── paths.py             # 可写目录解析（LOCALAPPDATA / 便携 fallback）
│   │   ├── runtime.py           # 拉前台（pywebview + Win32 兜底）
│   │   ├── models.py            # SQLModel 数据模型
│   │   ├── schemas.py           # 请求/响应 Schema
│   │   └── routers/             # applications / events / questions / dashboard / backup
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.vue              # 顶部导航 + RouterView
│       ├── router/              # 4 个路由
│       ├── views/               # Dashboard / ApplicationList / ApplicationDetail / Settings
│       ├── components/          # 表单/Modal/Markdown/LinkifiedText 等
│       └── api/                 # axios 客户端
├── assets/
│   ├── app.ico                  # 多分辨率应用图标
│   └── app_source.png           # 图标源 PNG（透明底）
├── scripts/
│   ├── build_icon.py            # 把源 PNG 转成多分辨率 ICO
│   └── create_shortcut.ps1      # 在桌面造带显式 IconLocation 的 .lnk
├── LICENSE                      # MIT
└── README.md
```

## 🛠️ 技术栈

| 层级 | 选型 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLModel |
| 数据库 | SQLite（单文件，零配置） |
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS 4 |
| Markdown | md-editor-v3（自带代码高亮） |
| 状态管理 | Pinia |
| 桌面壳 | PyWebView 5（Edge WebView2）+ pywin32 |
| 打包 | PyInstaller（单文件 exe） |

## 📋 使用流程

1. **新建投递**：在「投递记录」页点「+ 新建投递」，填公司、岗位、JD 等
2. **进入详情页**：点列表里的公司名进入投递详情
3. **添加时间线节点**：每次有进展（笔试/一面/HR 面…）点「+ 添加节点」，状态会自动联动
4. **记录面试题**：在面试类型节点下点「+ 添加面试题」，Markdown 录入题目 + 复盘
5. **查看仪表盘**：随时打开「仪表盘」看数字总览、近期要面的、疑似挂掉的
6. **备份数据**：「设置」页一键导出 JSON；换电脑同样可一键导入

## 🗺️ Roadmap

**v0.1（当前）** ✅
- 投递、时间线、面试题三层数据模型
- 仪表盘（含可调时间窗口）
- 一键导入导出
- Windows 单文件 exe 桌面应用（PyWebView）

**规划中**
- [ ] 全局题库检索（跨公司搜面试题）
- [ ] 投递趋势 / 面试转化率图表
- [ ] 面试题附件（图片/手写白板）
- [ ] 移动端响应式
- [ ] macOS 桌面打包
- [ ] 桌面通知 / 邮件提醒

## 🤝 贡献

个人开源项目，欢迎 issue / PR。

## 📄 License

[MIT](LICENSE) © 2026 OfferTrack Contributors
