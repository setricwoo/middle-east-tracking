#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融市场数据抓取器：
- Yahoo Finance HTTP API（商品/股票/利率/汇率）
- Treasury.gov CSV（名义收益率 + TIPS实际收益率，计算BEI）
- Economist CDN JSON（Trump支持率）
输出：market_data.json
"""

import csv
import io
import json
import os
import time
import urllib.request
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(r"D:\python_code\海湾以来-最新")
OUTPUT_FILE = WORKDIR / "market_data.json"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")
CONFLICT_START = "2026-01-07"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json,text/html,*/*",
}

# ── 指标配置 ───────────────────────────────────────────────────
COMMODITIES = {
    "BZ=F":  {"name": "Brent原油",        "unit": "USD/bbl", "group": "oil"},
    "CL=F":  {"name": "WTI原油",          "unit": "USD/bbl", "group": "oil"},
    "NG=F":  {"name": "Henry Hub天然气",   "unit": "USD/MMBtu", "group": "gas"},
    "TTF=F": {"name": "TTF欧洲天然气",     "unit": "EUR/MWh", "group": "gas"},
    "ZW=F":  {"name": "CBOT小麦",         "unit": "美分/蒲式耳", "group": "grain"},
    "ZC=F":  {"name": "CBOT玉米",         "unit": "美分/蒲式耳", "group": "grain"},
    "CF":    {"name": "CF Industries(尿素)", "unit": "USD", "group": "chem_n"},
    "NTR":   {"name": "Nutrien(钾肥)",    "unit": "USD", "group": "chem_n"},
    "OCI.AS":{"name": "OCI N.V.(甲醇)",   "unit": "EUR", "group": "chem_m"},
    "MOS":   {"name": "Mosaic(磷酸盐)",   "unit": "USD", "group": "chem_m"},
}

GSCPI_URL = "https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx"

FINANCIAL = {
    "^GSPC": {"name": "S&P 500",          "unit": "指数", "group": "equity"},
    "XLE":   {"name": "XLE能源ETF",       "unit": "USD",  "group": "equity"},
    "KSA":   {"name": "KSA沙特ETF",       "unit": "USD",  "group": "equity"},
    "PDBC":  {"name": "PDBC多商品ETF",    "unit": "USD",  "group": "equity"},
    "^TNX":  {"name": "美国10Y国债收益率", "unit": "%",    "group": "rates"},
    "^IRX":  {"name": "美国2Y国债收益率",  "unit": "%",    "group": "rates"},
    "SAR=X": {"name": "USD/SAR",          "unit": "汇率", "group": "fx"},
    "AED=X": {"name": "USD/AED",          "unit": "汇率", "group": "fx"},
    "ILS=X": {"name": "USD/ILS",          "unit": "汇率", "group": "fx"},
    "EMB":   {"name": "EMB新兴市场美元债", "unit": "USD",  "group": "credit"},
    "EMHY":  {"name": "EMHY新兴高收益债",  "unit": "USD",  "group": "credit"},
}


# ── Yahoo Finance ──────────────────────────────────────────────
def fetch_yahoo(ticker: str, retries: int = 2) -> dict | None:
    """直接 HTTP GET Yahoo Finance v8 API，返回 {dates, closes, latest}"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=90d"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = json.loads(r.read())
            result = raw["chart"]["result"][0]
            timestamps = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]
            pairs = []
            for ts, c in zip(timestamps, closes):
                if c is not None:
                    d = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
                    pairs.append([d, round(c, 4)])
            if not pairs:
                return None
            return {"hist": pairs, "latest": pairs[-1][1], "latest_date": pairs[-1][0]}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                print(f"  ERR {ticker}: {str(e)[:60]}")
                return None


# ── Treasury.gov BEI ──────────────────────────────────────────
def fetch_treasury_csv(year: int, rate_type: str) -> dict[str, float]:
    """下载 Treasury.gov 利率 CSV，返回 {date_str: rate_float}"""
    url = (
        f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
        f"daily-treasury-rates.csv/{year}/all?"
        f"type={rate_type}&field_tdr_date_value={year}&page&_format=csv"
    )
    req = urllib.request.Request(url, headers={**HEADERS, "Accept": "text/csv"})
    with urllib.request.urlopen(req, timeout=20) as r:
        content = r.read().decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if len(rows) < 2:
        return {}

    header = rows[0]
    # 名义: 10 YR 列 | TIPS: 10 YR 列（列名不同）
    target_col = None
    for i, h in enumerate(header):
        h_clean = h.strip().upper()
        if rate_type == "daily_treasury_yield_curve" and "10 YR" in h_clean:
            target_col = i
            break
        elif rate_type == "daily_treasury_real_yield_curve" and "10 YR" in h_clean:
            target_col = i
            break

    if target_col is None:
        print(f"  [警告] Treasury CSV 未找到10YR列, headers={header[:5]}")
        return {}

    result = {}
    for row in rows[1:]:
        if len(row) <= target_col:
            continue
        date_str = row[0].strip()
        val_str = row[target_col].strip()
        if date_str and val_str:
            try:
                # 日期可能是 "01/07/2026" 格式
                if "/" in date_str:
                    parts = date_str.split("/")
                    date_str = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                result[date_str] = float(val_str)
            except ValueError:
                pass
    return result


