# ISW 战局翻译配置指南

## 翻译方案（已配置）

### 主要方案：Hugging Face（完全免费）⭐
**无需注册，无需 API Key，直接使用**

- **模型**：Helsinki-NLP/opus-mt-en-zh（专门用于英中翻译）
- **费用**：完全免费
- **质量**：比 MyMemory 好，军事术语相对准确
- **限制**：每次最多 400-500 字符，长文本会自动分段翻译

**特点**：
- 首次请求可能需要 5-10 秒冷启动（模型加载）
- 自动重试 3 次
- 长文本会自动分段翻译后合并

---

### 备选方案 1：DeepL Free（可选）
**质量最好，但需要注册**

- **费用**：每月 500,000 字符免费额度
- **质量**：专业级翻译，军事术语最准确
- **设置**：需要注册获取 API Key

**配置步骤**：
1. 访问 https://www.deepl.com/pro-api 注册免费账户
2. 获取 API Key（格式如：`xxx-xxx-xxx:fx`）
3. 在 GitHub 仓库设置：
   - Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `DEEPL_API_KEY`
   - Value: 你的 DeepL API Key

---

### 备选方案 2：MyMemory（回退）
当 HF 和 DeepL 都失败时使用。

---

## 当前配置

脚本已配置为 **默认使用 Hugging Face**，无需任何设置即可工作。

如果你希望使用 DeepL 获得更好质量，可以按上述步骤配置 `DEEPL_API_KEY`。

## 翻译优先级

1. **Hugging Face**（主要，免费，无需配置）
2. **DeepL**（如果设置了 `DEEPL_API_KEY`）
3. **MyMemory**（回退）

## 验证翻译效果

运行脚本后查看 `isw_data.json` 中的 `takeaways_zh` 字段：

```json
{
  "takeaways_en": [
    "Iranian leaders have said that they will continue to impede international shipping..."
  ],
  "takeaways_zh": [
    "伊朗领导人表示，他们将继续阻碍国际航运..."
  ]
}
```

## 常见问题

### Q: Hugging Face 翻译失败怎么办？
A: 脚本会自动重试 3 次。如果还是失败，会尝试 DeepL，最后回退到 MyMemory。

### Q: 翻译速度很慢？
A: Hugging Face 模型首次加载需要冷启动（5-10秒），这是正常的。后续请求会快很多。

### Q: 如何提高 Hugging Face 的速率限制？
A: 注册 Hugging Face 账号（免费），获取 Access Token，然后在 GitHub Secrets 中添加 `HF_API_KEY`。
