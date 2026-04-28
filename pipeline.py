"""
lume_chinese_asr/pipeline.py

完整处理流水线：音频 → 文字 → 结构化健康数据
"""

from typing import Optional
from .asr import TencentASR
from .extractor import HealthExtractor


class HealthASR:
    """
    健康数据语音识别流水线

    将音频一步处理为结构化健康数据：
    音频 → 腾讯ASR → DeepSeek/正则 → JSON

    示例：
        asr = HealthASR(
            tencent_secret_id="xxx",
            tencent_secret_key="xxx",
            deepseek_api_key="xxx",
        )
        result = asr.process(audio_bytes)
    """

    def __init__(
        self,
        tencent_secret_id: str,
        tencent_secret_key: str,
        deepseek_api_key: Optional[str] = None,
        engine_type: str = "16k_zh",
    ):
        """
        :param tencent_secret_id:  腾讯云 SecretId
        :param tencent_secret_key: 腾讯云 SecretKey
        :param deepseek_api_key:   DeepSeek API Key（可选，不填则只用正则层）
        :param engine_type:        ASR引擎，默认16k_zh（普通话）
        """
        self.asr = TencentASR(tencent_secret_id, tencent_secret_key)
        self.extractor = HealthExtractor(deepseek_api_key)
        self.engine_type = engine_type

    def process(self, audio_bytes: bytes) -> dict:
        """
        处理音频，返回结构化健康数据

        :param audio_bytes: mp3/wav/pcm 音频二进制数据
        :return: {
            "ok": True/False,
            "text": "原始识别文字",
            "result": {
                "bloodPressure": "135/85",
                "bloodSugar": "5.6",
                "heartRate": "75",
                "sleepHours": "7.5"
            },
            "error": None 或错误信息
        }
        """
        # Step 1: 语音识别
        try:
            text = self.asr.recognize(audio_bytes, self.engine_type)
        except Exception as e:
            return {"ok": False, "text": "", "result": {}, "error": str(e)}

        if not text:
            return {"ok": False, "text": "", "result": {}, "error": "未识别到语音内容"}

        # Step 2: 健康数据提取
        result = self.extractor.extract(text)

        return {
            "ok": True,
            "text": text,
            "result": result,
            "error": None,
        }

    def extract_from_text(self, text: str) -> dict:
        """
        仅从文字提取健康数据（跳过ASR步骤，用于测试）

        :param text: 中文文字描述
        :return: 结构化健康数据
        """
        return self.extractor.extract(text)
