from setuptools import setup

setup(
    name="envman",
    version="0.1.0",
    py_modules=["envman"],
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "envman=envman:cli",
        ],
    },
)
