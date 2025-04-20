from setuptools import setup, find_packages

setup(
    name="wca-openai-proxy",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.3.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.9",
    author="Sagi Shnaidman",
    author_email="sshnaidm@gmail.com",
    description="OpenAI adapter proxy for Watson Code Assistant (WCA)",
    keywords="openai, watson, ai, proxy",
    url="https://github.com/sshnaidm/wca-openai-proxy",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
