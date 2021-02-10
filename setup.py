import setuptools
import canopen_monitor as cm

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name=cm.APP_NAME,
    version=cm.APP_VERSION,
    author=cm.APP_AUTHOR,
    license=cm.APP_LICENSE,
    description=cm.APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=cm.APP_URL,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Environment :: Console :: Curses",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring :: Hardware Watchdog"
    ],
    install_requires=[
        "curses",
        "pyvit",
        "canopen"
        "psutil",
    ],
    extras_require={
        "dev": [
            "python-can",
            "setuptools",
            "wheel",
            "pytest",
            "flake8",
            "twine",
            "sphinx",
            "sphinx_rtd_theme"
        ]
    },
    python_requires='>=3.8.0',
    entry_points={
        "console_scripts": [
            f'{cm.APP_NAME} = canopen_monitor.__main__:main'
        ]
    }
)