def fetch_bei() -> dict | None:
    """计算 BEI = 名义10Y - TIPS实际10Y，使用 Treasury.gov 数据"""
    try:
        current_year = datetime.now().year
        prev_year = current_year - 1

        nominal_all = {}
        tips_all = {}
        for yr in [prev_year, current_year]:
            try:
                nominal_all.update(fetch_treasury_csv(yr, "daily_treasury_yield_curve"))
            except Exception as e:
                print(f"  [警告] 名义收益率 {yr} 获取失败: {e}")
            try:
                tips_all.update(fetch_treasury_csv(yr, "daily_treasury_real_yield_curve"))
            except Exception as e:
                print(f"  [警告] TIPS {yr} 获取失败: {e}")

        common_dates = sorted(set(nominal_all) & set(tips_all))
        if not common_dates:
            return None

        # 只保留最近 90 天
        cutoff = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")
        common_dates = [d for d in common_dates if d >= cutoff]

        bei_hist = []
        for d in common_dates:
            bei = round(nominal_all[d] - tips_all[d], 4)
            bei_hist.append([d, bei])

        latest = bei_hist[-1][1] if bei_hist else None
        conflict_bei = next((v for dt, v in bei_hist if dt >= CONFLICT_START), None)
        print(f"  BEI 10Y: 当前={latest}%, 冲突前≈{conflict_bei}%")
        return {"hist": bei_hist, "latest": latest, "latest_date": common_dates[-1]}

    except Exception as e:
        print(f"  ERR BEI: {e}")
        return None


