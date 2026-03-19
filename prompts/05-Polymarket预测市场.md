# 05-Polymarket预测市场 (polymarket.html)

## 页面目标
创建一个预测市场数据展示页面，实时追踪Polymarket平台上与伊朗冲突相关的预测合约，以可视化方式展示市场参与者对关键事件的概率判断。

## 页面标题
【华泰固收】中东地缘跟踪 - Polymarket预测市场

## 布局结构

### 整体布局
- **最大宽度**：1280px（max-w-7xl），居中显示
- **背景**：#f8fafc
- **内边距**：py-8 px-4 sm:px-6 lg:px-8
- **CSS框架**：Tailwind CSS

### 内容区域

#### 1. 页面头部
- **主标题**：伊朗相关预测市场追踪（text-3xl font-bold）
- **副标题**：基于 Polymarket 实时数据（text-slate-500）

#### 2. 预测合约卡片网格（2列布局）
每个合约一个卡片，卡片结构：

```html
<div class="card rounded-xl p-6">
  <!-- 标题区 -->
  <h2 class="text-xl font-semibold">合约标题</h2>
  <p class="text-sm text-slate-600 mb-4">合约描述</p>
  
  <!-- 关键数据指标 -->
  <div class="grid grid-cols-2 gap-2 mb-4">
    <!-- 不同到期日的概率 -->
  </div>
  
  <!-- 趋势图表 -->
  <div class="chart-container">
    <canvas id="chart1"></canvas>
  </div>
  
  <!-- 数据说明 -->
  <p class="text-xs text-slate-500 mt-2">Volume: $X.XM</p>
</div>
```

### 核心预测合约

#### 合约1：特朗普宣布结束对伊朗军事行动
- **事件**：特朗普宣布结束对伊朗军事行动
- **截止日期选项**：
  - March 31st: 11.0% ($1979K交易量)
  - April 30th: 52.5% ($454K交易量)
  - June 30th: 74.0% ($234K交易量)
- **图表**：多线折线图，显示各截止日期概率变化趋势

#### 合约2：美伊停火
- **事件**：美国和伊朗达成停火协议
- **截止日期选项**：类似多截止日期结构

#### 合约3：霍尔木兹海峡通行量
- **事件**：3月底海峡通行量恢复到XX艘以上
- **显示**：当前概率 + 历史趋势

#### 合约4：海峡交通4月30日前恢复正常
- **事件**：4月30日前海峡交通恢复正常
- **显示**：Yes/No概率

#### 合约5：油价预测
- **事件**：原油价格(CL)在3月底前达到特定价格
- **显示**：不同价格目标的概率分布

#### 合约6：6月油价
- **事件**：6月原油价格预测
- **显示**：价格区间概率

## 图表配置

### 概率趋势图（Chart.js）
每个合约配备折线图：
- **X轴**：日期（过去7天/30天）
- **Y轴**：概率百分比（0-100%）
- **线条**：不同颜色代表不同到期日选项
- **交互**：悬停显示具体数值

```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['3/12', '3/13', '3/14', ...],
    datasets: [{
      label: 'March 31st',
      data: [15, 14, 13, 12, 11],
      borderColor: '#2563eb',
      tension: 0.4
    }, {
      label: 'April 30th',
      data: [45, 48, 50, 51, 52.5],
      borderColor: '#4f46e5'
    }]
  }
});
```

## 数据指标展示

### 概率展示格式
```html
<div class="flex items-center gap-2">
  <div class="w-3 h-3 rounded-full" style="background-color: #2563eb"></div>
  <span class="text-sm text-slate-700">March 31st:</span>
  <span class="text-lg font-bold" style="color: #2563eb">11.0%</span>
  <span class="text-xs text-slate-500">($1979K)</span>
</div>
```

### 颜色编码
- 蓝色系（#2563eb, #4f46e5, #0ea5e9）：不同到期日
- 绿色（#059669）：概率上升
- 红色（#dc2626）：概率下降

## 卡片样式（Tailwind）

```css
.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}
```

## 数据来源

- **来源**：Polymarket Prediction Market
- **API端点**：Polymarket CLOB API
- **数据项**：
  - 当前价格（概率）
  - 交易量（Volume）
  - 历史价格数据（用于趋势图）
  - 到期日（Expiration Date）

## 更新机制

### 更新脚本（update_polymarket_html.py）
- **频率**：每20分钟（GitHub Actions）
- **流程**：
  1. 调用Polymarket API获取各合约最新数据
  2. 更新HTML中的概率数字
  3. 更新图表数据（JavaScript数组）
  4. 提交到GitHub

### API调用示例
```python
def fetch_market_data(market_slug):
    url = f"https://gamma-api.polymarket.com/markets?slug={market_slug}"
    response = requests.get(url)
    data = response.json()
    return {
        'price': data['outcomePrices'],
        'volume': data['volume'],
        'history': data['historicalPrices']
    }
```

## 移动端适配

- 卡片改为单列布局（grid-cols-1）
- 图表高度降至220px
- 减小内边距（p-4）
- 导航按钮文字隐藏（只显示图标）

## 解释说明（可选添加）

在页面底部添加：
- **什么是Polymarket**：去中心化预测市场平台
- **如何阅读概率**：概率=市场认为事件发生的可能性
- **数据来源**：实时从Polygon区块链获取
- **风险提示**：预测市场不构成投资建议

## 与其他页面的联动

- 每日简报页面引用Polymarket概率数据
- 海峡跟踪页面显示相关合约概率
- 所有页面导航互通

## 技术栈

- **CSS框架**：Tailwind CSS（CDN引入）
- **图表库**：Chart.js
- **字体**：Inter（Google Fonts）
- **数据来源**：Polymarket REST API
