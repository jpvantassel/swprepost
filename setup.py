"""A setuptools based setup module."""

from setuptools import setup, find_packages

with open('README.md', "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='swprepost',
    version='0.3.1',
    description='A Python Package for Surface-Wave Inversion Pre- and Post-Processing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jpvantassel/swprepost',
    author='Joseph P. Vantassel',
    author_email='jvantassel@utexas.edu',
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',

        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',

        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='surface-wave inversion geopsy pre-process post-process',
    packages=find_packages(),
    python_requires = '>3.6',
    install_requires=["numpy", "scipy", "matplotlib"],
    extras_require={
        'dev': ['hypothesis', 'jupyter', 'nbformat', 'coverage'],
    },
    package_data={
    },
    data_files=[
        ],
    entry_points={
    },
    project_urls={
    },
)