# ── Trump 支持率 ───────────────────────────────────────────────
def fetch_trump_approval() -> dict | None:
    """从 Economist CDN 获取 Trump 支持率数据，备用 FiveThirtyEight"""
    # 优先 Economist CDN
    try:
        url = "https://cdn.economist.com/interactive/trump-approval-tracker/data.json"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = json.loads(r.read())

        # Economist data format 可能是 [{date, approve, disapprove}, ...]
        # 或 {approve: [...], disapprove: [...]}
        dates, approvals, disapprovals = [], [], []
        if isinstance(raw, list):
            for item in raw:
                d = item.get("date") or item.get("t") or item.get("x")
                a = item.get("approve") or item.get("approval") or item.get("y")
                dis = item.get("disapprove") or item.get("disapproval")
                if d and a is not None:
                    dates.append(str(d)[:10])
                    approvals.append(round(float(a), 2))
                    disapprovals.append(round(float(dis), 2) if dis is not None else None)
        elif isinstance(raw, dict):
            # 尝试通用结构
            for key in ["data", "results", "values"]:
                if key in raw:
                    raw = raw[key]
                    break
            if isinstance(raw, list):
                for item in raw:
                    d = item.get("date") or item.get("t")
                    a = item.get("approve") or item.get("approval")
                    dis = item.get("disapprove") or item.get("disapproval")
                    if d and a is not None:
                        dates.append(str(d)[:10])
                        approvals.append(round(float(a), 2))
                        disapprovals.append(round(float(dis), 2) if dis else None)

        if dates:
            print(f"  Trump支持率(Economist): {len(dates)} 条, 最新={approvals[-1]}%")
            return {"source": "economist", "dates": dates, "approve": approvals, "disapprove": disapprovals}
    except Exception as e:
        print(f"  Economist CDN 失败: {e}, 尝试 FiveThirtyEight...")

    # 备用 FiveThirtyEight
    try:
        url538 = "https://projects.fivethirtyeight.com/trump-approval-data/approval_topline.csv"
        req = urllib.request.Request(url538, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        by_date: dict[str, dict] = {}
        for row in reader:
            subgrp = row.get("subgroup", "")
            if subgrp != "All polls":
                continue
            d = row.get("modeldate", "")
            if "/" in d:
                parts = d.split("/")
                d = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            approve = row.get("approve_estimate", "")
            disapprove = row.get("disapprove_estimate", "")
            if d and approve:
                by_date[d] = {"approve": float(approve), "disapprove": float(disapprove) if disapprove else None}

        # 只保留最近 90 天
        cutoff = (date.today() - timedelta(days=180)).strftime("%Y-%m-%d")
        sorted_dates = sorted(d for d in by_date if d >= cutoff)
        dates = sorted_dates
        approvals = [by_date[d]["approve"] for d in sorted_dates]
        disapprovals = [by_date[d]["disapprove"] for d in sorted_dates]

        if dates:
            print(f"  Trump支持率(538): {len(dates)} 条, 最新={approvals[-1] if approvals else 'N/A'}%")
            return {"source": "fivethirtyeight", "dates": dates, "approve": approvals, "disapprove": disapprovals}
    except Exception as e:
        print(f"  FiveThirtyEight 失败: {e}")

    return None


# ── GSCPI 全球供应链压力指数 ────────────────────────────────────
_GSCPI_MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def _parse_gscpi_date(raw: str) -> str | None:
    """'31-Jan-1998' → '1998-01'"""
    parts = str(raw).strip().split("-")
    if len(parts) == 3:
        mon = _GSCPI_MONTHS.get(parts[1].lower())
        if mon:
            return f"{parts[2]}-{mon}"
    return None


def fetch_gscpi() -> dict | None:
    """从 NY Fed 获取全球供应链压力指数（月度数据，近6年）
    文件为旧 .xls 格式，日期列格式 '31-Jan-1998'"""
    try:
        import xlrd

        req = urllib.request.Request(GSCPI_URL, headers=HEADERS)
        buf = urllib.request.urlopen(req, timeout=30).read()
        wb = xlrd.open_workbook(file_contents=buf)
        ws = wb.sheet_by_name("GSCPI Monthly Data")

        rows = []
        for i in range(ws.nrows):
            raw_date = ws.cell_value(i, 0)
            raw_val  = ws.cell_value(i, 1)
            if not raw_date or not isinstance(raw_val, (int, float)):
                continue
            d = _parse_gscpi_date(raw_date)
            if d:
                rows.append([d, round(float(raw_val), 4)])

        rows = rows[-72:]  # 近6年
        if not rows:
            return None
        latest = rows[-1][1]
        latest_date = rows[-1][0]
        print(f"  GSCPI: {len(rows)} 条, 最新={latest} ({latest_date})")
        return {"hist": rows, "latest": latest, "latest_date": latest_date}
    except Exception as e:
        print(f"  ERR GSCPI: {e}")
        return None


# ── 主函数 ─────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("金融市场数据抓取器")
    print(f"时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    os.chdir(WORKDIR)

    result = {
        "updated": datetime.now(BEIJING_TZ).strftime("%Y-%m-%dT%H:%M:%S"),
        "conflict_start": CONFLICT_START,
        "commodities": {},
        "financial": {},
        "bei": None,
        "trump_approval": None,
        "gscpi": None,
    }

    # 商品
    print("\n── 商品价格 ──")
    for ticker, meta in COMMODITIES.items():
        print(f"  {ticker} ({meta['name']})...", end="", flush=True)
        data = fetch_yahoo(ticker)
        if data:
            result["commodities"][ticker] = {**meta, **data}
            print(f" {data['latest']} {meta['unit']}")
        else:
            result["commodities"][ticker] = {**meta, "hist": [], "latest": None, "latest_date": None}
            print(" 失败")
        time.sleep(0.4)

    # 金融市场
    print("\n── 金融市场 ──")
    for ticker, meta in FINANCIAL.items():
        print(f"  {ticker} ({meta['name']})...", end="", flush=True)
        data = fetch_yahoo(ticker)
        if data:
            result["financial"][ticker] = {**meta, **data}
            print(f" {data['latest']} {meta['unit']}")
        else:
            result["financial"][ticker] = {**meta, "hist": [], "latest": None, "latest_date": None}
            print(" 失败")
        time.sleep(0.4)

    # BEI
    print("\n── 通胀预期 BEI ──")
    bei = fetch_bei()
    result["bei"] = bei or {"hist": [], "latest": None}

    # Trump 支持率
    print("\n── Trump 支持率 ──")
    trump = fetch_trump_approval()
    result["trump_approval"] = trump or {"source": None, "dates": [], "approve": [], "disapprove": []}

    # GSCPI
    print("\n── 全球供应链压力指数 GSCPI ──")
    gscpi = fetch_gscpi()
    result["gscpi"] = gscpi or {"hist": [], "latest": None, "latest_date": None}

    # 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[保存] {OUTPUT_FILE.name} 已生成")
    print("=" * 60)
    print("完成!")


if __name__ == "__main__":
    main()
