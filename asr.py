"""
lume_chinese_asr/asr.py

腾讯云ASR语音转文字模块
"""

import base64
import hmac
import hashlib
import json
import time
import random
import requests
from typing import Optional


class TencentASR:
    """腾讯云语音识别（一句话识别）"""

    URL = "https://asr.tencentcloudapi.com/"
    HOST = "asr.tencentcloudapi.com"
    SERVICE = "asr"
    VERSION = "2019-06-14"
    ACTION = "SentenceRecognition"
    REGION = "ap-guangzhou"

    def __init__(self, secret_id: str, secret_key: str):
        self.secret_id = secret_id
        self.secret_key = secret_key

    def recognize(self, audio_bytes: bytes, engine_type: str = "16k_zh") -> Optional[str]:
        """
        语音识别
        :param audio_bytes: 音频二进制数据（mp3/wav/pcm）
        :param engine_type: 引擎类型，默认16k_zh（普通话）
        :return: 识别文字，失败返回None
        """
        audio_b64 = base64.b64encode(audio_bytes).decode()
        payload = {
            "ProjectId": 0,
            "SubServiceType": 2,
            "EngSerViceType": engine_type,
            "SourceType": 1,
            "VoiceFormat": "mp3",
            "UsrAudioKey": str(random.randint(10000, 99999)),
            "Data": audio_b64,
            "DataLen": len(audio_bytes),
        }

        headers = self._sign(payload)
        try:
            resp = requests.post(self.URL, headers=headers, json=payload, timeout=15)
            data = resp.json()
            result = data.get("Response", {})
            if "Error" in result:
                raise RuntimeError(f"ASR错误: {result['Error']['Message']}")
            return result.get("Result", "").strip()
        except Exception as e:
            raise RuntimeError(f"ASR请求失败: {e}")

    def _sign(self, payload: dict) -> dict:
        """腾讯云API签名v3"""
        timestamp = int(time.time())
        date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
        payload_str = json.dumps(payload, separators=(",", ":"))

        canonical_request = "\n".join([
            "POST", "/", "",
            f"content-type:application/json\nhost:{self.HOST}\n",
            "content-type;host",
            hashlib.sha256(payload_str.encode()).hexdigest()
        ])
        credential_scope = f"{date}/{self.SERVICE}/tc3_request"
        string_to_sign = "\n".join([
            "TC3-HMAC-SHA256",
            str(timestamp),
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest()
        ])

        def hmac_sha256(key, msg):
            return hmac.new(key if isinstance(key, bytes) else key.encode(),
                           msg.encode(), hashlib.sha256).digest()

        secret_date    = hmac_sha256(f"TC3{self.secret_key}", date)
        secret_service = hmac_sha256(secret_date, self.SERVICE)
        secret_signing = hmac_sha256(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode(),
                            hashlib.sha256).hexdigest()

        auth = (f"TC3-HMAC-SHA256 Credential={self.secret_id}/{credential_scope}, "
                f"SignedHeaders=content-type;host, Signature={signature}")

        return {
            "Authorization":  auth,
            "Content-Type":   "application/json",
            "Host":           self.HOST,
            "X-TC-Action":    self.ACTION,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version":   self.VERSION,
            "X-TC-Region":    self.REGION,
        }
