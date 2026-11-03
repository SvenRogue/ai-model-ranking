# 🏆 全球大模型实时热度榜（LLM Live Rankings）

一个零依赖、单页面的大模型实时排行榜，基于 [OpenRouter](https://openrouter.ai/rankings) 平台全球开发者真实调用量（Tokens 用量 + API 请求数）统计排名。

## ✨ 功能

- **实时数据**：页面每 5 分钟自动从 OpenRouter 公开接口拉取最新用量排名（前端直连，无需任何密钥）
- **离线兜底**：接口不可达时自动回退到内置快照 `snapshot.js`，并显示提示条与重试按钮
- **热度三甲**：金银铜领奖台卡片，含用量、调用、上下文、份额
- **市场格局**：Top 10 用量条形图 + 机构份额环形图（Canvas 手绘，支持悬停明细）
- **完整榜单**：搜索（中英文/机构）、机构筛选、大语言模型 / 多模态 / 全部切换、多种排序、分页展开
- **详情抽屉**：点击任意模型查看 24h 用量、调用次数、上下文、价格（输入/输出/混合均价）、变体分布、发布日期等
- **精美 UI**：极光渐变背景、玻璃拟态卡片、数字滚动动画、粘性表头、骨架屏、Toast 提示，桌面 / 移动端自适应

## 🌐 线上地址

- **主站**：https://rank.svenrogue.top （Cloudflare Workers 静态资源 + 自定义域名）
- 备用：https://ai-model-ranking-7y8.pages.dev （Cloudflare Pages）

## 🚀 本地使用

直接**双击 `index.html`** 用浏览器打开即可（Chrome / Edge 均可），无需服务器。

> 也可以本地起服务：`python -m http.server 8000`，然后访问 http://localhost:8000

## 📁 文件

| 文件 | 说明 |
|---|---|
| `index.html` | 主页面（全部样式与逻辑内联，无外部依赖） |
| `snapshot.js` | 内置离线快照（真实数据备份，页面打开瞬间先渲染它） |
| `build_snapshot.py` | 快照生成 / 数据刷新脚本 |
| `dist/` | 部署目录（index.html + snapshot.js + README） |
| `worker/wrangler.jsonc` | Workers 部署配置（绑定 rank.svenrogue.top） |
| `deploy_worker.sh` | 一键部署到 Workers + 自定义域名 |
| `deploy_cf.sh` | 部署到 Cloudflare Pages（pages.dev） |
| `cf_api.sh` | Cloudflare API 调试辅助 |
| `or_models.json` / `or_meta.json` | 上次抓取的原始 API 数据（供离线重建快照） |

## 🔄 手动更新快照并重新部署

```bash
python build_snapshot.py --refresh    # 拉最新数据更新 snapshot.js
cp snapshot.js index.html README.md dist/   # 同步到部署目录
bash deploy_worker.sh                 # 重新部署上线（约 10 秒）
```

页面本身每 5 分钟自动从 OpenRouter 实时拉取数据，此脚本只是更新兜底快照。

## 📊 数据说明

- 数据来源：`openrouter.ai/api/frontend/v1/rankings/models`（用量排名）与 `openrouter.ai/api/v1/models`（模型元数据），两个接口均支持浏览器跨域直连
- 排名口径：每个模型取其最新一天的数据，聚合 `standard / free / batch` 等变体的 Tokens 与请求数
- 排名反映 OpenRouter 平台生态内的相对热度，不等同于全行业市场份额，仅供参考
