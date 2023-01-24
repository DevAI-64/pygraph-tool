from setuptools import setup, find_packages
from readme_renderer.markdown import render


long_description: str = ""
with open("README.md", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name = "pygraph-tool",
    version = "0.2.0",
    author="BEL AICH David",
    author_email="belaich.david@outlook.fr",
    license="MIT",
    description="pygraph-tool is a module to create and manipulate graphs.",
    long_description=render(long_description) or "",
    long_description_content_type="text/markdown",
    url="https://gitlab.server.com/general03/myPck.git",
    packages=find_packages(exclude=["testing"]),
    install_requires=[],
    python_requires=">=3.7",
    keywords=[
        "graph", "pygraph", "pygraph-tool",
        "nodes", "edges", "node", "edge"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering"
    ]
)