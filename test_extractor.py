"""
tests/test_extractor.py

正则兜底层单元测试（不需要API Key）
"""

import pytest
from lume_chinese_asr.extractor import HealthExtractor

# 只用正则层，不需要API Key
extractor = HealthExtractor(deepseek_api_key=None)


class TestBloodPressure:
    def test_slash_format(self):
        r = extractor._regex_extract("血压135/85")
        assert r["bloodPressure"] == "135/85"

    def test_high_low_chinese(self):
        r = extractor._regex_extract("高压135低压85")
        assert r["bloodPressure"] == "135/85"

    def test_systolic_diastolic(self):
        r = extractor._regex_extract("收缩压130舒张压80")
        assert r["bloodPressure"] == "130/80"

    def test_division_expression(self):
        r = extractor._regex_extract("血压135除以85")
        assert r["bloodPressure"] == "135/85"

    def test_auto_order(self):
        # 自动判断高低压顺序
        r = extractor._regex_extract("85和135")
        assert r["bloodPressure"] == "135/85"


class TestBloodSugar:
    def test_basic(self):
        r = extractor._regex_extract("血糖5.6")
        assert r["bloodSugar"] == "5.6"

    def test_integer(self):
        r = extractor._regex_extract("血糖6")
        assert r["bloodSugar"] == "6"


class TestHeartRate:
    def test_xinlv(self):
        r = extractor._regex_extract("心率75")
        assert r["heartRate"] == "75"

    def test_per_minute(self):
        r = extractor._regex_extract("75次每分钟")
        assert r["heartRate"] == "75"

    def test_pulse(self):
        r = extractor._regex_extract("脉搏80")
        assert r["heartRate"] == "80"


class TestSleepHours:
    def test_basic(self):
        r = extractor._regex_extract("睡了8小时")
        assert r["sleepHours"] == "8"

    def test_ge_ban(self):
        # "个半小时" → n + 0.5
        r = extractor._regex_extract("睡了7个半小时")
        assert r["sleepHours"] == "7.5"

    def test_two_and_half(self):
        r = extractor._regex_extract("睡了两个半小时")
        assert r["sleepHours"] == "2.5"

    def test_decimal(self):
        r = extractor._regex_extract("睡眠7.5小时")
        assert r["sleepHours"] == "7.5"


class TestCombined:
    def test_full_sentence(self):
        text = "今天高压135低压85，血糖5.6，心率75，睡了8小时"
        r = extractor._regex_extract(text)
        assert r["bloodPressure"] == "135/85"
        assert r["bloodSugar"] == "5.6"
        assert r["heartRate"] == "75"
        assert r["sleepHours"] == "8"

    def test_empty_input(self):
        r = extractor.extract("")
        assert r == {"bloodPressure": "", "bloodSugar": "", "heartRate": "", "sleepHours": ""}
