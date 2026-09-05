#!/usr/bin/env bash
# Cloudflare API 辅助：用法 cf_api.sh GET /path  或  cf_api.sh POST /path '{"json":...}'
set -e
TOKEN=$(python - <<'PY'
import re
s = open(r'C:/Users/vanfh/AppData/Roaming/xdg.config/.wrangler/config/default.toml', encoding='utf-8').read()
m = re.search(r'oauth_token\s*=\s*"([^"]+)"', s)
print(m.group(1) if m else '')
PY
)
ACC="2436df498e34aef84f6add92284ef920"
METHOD="$1"; PATH_="$2"; DATA="${3:-}"
if [ "$METHOD" = "GET" ]; then
  curl -s -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "https://api.cloudflare.com/client/v4${PATH_/\{acc\}/$ACC}"
else
  curl -s -X "$METHOD" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$DATA" "https://api.cloudflare.com/client/v4${PATH_/\{acc\}/$ACC}"
fi
