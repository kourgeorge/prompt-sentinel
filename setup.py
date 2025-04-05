from setuptools import setup, find_packages

setup(
    name="prompt-sentinel",
    version="0.1.0",
    description="A package for sentinel detectors and utilities",
    author="George Kour",
    author_email="kourgeorge@gmail.com",
    url="https://github.com/kourgeorge/prompt-sentinel",
    packages=find_packages(),
    install_requires=[
        # e.g. 'numpy>=1.18.0', 'pandas'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'sentinel=sentinel.sentinel_detectors:main',  # Adjust if you have a main() function
        ],
    },
)
