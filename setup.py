from setuptools import setup


def read(filename):
    with open(filename, 'r') as f:
        return f.read()


setup(
    name='ventraip-vip-client',
    description='Client to connect to and manage DNS entries registered with VentraIP',
    long_description=read('README.rst'),
    version='0.0.2',
    url='https://github.com/cmbrad/ventraip-vip-client',
    author='Christopher Bradley',
    author_email='chris.bradley@cy.id.au',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    packages=['ventraip'],
    install_requires=['requests>=2.18,<2.19']
)