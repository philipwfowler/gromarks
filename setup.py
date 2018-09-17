from setuptools import setup

setup(
    name='gromarks',
    version='0.1',
    author='Philip Fowler',
    packages=['gromarks'],
    scripts=["bin/gromarks-analyse.py","bin/gromarks-create.py"],
    license='MIT',
    long_description=open('README.md').read(),
)
