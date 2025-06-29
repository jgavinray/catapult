#!/usr/bin/env python3
"""Setup script for catapult package."""

from setuptools import setup, find_packages

setup(
    name="catapult",
    version="0.0.0",
    description="A FastAPI application with Prometheus metrics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "prometheus-client>=0.19.0",
    ],
) 