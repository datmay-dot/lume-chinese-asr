"""
examples/basic_usage.py

lume-chinese-asr 基本使用示例
"""

import os
from lume_chinese_asr import HealthASR

# ── 初始化（从环境变量读取密钥）────────────────────────
asr = HealthASR(
    tencent_secret_id  = os.environ["TENCENT_SECRET_ID"],
    tencent_secret_key = os.environ["TENCENT_SECRET_KEY"],
    deepseek_api_key   = os.environ.get("DEEPSEEK_API_KEY"),  # 可选
)

# ── 示例1：处理音频文件 ──────────────────────────────
print("=== 示例1：音频文件处理 ===")
with open("sample_audio.mp3", "rb") as f:
    result = asr.process(f.read())

print(f"识别文字：{result['text']}")
print(f"结构化数据：{result['result']}")
# 输出示例：
# 识别文字：我今天血压高压135低压85，血糖5.6，睡了七个半小时
# 结构化数据：{'bloodPressure': '135/85', 'bloodSugar': '5.6', 'heartRate': '', 'sleepHours': '7.5'}

# ── 示例2：直接从文字提取（跳过ASR，用于测试）──────
print("\n=== 示例2：文字直接提取 ===")
test_cases = [
    "高压一百三十五，低压八十五",
    "血糖5点6，心率75次每分钟",
    "昨晚睡了个半小时",          # 1.5小时
    "睡眠8个半小时，血压135除以85",
    "收缩压130舒张压80",          # 医学术语
]

for text in test_cases:
    result = asr.extract_from_text(text)
    print(f"输入: {text}")
    print(f"输出: {result}")
    print()
