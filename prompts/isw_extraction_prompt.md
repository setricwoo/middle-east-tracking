# ISW 伊朗局势报告提取 Prompt

## 任务目标
从 Institute for the Study of War (ISW) 网站提取最新的 Iran Update Special Report，包括全文翻译和所有图表提取。

## 报告URL格式
```
https://understandingwar.org/backgrounder/iran-update-special-report-{月份}-{日期}-{年份}
```
例如：
- https://understandingwar.org/backgrounder/iran-update-special-report-march-29-2026
- https://understandingwar.org/backgrounder/iran-update-march-30-2026

如果日期不确定，先访问 https://understandingwar.org/backgrounder/iran-updates 查找最新报告链接。

---

## 重要说明

**本任务的所有工作必须由AI直接完成，禁止调用任何自动化脚本或外部工具：**

- ❌ 禁止使用 Python 脚本提取内容
- ❌ 禁止使用自动化工具抓取网页
- ❌ 禁止使用批量翻译API

- ✅ **必须由AI直接阅读页面内容**
- ✅ **必须由AI直接进行翻译**
- ✅ **必须由AI直接识别和描述图片**
- ✅ **所有配文解读必须由AI根据原文手动撰写**

---

## 执行步骤

### 步骤1：访问报告页面（AI直接操作浏览器）
1. AI 使用浏览器工具访问ISW报告页面
2. 等待页面完全加载（包含所有图片和图表）
3. 确认页面包含 "Key Takeaways" 部分

### 步骤2：提取并翻译 Key Takeaways（AI手动完成）
1. **定位**：AI 直接阅读页面，找到 "Key Takeaways" 或 "Key Developments" 部分
2. **全量提取**：AI **手动复制**每一条 Takeaway 的完整英文原文（逐条阅读，不要截断）
3. **逐条翻译**：AI **直接翻译**每条 Takeaway 成中文，保持专业术语准确

**注意**：这一步必须由AI直接阅读和翻译，不能使用任何提取脚本
4. **格式要求**：
   - 保留原文的编号（1、2、3...）
   - 中文翻译放在英文原文下方
   - 专有名词（人名、地名、组织名）保留英文并在括号中注明

**示例格式**：
```
1. [英文原文完整内容]
   【中文翻译】[翻译内容，保持专业准确]

2. [英文原文完整内容]
   【中文翻译】[翻译内容]
```

### 步骤3：提取所有图表和地图（AI手动截图）
1. **全量识别**：AI 手动滚动页面，**逐个查看并识别**所有图片元素，包括：
   - 数据图表（柱状图、折线图、饼图等）
   - 地理地图（战场态势图、袭击位置图等）
   - 信息图表（流程图、组织结构图等）
   - 卫星图像

2. **AI手动截图**：
   - AI 使用截图工具**逐张截取**每张图片
   - 确保图片清晰、完整，包含所有图例和标注
   - 保存格式：PNG
   - 命名格式：`chart_{YYYYMMDD}_{序号:02d}.png`

3. **图表信息记录**（AI手动记录）：
   - 原始图片URL（AI从浏览器地址栏或img标签复制）
   - 图片在报告中的顺序编号

**注意**：这一步必须由AI手动截图，禁止使用任何自动下载或批量截图脚本

### 步骤4：为每个图表生成解读（AI手动撰写）
对于每个提取的图表，AI 必须**手动阅读报告原文**并撰写解读：

1. **标题翻译/生成**（AI直接完成）：
   - AI 查看图表中的英文标题，**直接翻译**成中文
   - 如果没有标题，AI 根据图表内容**手动生成**简洁中文标题

2. **内容解读**（AI必须基于原文手动撰写）：
   - AI **手动在报告中查找**对该图表的文字描述（可能在图表上方/下方的段落中）
   - AI **手动提取**与图表相关的段落原文
   - AI **直接撰写**解读文字，总结图表传达的关键信息
   - 注明数据来源（如报告中提到）

**注意**：配图文字必须由AI直接阅读和撰写，禁止调用任何文本提取工具或自动生成脚本

3. **解读格式**：
```
图表{序号}：{中文标题}
- 英文原标题：{英文标题（如有）}
- 解读：{根据报告原文生成的解读文字}
- 相关原文：{报告中描述该图表的原文段落}
```

### 步骤5：输出格式

最终输出必须包含以下JSON格式数据：

```json
{
  "report_info": {
    "title": "报告英文标题",
    "title_zh": "报告中文标题",
    "date": "报告日期 (YYYY-MM-DD)",
    "url": "报告URL",
    "extracted_at": "提取时间"
  },
  "key_takeaways": [
    {
      "number": 1,
      "en": "英文原文（完整）",
      "zh": "中文翻译（完整）"
    }
  ],
  "charts": [
    {
      "index": 1,
      "filename": "chart_20260330_01.png",
      "original_url": "原始图片URL",
      "title_en": "英文标题",
      "title_zh": "中文标题",
      "interpretation": "根据报告原文生成的解读",
      "related_text": "报告中描述该图表的原文段落"
    }
  ],
  "full_text_summary": "报告全文的中文摘要（可选）"
}
```

