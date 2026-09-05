# -*- coding: utf-8 -*-
"""从 OpenRouter 公开 API 生成离线快照 snapshot.js（页面兜底数据 + 数据刷新脚本）

用法：
  python build_snapshot.py             # 用本地缓存的 JSON 生成快照（无网络也可用）
  python build_snapshot.py --refresh   # 重新拉取最新数据并更新 snapshot.js
"""
import json, re, sys, time, urllib.request, os

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

RANK_URL = "https://openrouter.ai/api/frontend/v1/rankings/models"
META_URL = "https://openrouter.ai/api/v1/models"

DESC_KEEP = 300      # 详情描述截断长度
DESC_TOP_N = 150     # 仅为排名前 N 的模型保存描述


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def load_local_or_fetch(name, url):
    p = os.path.join(HERE, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return fetch(url)


def norm_base(sid):
    s = sid.lstrip("~")
    s = re.sub(r":\w+$", "", s)          # 去掉 :batch 等变体后缀
    s = re.sub(r"-latest$", "", s)
    return s


def base_key(sid):
    return re.sub(r"-\d{4,8}$", "", norm_base(sid))


def write_snapshot(snap):
    p = os.path.join(HERE, "snapshot.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write("// 自动生成的离线快照（OpenRouter 真实数据备份）· 生成时间 %s\n" % snap["fetchedAt"])
        f.write("window.SNAPSHOT=")
        json.dump(snap, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")


def build(rank_raw=None, meta_raw=None):
    if rank_raw is None:
        rank_raw = load_local_or_fetch("or_models.json", RANK_URL)
    if meta_raw is None:
        meta_raw = load_local_or_fetch("or_meta.json", META_URL)

    rows = rank_raw["data"]

    # ---- 排名：每个 slug 只取其最新一天的数据，聚合变体（standard/free/batch）----
    latest_by_slug = {}
    for r in rows:
        s, d = r["model_permaslug"], r["date"]
        if s not in latest_by_slug or d > latest_by_slug[s]:
            latest_by_slug[s] = d

    agg = {}
    for r in rows:
        s = r["model_permaslug"]
        if r["date"] != latest_by_slug[s]:
            continue
        a = agg.setdefault(s, {"tok": 0, "req": 0, "var": {}})
        a["tok"] += (r.get("total_prompt_tokens") or 0) + (r.get("total_completion_tokens") or 0)
        a["req"] += r.get("count") or 0
        vv = a["var"].setdefault(r.get("variant") or "standard", [0, 0])
        vv[0] += (r.get("total_prompt_tokens") or 0) + (r.get("total_completion_tokens") or 0)
        vv[1] += r.get("count") or 0

    rankings = sorted(
        ([s, a["tok"], a["req"], [[v, t[0], t[1]] for v, t in a["var"].items()]]
         for s, a in agg.items()),
        key=lambda x: -x[1])

    data_date = max(latest_by_slug.values(), default="")[:10]

    # ---- 元数据索引 ----
    metas = {}
    for m in meta_raw["data"]:
        b = norm_base(m["id"])
        cur = metas.get(b)
        if cur is None or (m.get("created") or 0) > (cur.get("created") or 0):
            metas[b] = m
    by_key = {}
    for b, m in metas.items():
        k = base_key(b)
        cur = by_key.get(k)
        if cur is None or (m.get("created") or 0) > (cur.get("created") or 0):
            by_key[k] = m

    top_slugs = set(s for s, *_ in rankings[:DESC_TOP_N])

    def meta_for(slug):
        k = re.sub(r"-\d{8}$", "", slug)
        if slug in metas:
            return metas[slug]
        if k in metas:
            return metas[k]
        return by_key.get(base_key(slug)) or by_key.get(k)

    meta_out = {}
    for s, *_ in rankings:
        m = meta_for(s)
        if not m:
            continue
        b = norm_base(m["id"])
        if b in meta_out:
            continue
        arch = m.get("architecture") or {}
        pr = m.get("pricing") or {}
        desc = ""
        if s in top_slugs:
            desc = re.sub(r"<[^>]+>|\s+", " ", m.get("description") or "").strip()[:DESC_KEEP]
        meta_out[b] = [
            m.get("name") or b,
            m.get("context_length") or 0,
            float(pr.get("prompt") or 0),
            float(pr.get("completion") or 0),
            ",".join(arch.get("input_modalities") or ["text"]),
            ",".join(arch.get("output_modalities") or ["text"]),
            m.get("created") or 0,
            desc,
        ]

    snap = {
        "date": data_date,
        "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": "openrouter",
        "rankings": rankings,
        "meta": meta_out,
    }
    write_snapshot(snap)
    return snap


def refresh():
    r = fetch(RANK_URL)
    m = fetch(META_URL)
    snap = build(r, m)
    print("snapshot.js 已更新 · 数据日期:", snap["date"], "· 模型数:", len(snap["rankings"]))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--refresh":
        refresh()
    else:
        snap = build()
        print("date:", snap["date"], "| rankings:", len(snap["rankings"]), "| meta:", len(snap["meta"]))
