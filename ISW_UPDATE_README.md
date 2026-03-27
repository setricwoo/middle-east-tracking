# ISW 战局形势页面更新说明

## 功能概述

修复了 `war-situation.html` 页面的数据提取逻辑，现在正确：

1. **提取所有 ISW Key Takeaways 并翻译为中文**
2. **截取所有战场地图图表**
3. **生成中文解读标签**

## 文件说明

### 主要脚本

- **`fetch_isw_v2.py`** - 主抓取脚本
  - 从 understandingwar.org 抓取最新伊朗战事更新
  - 提取所有 Key Takeaways
  - 使用 MyMemory API 翻译为中文
  - 截取所有战场地图截图
  - 生成中文解读标签

- **`update_war_situation.py`** - 更新脚本
  - 运行 `fetch_isw_v2.py`
  - 验证截图质量
  - 输出更新摘要

- **`convert_isw_data.py`** - 数据转换脚本
  - 将 `isw_data.json` 转换为 `war-situation.html` 使用的格式

### 数据文件

- **`isw_war_data.json`** - war-situation.html 使用的数据文件
  - 最新报告标题、日期、URL
  - 5条 Key Takeaways（中英双语）
  - 12张战场地图截图路径
  - 每张地图的中文标题和解读标签
  - 3条历史记录

- **`isw_data.json`** - 完整数据备份
  - 包含所有抓取的历史数据

### 截图目录

- **`isw_screenshots/`** - 战场地图截图
  - 命名格式: `chart_YYYY-MM-DD_NN.png`
  - 每张截图约 200-700KB

## 使用方法

### 手动更新

```bash
python fetch_isw_v2.py
```

或

```bash
python update_war_situation.py
```

### 查看结果

打开 `war-situation.html` 查看更新后的战局形势页面。

## 数据格式

### isw_war_data.json 结构

```json
{
  "updated": "2026-03-25T09:38:26+08:00",
  "source_url": "https://understandingwar.org/...",
  "current_report": {
    "url": "...",
    "title": "Iran Update Special Report, March 23, 2026",
    "title_zh": "伊朗局势更新特别报告 - 2026年3月23日",
    "date": "2026-03-23",
    "takeaways": [
      {
        "en": "英文原文...",
        "zh": "中文翻译..."
      }
    ],
    "charts": [
      {
        "url": "isw_screenshots/chart_2026-03-23_00.png",
        "title": "",
        "title_zh": "美以联军在伊朗境内的军事打击",
        "context": ["美以联军行动", "军事打击", "精确打击"]
      }
    ]
  },
  "history": [...]
}
```

## 最新数据 (2026-03-23)

- **报告标题**: 伊朗局势更新特别报告 - 2026年3月23日
- **Key Takeaways**: 5 条
  1. 特朗普延长伊朗协议最后期限至3月27日
  2. 加利巴夫否认美伊谈判报道
  3. 联合部队继续空袭伊朗弹道导弹设施
  4. 伊朗决定限制对沙特袭击
  5. 真主党声称发动55次袭击
- **战场地图**: 12 张
  - 美以联军在伊朗境内的军事打击 (4张)
  - 伊朗及盟友报复性打击示意图
  - 伊朗对沙特导弹/无人机发射情况
  - 伊朗对巴林导弹/无人机发射情况
  - 伊朗对阿联酋导弹/无人机发射情况
  - 伊朗对科威特导弹发射情况
  - 真主党对以色列袭击示意图 (3张)

## 注意事项

1. 截图使用 viewport 方式截取，包含地图的完整上下文
2. 翻译使用 MyMemory API，可能存在一定延迟
3. 截图文件保存在 `isw_screenshots/` 目录，需要与 HTML 文件一起部署
