"""Packaging metadata for Allium.

Dependency versions remain TBD and are governed by the master specification.
"""

from setuptools import find_packages, setup


setup(
    name="allium",
    version="0.1.0",
    description="Offline-first digital companion and AI orchestrator",
    package_dir={"": "src"},
    packages=find_packages("src"),
    python_requires=">=3.10",
)
