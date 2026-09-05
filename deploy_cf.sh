#!/usr/bin/env bash
# Cloudflare Pages 部署脚本（复用 wrangler 的 OAuth 令牌）
set -e
cd "$(dirname "$0")"
CFG="$APPDATA/xdg.config/.wrangler/config/default.toml"
TOKEN=$(python - <<'PY'
import re
s = open(r'C:/Users/vanfh/AppData/Roaming/xdg.config/.wrangler/config/default.toml', encoding='utf-8').read()
m = re.search(r'oauth_token\s*=\s*"([^"]+)"', s)
print(m.group(1) if m else '')
PY
)
if [ -z "$TOKEN" ]; then echo "ERROR: 未找到 wrangler 令牌，请先运行 npx wrangler login"; exit 1; fi
export CLOUDFLARE_API_TOKEN="$TOKEN"
export CLOUDFLARE_ACCOUNT_ID="2436df498e34aef84f6add92284ef920"
npx --yes wrangler@latest pages deploy dist --project-name=ai-model-ranking --branch=main --commit-dirty=true "$@"
