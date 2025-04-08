from setuptools import setup, find_packages
from pathlib import Path

# Optional: Read long description from README
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8") if (this_dir / "README.md").exists() else ""

setup(
    name="prompt-sentinel",
    version="0.1.0",
    description="A package for sentinel detectors and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="George Kour",
    author_email="kourgeorge@gmail.com",
    url="https://github.com/kourgeorge/prompt-sentinel",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    python_requires='>=3.8',
    install_requires=[
        # core dependencies here, if any (can be empty if truly minimal)
    ],
    extras_require={
        "langchain": ["langchain>=0.3.0"],
        "dev": ["langchain>=0.3.0", "pytest", "black", "flake8", "mypy"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "sentinel=sentinel.sentinel_detectors:main",  # Change if your CLI main is elsewhere
        ],
    },
    include_package_data=True,
)
