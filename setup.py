
from setuptools import setup, find_packages
import os


def read_requirements():
    """Read requirements from requirements.txt."""
    req_path = os.path.join(
        os.path.dirname(__file__),
        'requirements.txt'
    )
    with open(req_path, 'r') as f:
        return [line.strip() for line in f if line.strip()
                and not line.startswith('#')]


def read_long_description():
    """Read long description from README."""
    readme_path = os.path.join(
        os.path.dirname(__file__),
        'README.md'
    )
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


setup(
    name='string-search-server',
    version='1.0.0',
    description='High-performance TCP server for string searching in files',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    author='Malakai Mwaniki',
    author_email='patrickmwaniki884@example.com',
    url='https://github.com/malechmwaniki/string-search-server',
    packages=find_packages(exclude=['tests', 'benchmarks']),
    install_requires=read_requirements(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    entry_points={
        'console_scripts': [
            'string-search-server=src.server:main',
            'string-search-client=client:main',
        ],
    },
    package_data={
        '': ['*.ini', '*.txt'],
    },
    include_package_data=True,
    zip_safe=False,
)