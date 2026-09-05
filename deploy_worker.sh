#!/usr/bin/env bash
# 通过 Workers 静态资源部署并绑定自定义域名（复用 wrangler OAuth 令牌）
set -e
cd "$(dirname "$0")/worker"
TOKEN=$(python - <<'PY'
import re
s = open(r'C:/Users/vanfh/AppData/Roaming/xdg.config/.wrangler/config/default.toml', encoding='utf-8').read()
m = re.search(r'oauth_token\s*=\s*"([^"]+)"', s)
print(m.group(1) if m else '')
PY
)
if [ -z "$TOKEN" ]; then echo "ERROR: 未找到 wrangler 令牌"; exit 1; fi
export CLOUDFLARE_API_TOKEN="$TOKEN"
export CLOUDFLARE_ACCOUNT_ID="2436df498e34aef84f6add92284ef920"
npx --yes wrangler@latest deploy "$@"
