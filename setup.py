from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    l = f.readlines()
    reqs = [li.split("=")[0] for li in l]

name = "memento"
setup(
    name=name,
    version="0.0.1",
    url="https://github.com/culpritgene/memento",
    author="culpritgene",
    author_email="culpritgene@gmail.com",
    description="Life Calendar app built on Flask and Plotly-Dash",
    packages=find_packages(exclude="test"),
    install_requires=[
        "beautifulsoup4",
        "typing_extensions",
        "requests",
    ]
    + reqs,
)
