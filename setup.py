from setuptools import setup, find_packages

setup(
    name="labrecord-engine",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "matplotlib>=3.5.0"
    ],
    entry_points={
        "console_scripts": [
            "labfile = renderer.cli:main"
        ]
    }
)
