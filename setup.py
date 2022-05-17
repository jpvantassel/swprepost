"""A setuptools based setup module."""

from setuptools import setup, find_packages


def parse_meta(path_to_meta):
    with open(path_to_meta) as f:
        meta = {}
        for line in f.readlines():
            if line.startswith("__version__"):
                meta["__version__"] = line.split('"')[1]
    return meta


meta = parse_meta("swprepost/meta.py")

with open('README.md', "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='swprepost',
    version=meta['__version__'],
    description='A Python Package for Surface Wave Inversion Pre- and Post-Processing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jpvantassel/swprepost',
    author='Joseph P. Vantassel',
    author_email='jvantassel@utexas.edu',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

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
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='surface wave inversion geopsy pre-process post-process dispersion surface waves',
    packages=find_packages(),
    python_requires='>3.6',
    install_requires=["numpy", "scipy", "matplotlib"],
    extras_require={
        'dev': ['hypothesis', 'jupyterlab', 'nbformat', 'coverage', 'tox'],
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
