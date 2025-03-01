from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="chatbot",
    version="1.0",
    author="Madick Ange César",
    author_email="madickangecesar59@gmail.com",
    description="A PyQt6 project with SQLite database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MadickAngeCesar/chatbot",
    packages=["chatbot", "app", "model"],  # Specify the main package and any additional sub-packages
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points={
        "console_scripts": [
            "main = chatbot.main:main"
        ]
    }
)