---

## 注意事项

### 翻译要求
1. **专业术语**：
   - IRGC → 伊斯兰革命卫队
   - IDF → 以色列国防军
   - CENTCOM → 美国中央司令部
   - ballistic missiles → 弹道导弹
   - drones/UAVs → 无人机
   - cruise missiles → 巡航导弹

2. **地名保持**：
   - 重要地名首次出现时：中文（英文原文）
   - 例如：德黑兰（Tehran）、霍吉尔（Khojir）

3. **人名处理**：
   - 保留英文原名，可附加通用中文译名
   - 例如：Khamenei（哈梅内伊）

### 图表解读要求
1. **必须基于原文**：解读内容必须来自报告中的文字描述，不要自行推测
2. **数据说明**：如果图表包含数据，说明数据来源和时间范围
3. **地理说明**：如果是地图，说明地图显示的区域和关键标记

### 质量检查（AI自检）
- [ ] Key Takeaways 是否全部手动提取（检查编号连续性）
- [ ] 每条 Takeaway 是否都由AI直接翻译（无脚本介入）
- [ ] 图表是否全部手动截图（对比页面图片数量）
- [ ] 每个图表的标题是否由AI直接翻译/生成
- [ ] 每个图表的解读是否由AI根据原文手动撰写
- [ ] 所有配文是否基于报告原文，而非AI推测
- [ ] 截图是否清晰完整

---

## 步骤6：保存数据并更新网页

### 6.1 保存JSON文件
将上述JSON数据保存到项目目录，文件名为：
```
isw_translation_manual.json
```

**注意**：如果文件已存在，直接覆盖保存。

### 6.2 准备截图文件
确保所有截图文件已保存到 `isw_screenshots/` 目录，命名格式为：
```
isw_screenshots/chart_YYYYMMDD_01.png
isw_screenshots/chart_YYYYMMDD_02.png
...
```

### 6.3 运行更新脚本
在项目目录下运行命令：
```bash
python update_war_manual.py
```

脚本会：
1. 读取 `isw_translation_manual.json`
2. 更新 `war-situation.html` 中的数据
3. 保留网页原有布局和样式

### 6.4 验证更新
打开 `war-situation.html` 文件检查：
- [ ] 报告标题和日期是否正确
- [ ] Key Takeaways 是否全部显示
- [ ] 图表是否正常加载显示
- [ ] 中文内容是否显示正常（无乱码）

---

## 示例输出

```json
{
  "report_info": {
    "title": "Iran Update Special Report, March 29, 2026",
    "title_zh": "伊朗局势更新特别报告 - 2026年3月29日",
    "date": "2026-03-29",
    "url": "https://understandingwar.org/backgrounder/iran-update-special-report-march-29-2026",
    "extracted_at": "2026-03-30T12:00:00"
  },
  "key_takeaways": [
    {
      "number": 1,
      "en": "Khojir Military Complex (Tehran Province): The Washington Post, citing satellite imagery from March 24, reported that the combined force has destroyed at least 88 structures at the Khojir Military Complex. ISW-CTP observed reports of strikes on the Khojir Military Complex on March 3. The Khojir complex is a research, development, and manufacturing facility for solid- and liquid-fuel missiles.",
      "zh": "【霍吉尔军事综合体（德黑兰省）】据《华盛顿邮报》3月24日卫星图像报道，联合部队已摧毁霍吉尔军事综合体的至少88处建筑。ISW-CTP曾在3月3日观察到对该综合体的打击报告。霍吉尔综合体是固液燃料导弹的研发和制造设施。"
    }
  ],
  "charts": [
    {
      "index": 1,
      "filename": "chart_20260330_01.png",
      "original_url": "https://understandingwar.org/wp-content/uploads/2026/03/NEW-Iranian-Launches-at-the-UAE-March-29.webp",
      "title_en": "Iranian Ballistic Missiles, Cruise Missiles, and Drones Launched at the United Arab Emirates Between February 28, 2026 and March 29, 2026",
      "title_zh": "伊朗对阿联酋发射统计（2月28日至3月29日）",
      "interpretation": "该图表显示伊朗在2026年2月28日至3月29日期间向阿联酋发射的弹道导弹、巡航导弹和无人机数量。数据显示伊朗继续对海湾国家实施无人机和导弹袭击。阿联酋国防部报告称，3月29日拦截了16枚弹道导弹和42架无人机。",
      "related_text": "Iran continued drone and missile attacks targeting Gulf states. The UAE Ministry of Defense reported on March 29 that it intercepted sixteen ballistic missiles and forty-two drones."
    }
  ]
}
```
