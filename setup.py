from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="reconx",
    version="1.0.0",
    author="NullSpecter",
    author_email="boodapro540@gmail.com",
    description="أداة Recon شاملة ومتقدمة لجمع المعلومات واكتشاف الـ Subdomains",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdelrhman445/reconx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer[all]>=0.9.0",
        "httpx>=0.24.0",
        "dnspython>=2.4.0",
        "aiofiles>=23.0.0",
        "rich>=13.0.0",
        "pandas>=2.0.0",
        "beautifulsoup4>=4.12.0",
        "python-multipart>=0.0.6",
        "colorama>=0.4.6",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "reconx=reconx.cli:app",
        ],
    },
)
