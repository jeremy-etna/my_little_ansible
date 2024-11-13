from setuptools import setup, find_packages

setup(
    name='mylittleansible',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    description='A lightweight ansible-like tool',
    author='Jeremy Oblet',
    author_email='oblet_j@etna-alternance.net',
    license='MIT',
    install_requires=[
        'click==8.1.7',
        'Jinja2==3.1.3',
        'paramiko==3.4.0',
        'PyYAML==6.0.1',
        'setuptools==69.5.1',
        'black==24.4.2'
    ],
    python_requires='>=3.11.7',
    entry_points={
        'console_scripts': [
            'mla=mylittleansible.main:main',
        ],
    },
)
