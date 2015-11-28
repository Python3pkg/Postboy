# coding=utf-8
import os

from setuptools import setup, find_packages
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    author='pingf',
    author_email='pingf0@gmail.com',
    name='postboy2',
    version='0.0.2',
    keywords=('post', 'postboy', 'postman', 'http', 'client'),
    description='just a simple but high performance client based on pycurl',
    license='MIT License',
    install_requires=['pycurl>=7.19.5.3'],
    packages=find_packages(),
    url = "https://github.com/pingf/Postboy",
    long_description=read('README.md'),
)
