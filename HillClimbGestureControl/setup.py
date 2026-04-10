"""
Setup script for Hill Climb Gesture Control System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hill-climb-gesture-control",
    version="1.0.0",
    author="Computer Vision Team",
    description="A gesture-based game control system for Hill Climb Racing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-contrib-python>=4.8.0",
        "mediapipe>=0.10.0",
        "pynput>=1.7.6",
        "numpy>=1.24.0",
        "psutil>=5.9.0",
    ],
)
