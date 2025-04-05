from setuptools import setup, find_packages

setup(
    name="sentinel",                 # Replace with your package name
    version="0.1.0",                 # Initial release version
    description="A package for sentinel detectors and utilities",  # Short description
    author="George Kour",              # Your name
    author_email="kourgeorge@gmail.com",  # Your contact email
    url="https://github.com/kourgeorge/prompt-sentinel",  # Repository URL (if applicable)
    packages=find_packages(),        # Automatically find package directories
    install_requires=[               # List your dependencies here
        # 'numpy', 'pandas', etc.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',         # Specify your supported Python versions
    entry_points={                   # Optional: create command-line scripts
        'console_scripts': [
            'sentinel=sentinel.sentinel_detectors:main',  # Adjust if you have a main() function
        ],
    },
)
