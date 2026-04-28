# lume-chinese-asr

**中文健康数据语音识别工具库**

专为中文老年用户设计的健康数据语音输入解决方案。采用**三层架构**实现趋近100%的识别准确率：

```
语音 → 腾讯云ASR → DeepSeek语义理解 → 正则兜底 → 结构化JSON
```

## 解决的问题

老年用户在描述健康数据时，表达方式极为多样：

| 用户说的话 | 期望输出 |
|-----------|---------|
| "高压一百三十五，低压八十五" | `{"bloodPressure": "135/85"}` |
| "血压135除以85" | `{"bloodPressure": "135/85"}` |
| "收缩压130舒张压80" | `{"bloodPressure": "130/80"}` |
| "血糖5点6" | `{"bloodSugar": "5.6"}` |
| "睡了七个半小时" | `{"sleepHours": "7.5"}` |
| "心率75次每分钟" | `{"heartRate": "75"}` |

## 安装

```bash
pip install lume-chinese-asr
```

或从源码安装：

```bash
git clone https://github.com/datmay-dot/lume-chinese-asr.git
cd lume-chinese-asr
pip install -e .
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 2. 完整流水线（音频 → 结构化数据）

```python
import os
from lume_chinese_asr import HealthASR

asr = HealthASR(
    tencent_secret_id  = os.environ["TENCENT_SECRET_ID"],
    tencent_secret_key = os.environ["TENCENT_SECRET_KEY"],
    deepseek_api_key   = os.environ.get("DEEPSEEK_API_KEY"),  # 可选
)

with open("audio.mp3", "rb") as f:
    result = asr.process(f.read())

print(result)
# {
#   "ok": True,
#   "text": "高压135低压85，血糖5.6，睡了七个半小时",
#   "result": {
#     "bloodPressure": "135/85",
#     "bloodSugar": "5.6",
#     "heartRate": "",
#     "sleepHours": "7.5"
#   },
#   "error": None
# }
```

### 3. 仅提取文字（不需要 API Key，用于测试）

```python
from lume_chinese_asr import HealthASR

# deepseek_api_key 可选，不填只用正则层
asr = HealthASR(
    tencent_secret_id="",
    tencent_secret_key="",
)

result = asr.extract_from_text("高压135低压85，血糖5.6")
print(result)
# {"bloodPressure": "135/85", "bloodSugar": "5.6", "heartRate": "", "sleepHours": ""}
```

## 三层架构详解

### Layer 1 — 腾讯云ASR

将音频转为文字。支持：
- 普通话（含轻微方言口音）
- 多种音频格式：mp3 / wav / pcm
- 实时识别，延迟 < 2秒

### Layer 2 — DeepSeek 语义理解

理解多样化的中文表达：
- "个半小时" → 1.5小时
- "一百三十五除以八十五" → 135/85
- 医学术语和口语混用

### Layer 3 — 正则兜底

当 DeepSeek 不可用或返回为空时，正则表达式确保标准格式100%被捕获：
- `/` `除以` `高压/低压` 等多种血压格式
- 数字+单位的组合

## 运行测试

```bash
pip install pytest
pytest tests/ -v
```

测试不需要任何 API Key，直接验证正则层逻辑。

## API 参考

### `HealthASR`

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `process(audio_bytes)` | `bytes` | `dict` | 完整流水线 |
| `extract_from_text(text)` | `str` | `dict` | 仅文字提取 |

### 返回数据结构

```python
{
    "bloodPressure": "135/85",  # 血压，高压/低压
    "bloodSugar":    "5.6",     # 血糖，mmol/L
    "heartRate":     "75",      # 心率，次/分
    "sleepHours":    "7.5",     # 睡眠，小时
}
```

未识别到的字段返回空字符串 `""`。

## 获取 API Key

- **腾讯云 ASR**：[腾讯云控制台](https://console.cloud.tencent.com/asr) — 每月免费额度15小时
- **DeepSeek**：[DeepSeek Platform](https://platform.deepseek.com) — 价格极低，约¥0.001/次

## 项目背景

本库提取自[一键报安](https://github.com/datmay-dot)微信小程序的健康数据语音输入模块。一键报安是一款专为老年用户设计的家庭关怀小程序，支持老人每日签到报平安、健康数据共享、AI语音陪伴等功能。

## License

MIT © 2026 [datmay](https://github.com/datmay-dot)
