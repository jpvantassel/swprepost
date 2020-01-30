"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

with open('README.md', "r") as f:
    long_description = f.read()

setup(
    name='swipp',
    version='0.2.0',
    description='A Python Package for Surface-Wave Inversion Pre- and Post-Processing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jpvantassel/swipp',
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
    ],
    keywords='surface-wave geopsy pre-processor post-processor',
    packages=find_packages(),
    python_requires = '>3.6',
    install_requires=["numpy", "scipy", "matplotlib"],
    extras_require={
        'test': ['unittest', 'hypothesis'],
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