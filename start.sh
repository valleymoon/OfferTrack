#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== OfferTrack 启动 ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "[X] 未检测到 Python，请先安装 Python 3.11+"
    exit 1
fi
if ! command -v node >/dev/null 2>&1; then
    echo "[X] 未检测到 Node.js，请先安装 Node.js 18+"
    exit 1
fi
echo "[OK] Python: $(python3 --version)"
echo "[OK] Node: $(node --version)"

if [ ! -d "$ROOT/backend/.venv" ]; then
    echo "-> 首次运行：创建后端虚拟环境..."
    cd "$ROOT/backend"
    python3 -m venv .venv
    echo "-> 安装后端依赖..."
    .venv/bin/pip install --upgrade pip --quiet
    .venv/bin/pip install -r requirements.txt
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "-> 首次运行：安装前端依赖（可能耗时 1~2 分钟）..."
    cd "$ROOT/frontend"
    npm install
fi

echo "-> 启动后端 (http://localhost:8000)..."
cd "$ROOT/backend"
.venv/bin/uvicorn app.main:app --reload &
BACKEND_PID=$!

echo "-> 启动前端 (http://localhost:5173)..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "-> 停止服务..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup EXIT INT TERM

echo ""
echo "[OK] 启动完成！浏览器打开 http://localhost:5173"
echo "    停止服务：在此终端按 Ctrl+C"
wait
