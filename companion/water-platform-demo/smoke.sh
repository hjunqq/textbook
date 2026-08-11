#!/usr/bin/env bash
# 冒烟测试：一条命令验证"启动—登录—取数—拒绝"四个环节。
# 用法：./smoke.sh   （需先 cp secrets/*.example 为正式文件并 docker compose up -d --build）
set -euo pipefail
BASE="${BASE:-http://localhost:8080}"
API="${API:-http://localhost:8080}"   # 生产同源；本机联调可设 API=http://localhost:8081 等

echo "[1/5] 等待后端就绪 ..."
for i in $(seq 1 60); do
  if curl -fsS "$BASE/readyz" | grep -q UP; then break; fi
  sleep 5; [ "$i" = 60 ] && { echo "后端未就绪"; exit 1; }
done

echo "[2/5] 未带令牌访问业务接口应为 401 ..."
code=$(curl -s -o /dev/null -w '%{http_code}' "$API/api/assets")
[ "$code" = 401 ] || { echo "预期 401，实际 $code"; exit 1; }

echo "[3/5] 登录取令牌 ..."
token=$(curl -fsS -X POST "$API/api/auth/login" -H 'Content-Type: application/json' \
  -d '{"username":"duty01","password":"duty123"}' | python3 -c 'import json,sys;print(json.load(sys.stdin)["accessToken"])')
[ -n "$token" ]

echo "[4/5] 带令牌查询测点与观测 ..."
curl -fsS -H "Authorization: Bearer $token" "$API/api/assets" | grep -q 'DAM-A-PZ-07'
from=$(date -u -d '2 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-2H +%Y-%m-%dT%H:%M:%SZ)
to=$(date -u +%Y-%m-%dT%H:%M:%SZ)
curl -fsS -H "Authorization: Bearer $token" \
  "$API/api/assets/DAM-A-PZ-07/readings?from=$from&to=$to" | grep -q 'SEED-PZ07'

echo "[5/5] 错误口令应为 401 ..."
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$API/api/auth/login" \
  -H 'Content-Type: application/json' -d '{"username":"duty01","password":"wrong"}')
[ "$code" = 401 ] || { echo "预期 401，实际 $code"; exit 1; }

echo "冒烟测试全部通过 ✔"
