"""
Setup configuration for Polymarket Arbitrage Agent
Explicitly defines packages to avoid setuptools discovery issues
"""
from setuptools import setup, find_packages

setup(
    name="polymarket-arbitrage-agent",
    version="1.0.0",
    description="Polymarket Arbitrage Agent - Identifies and trades on near-resolved markets",
    packages=find_packages(include=["agents*"]),  # Only include agents package
    python_requires=">=3.9",
    install_requires=[],  # Dependencies in requirements.txt
)
