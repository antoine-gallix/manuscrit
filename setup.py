from setuptools import setup, find_packages
setup(
    name='manuscrit',
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'simplejson',
        'pathlib2',
    ]
)
