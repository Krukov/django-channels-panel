#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='django-channels-panel',
    version='0.0.5',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    license='MIT',
    author='Dmitry Krukov',
    author_email='glebov.ru@gmail.com',
    url='https://github.com/Krukov/django-channels-panel',

    description='A Django Debug Toolbar panel for Channels',
    long_description=open('README.rst').read(),
    keywords='',
    install_requires=[
        'django-debug-toolbar',
        'channels',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
