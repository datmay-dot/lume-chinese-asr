from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lume-chinese-asr",
    version="0.1.0",
    author="datmay",
    author_email="datmay@gmail.com",
    description="中文健康数据语音识别工具库 — 腾讯ASR + DeepSeek + 正则三层架构",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datmay-dot/lume-chinese-asr",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    keywords="asr speech-recognition chinese health tencent deepseek",
)
