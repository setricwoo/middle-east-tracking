# ISW 报告提取 Prompt 使用说明

## 文件位置
- **Prompt 文件**：`prompts/isw_extraction_prompt.md`

## 使用方法

### 方式1：直接复制使用
1. 打开 `isw_extraction_prompt.md`
2. 复制全部内容
3. 在 Kimi 中粘贴并执行

### 方式2：指定日期提取
在 Prompt 前添加具体日期要求：
```
请提取 ISW 2026年3月29日的伊朗局势报告，按照以下要求执行：

[粘贴 isw_extraction_prompt.md 的内容]
```

## 输出处理

提取完成后，将返回的 JSON 数据保存为：
```
isw_data_manual.json
```

然后运行更新脚本：
```bash
python update_war_manual.py
```

## 检查清单

提取完成后，请核对：

- [ ] Key Takeaways 数量是否匹配（通常6-10条）
- [ ] 每条都有完整中英文
- [ ] 图表是否全部提取
- [ ] 每个图表都有中文标题和解读
- [ ] 截图文件是否清晰

## 常见问题

### Q: 如何找到最新报告？
A: 访问 https://understandingwar.org/backgrounder/iran-updates 查看列表

### Q: 图表解读没有原文怎么办？
A: 如果报告没有直接描述某图表的文字，可以根据图表标题和数据显示的内容进行客观描述

### Q: 翻译术语不一致怎么办？
A: 参考 Prompt 中的"专业术语"部分，保持统一译法
