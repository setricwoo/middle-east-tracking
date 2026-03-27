# 全球流动性指标 - 免费数据获取指南

## ✅ 已验证可用的指标

### 1. 金融条件指数 (FRED API)
| 指标 | Series ID | 说明 | 更新频率 |
|------|-----------|------|----------|
| **美国金融条件指数** | `NFCI` | 芝加哥联储编制，负值表示宽松 | 周度 |
| **国家金融条件指数** | `ANFCI` | 调整后版本，更敏感 | 周度 |

### 2. 波动率指标 (FRED + Yahoo Finance)
| 指标 | 数据源 | 代码 | 说明 |
|------|--------|------|------|
| **VIX** | FRED | `VIXCLS` | 美股恐慌指数 |
| **VIX** | Yahoo | `^VIX` | 实时数据 |
| **黄金波动率** | Yahoo | `^GVZ` | GVZ Index |
| **原油波动率** | Yahoo | `^OVX` | OVX Index |

### 3. 信用利差 (FRED API)
| 指标 | Series ID | 说明 | 最新值参考 |
|------|-----------|------|------------|
| **投资级 OAS** | `BAMLC0A0CM` | 美银美林投资级利差 | 0.90% |
| **高收益 OAS** | `BAMLH0A0HYM2` | 垃圾债利差 | 3.27% |
| **EM 公司债 OAS** | `BAMLEMFSFCRPITRIV` | 新兴市场公司债 | 536.55bp |
| **BAA-AAA 利差** | 计算值 | DBAA - DAAA | ~0.54% |
| **商业票据利差** | `DPCREDIT` | 商业票据信用利差 | 3.75% |

### 4. 利率与曲线 (FRED API)
| 指标 | Series ID | 说明 |
|------|-----------|------|
| **10年期国债** | `DGS10` | 基准利率 |
| **2年期国债** | `DGS2` | 短期利率预期 |
| **3个月国库券** | `DTB3` | 短期无风险利率 |
| **SOFR** | `SOFR` | 担保隔夜融资利率 |
| **收益率曲线** | `T10Y2Y` | 10Y-2Y 利差 |
| **期限溢价** | `T10Y3M` | 10Y-3M 利差 |

### 5. 汇率 (FRED API)
| 货币对 | Series ID | 说明 |
|--------|-----------|------|
| **EUR/USD** | `DEXUSEU` | 欧元兑美元 |
| **USD/JPY** | `DEXJPUS` | 美元兑日元 |
| **美元指数** | Yahoo `DX-Y.NYB` | 综合汇率指标 |

## 📊 OIS 数据 (Overnight Index Swaps)

### 方案1: MacroMicro (推荐)

从 [MacroMicro](https://en.macromicro.me/collections/9/us-market-relative/115044/us-overnight-indexed-swaps) 获取完整的 OIS 期限结构数据。

**获取方式**: Playwright 自动抓取
**数据内容**:
| 期限 | 当前利率 (示例) |
|------|----------------|
| 1 Month | 3.677% |
| 3 Months | 3.703% |
| 6 Months | 3.7217% |
| 1 Year | 3.7386% |
| 2 Years | 3.6401% |
| 10 Years | 3.7972% |
| 30 Years | 4.0348% |

**历史数据**: 从 2007年至今

**自动更新**: `.github/workflows/oisfetch.yml` (每6小时)

**脚本**: `fetch_ois_from_macromicro.py`

---

### 方案2: FRED 代理 (备用)

如果 MacroMicro 无法访问，使用 FRED 代理：

| 利差 | 数据来源 | Series ID | 计算公式 |
|------|----------|-----------|----------|
| **SOFR-OIS** | FRED | `SOFR` - `EFFR` | SOFR - Effective Fed Funds Rate |

**说明：**
- **EFFR** 作为 OIS 的代理，因为 OIS 利率通常与 Fed Funds 利率高度相关
- 正常情况下，SOFR-EFFR 利差应在 **±10bp** 范围内
- 危机期间（如 2008、2020），该利差可能扩大至 **50-100bp**

**解读：**
- 利差 > 0：SOFR > OIS，无担保融资成本上升，流动性紧张
- 利差 < 0：SOFR < OIS，流动性宽松
- 绝对值 > 10bp：值得关注
- 绝对值 > 50bp：流动性危机信号

## ❌ 不可用的指标

| 指标 | 原因 | 替代方案 |
|------|------|----------|
| **TED Spread** | 2022年后停止更新 | 使用 `DPCREDIT` 商业票据利差 |
| **FRA-OIS** | FRED无直接数据 | 使用 SOFR 利率 |
| **3M LIBOR** | 2023年6月停用 | 使用 `SOFR` (隔夜利率) |
| **EMBIG主权债** | 需付费订阅 | 使用 `BAMLEMFSFCRPITRIV` EM公司债 |
| **OIS Swap Rate** | FRED无直接数据 | ✅ 使用 SOFR - EFFR 作为代理 (已实现) |
| **欧洲/日韩股市波动率** | VSTOXX/VXJ 不可用 | 使用本地指数 VIX |

## 🔧 GitHub Actions 配置

```yaml
# .github/workflows/liquidity.yml
name: Update Liquidity Data

on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Fetch Data
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
        run: python fetch_liquidity_data.py
      
      - name: Commit
        run: |
          git config user.name "GitHub Action"
          git config user.email "action@github.com"
          git add liquidity_data.json
          git diff --quiet && git diff --staged --quiet || git commit -m "Update liquidity data"
          git push
```

## 📊 推荐的核心指标组合

对于中东局势下的全球流动性跟踪，建议使用以下**8个核心指标**：

1. **NFCI** - 综合金融条件
2. **VIX** - 美股恐慌指数  
3. **高收益债利差 (BAMLH0A0HYM2)** - 信用风险
4. **收益率曲线 (T10Y2Y)** - 衰退预期
5. **SOFR** - 美元流动性
6. **商业票据利差 (DPCREDIT)** - 短期信用
7. **EM公司债利差** - 新兴市场风险
8. **黄金价格** - 终极避险资产

这些指标可以全面反映：
- 整体金融环境松紧
- 市场风险偏好
- 信用风险水平
- 美元流动性状况
- 地缘政治避险情绪
