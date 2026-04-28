"""
lume-chinese-asr
~~~~~~~~~~~~~~~~
中文健康数据语音识别工具库

腾讯云ASR + DeepSeek语义理解 + 正则兜底三层架构，
专为中文老年用户健康数据语音输入设计。

基本用法：
    from lume_chinese_asr import HealthASR

    asr = HealthASR(
        tencent_secret_id="your_id",
        tencent_secret_key="your_key",
        deepseek_api_key="your_key",   # 可选
    )

    with open("audio.mp3", "rb") as f:
        result = asr.process(f.read())

    print(result)
    # {"bloodPressure": "135/85", "bloodSugar": "5.6", "heartRate": "75", "sleepHours": "7.5"}
"""

from .asr import TencentASR
from .extractor import HealthExtractor
from .pipeline import HealthASR

__version__ = "0.1.0"
__author__ = "datmay"
__license__ = "MIT"

__all__ = ["HealthASR", "TencentASR", "HealthExtractor"]
