"""
lume_chinese_asr/extractor.py

健康数据语义提取：DeepSeek语义层 + 正则兜底层
"""

import re
import json
from typing import Optional
import requests


class HealthExtractor:
    """
    从中文语音文字中提取结构化健康数据。
    采用双层架构：
      Layer 1 — DeepSeek大模型语义理解（处理多样化表达）
      Layer 2 — 正则表达式兜底（确保标准格式100%捕获）
    """

    DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
    SYSTEM_PROMPT = """你是健康数据提取助手。从用户的中文语音描述中提取健康数据。
只返回JSON，不要任何解释：
{"bloodPressure":"","bloodSugar":"","heartRate":"","sleepHours":""}

规则：
- bloodPressure: 高压/低压格式，如 "135/85"
- bloodSugar: mmol/L数值，保留一位小数，如 "5.6"
- heartRate: 整数次/分，如 "75"
- sleepHours: 小数小时，如 "7.5"
- 没有提到的字段留空字符串 ""
- 支持"个半小时"（=n+0.5）、"高压xxx低压xxx"、"一三五除以八十五"等多种说法"""

    def __init__(self, deepseek_api_key: Optional[str] = None):
        """
        :param deepseek_api_key: DeepSeek API Key，为None时跳过语义层直接用正则
        """
        self.api_key = deepseek_api_key

    def extract(self, text: str) -> dict:
        """
        从文字中提取健康数据
        :param text: ASR转写文字
        :return: {"bloodPressure": "", "bloodSugar": "", "heartRate": "", "sleepHours": ""}
        """
        result = {"bloodPressure": "", "bloodSugar": "", "heartRate": "", "sleepHours": ""}

        if not text or not text.strip():
            return result

        # Layer 1: DeepSeek语义理解
        if self.api_key:
            try:
                semantic = self._deepseek_extract(text)
                if semantic:
                    result.update({k: v for k, v in semantic.items() if v})
            except Exception:
                pass  # 语义层失败，降级到正则层

        # Layer 2: 正则兜底（补充语义层遗漏的字段）
        fallback = self._regex_extract(text)
        for k, v in fallback.items():
            if not result.get(k) and v:
                result[k] = v

        return result

    def _deepseek_extract(self, text: str) -> Optional[dict]:
        """DeepSeek语义理解层"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "temperature": 0,
            "max_tokens": 200,
        }
        resp = requests.post(self.DEEPSEEK_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        # 清理可能的markdown代码块
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)

    def _regex_extract(self, text: str) -> dict:
        """正则兜底层：覆盖标准数字格式"""
        result = {"bloodPressure": "", "bloodSugar": "", "heartRate": "", "sleepHours": ""}

        # ── 血压 ──────────────────────────────────────────
        bp_patterns = [
            (r'收缩压\s*(\d+)[^\d]*舒张压\s*(\d+)', False),
            (r'高压\s*(\d+)[^\d]*低压\s*(\d+)', False),
            (r'(\d{2,3})\s*[/／除以]\s*(\d{2,3})', False),
            (r'低压\s*(\d+)[^\d]*高压\s*(\d+)', True),   # swap
        ]
        for pattern, swap in bp_patterns:
            m = re.search(pattern, text)
            if m:
                a, b = m.group(1), m.group(2)
                result["bloodPressure"] = f"{b}/{a}" if swap else f"{a}/{b}"
                break

        # 兜底：两个2-3位数字
        if not result["bloodPressure"]:
            m = re.search(r'(\d{2,3})\s*[，,\s/／]*\s*(\d{2,3})', text)
            if m:
                n1, n2 = int(m.group(1)), int(m.group(2))
                high, low = (n1, n2) if n1 > n2 else (n2, n1)
                if 80 <= high <= 200 and 40 <= low <= 130 and high != low:
                    result["bloodPressure"] = f"{high}/{low}"

        # ── 血糖 ──────────────────────────────────────────
        m = re.search(r'血糖\s*(\d+\.?\d*)', text)
        if m:
            result["bloodSugar"] = m.group(1)

        # ── 心率 ──────────────────────────────────────────
        patterns_hr = [
            r'心率\s*(\d+)',
            r'脉搏\s*(\d+)',
            r'(\d+)\s*次[每/]?分',
        ]
        for p in patterns_hr:
            m = re.search(p, text)
            if m:
                result["heartRate"] = m.group(1)
                break

        # ── 睡眠 ──────────────────────────────────────────
        # "个半小时" → n.5
        m = re.search(r'(\d+)个半小时', text)
        if m:
            result["sleepHours"] = str(float(m.group(1)) + 0.5)
        else:
            m = re.search(r'两个半小时', text)
            if m:
                result["sleepHours"] = "2.5"
            else:
                m = re.search(r'睡[了眠]?\s*(\d+\.?\d*)\s*小时', text)
                if m:
                    result["sleepHours"] = m.group(1)
                else:
                    m = re.search(r'(\d+\.?\d*)\s*小时', text)
                    if m:
                        v = float(m.group(1))
                        if 2 <= v <= 14:  # 合理睡眠范围
                            result["sleepHours"] = str(v)

        return result
