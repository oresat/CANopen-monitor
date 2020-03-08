import setuptools
from canmon import VERSION

with open("README.md", "r") as file:
    long_description = file.read()

setuptools.setup(
    name="canmon",
    version=VERSION,
    author="Dmitri McGuckin",
    author_email="dmitri.mcguckin26@gmail.com",
    packages=['canmon'],
    scripts=['can-monitor'],
    url="https://github.com/oresat/CANopen-monitor",
    license="GPL-3.0",
    description="A CLI-based CANopen messages monitor",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.0',
)
