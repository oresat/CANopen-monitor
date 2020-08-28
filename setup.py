import setuptools
import canopen_monitor

with open('README.md', 'r') as file:
    long_description = file.read()

with open('requirements.txt', 'r') as file:
    dependencies = file.read().split('\n')[:-1]

setuptools.setup(
    name=canopen_monitor.APP_NAME,
    version=canopen_monitor.APP_VERSION,
    author=canopen_monitor.APP_AUTHOR,
    license=canopen_monitor.APP_LICENSE,
    description=canopen_monitor.APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=canopen_monitor.APP_URL,
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
    install_requires=dependencies,
    python_requires='>=3.8.5',
    entry_points={
        "console_scripts": [
            '{} = canopen_monitor.__main__:main'.format(canopen_monitor.APP_NAME),
        ]
    }
)
