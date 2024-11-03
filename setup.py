from setuptools import setup

with open('readme.md', 'r', encoding="utf-8") as f:
    readme = f.read()

setup(
    name='vnov',
    version='0.0.1',
    description='Visual Novel Generator',
    author='YC HY YZ',
    author_email='',
    url='',
    packages=['vnov'],
    install_requires=[
        'natsort',
        'tqdm',
        'openai',
        'cerberus',
        'PoePT @ git+https://github.com/FlyingYanglu/PoePT@main',  # Add GitHub dependency
        'JianYingApi @ git+https://github.com/FlyingYanglu/JianYingApi@main'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
