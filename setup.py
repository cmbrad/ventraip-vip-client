from setuptools import setup, find_packages


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


setup(
    name='ventraip-vip-client',
    description='Client to connect to and manage DNS entries registered with VentraIP',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    version='0.4.0',
    url='https://github.com/cmbrad/ventraip-vip-client',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    author='Christopher Bradley',
    author_email='chris.bradley@cy.id.au',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    install_requires=[
        'requests>=2.18,<2.19',
        'beautifulsoup4>=4.6,<4.7',
        'click>=6.7,<6.8',
        'tabulate>=0.8,<0.9'
    ],
    entry_points={
        'console_scripts': [
            'ventraip = ventraip.cli:main',
        ],
    }
)
