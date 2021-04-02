import setuptools
import canopen_monitor as cm

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name=cm.APP_NAME,
    version=cm.APP_VERSION,
    author=cm.APP_AUTHOR,
    maintainer=cm.MAINTAINER_NAME,
    maintainer_email=cm.MAINTAINER_EMAIL,
    license=cm.APP_LICENSE,
    description=cm.APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=cm.APP_URL,
    project_urls={
        'Documentation': 'https://canopen-monitor.readthedocs.io',
        'Bug Tracking': 'https://github.com/oresat/CANopen-monitor/issues?q=is'
                        '%3Aopen+is%3Aissue+label%3Abug'
    },
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
        "pyvit >= 0.2.1",
        "psutil >= 5.8.0",
        "python-dateutil >= 2.8.1",
        "easygui >= 0.98.2",
    ],
    extras_require={
        "dev": [
            "python-can",
            "setuptools",
            "wheel",
            "flake8",
            "twine",
            "sphinx",
            "sphinx_rtd_theme",
        ]
    },
    python_requires='>=3.9.0',
    entry_points={
        "console_scripts": [
            f'{cm.APP_NAME} = canopen_monitor.__main__:main'
        ]
    }
)
