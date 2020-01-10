from distutils.core import setup

setup(
    name='UpdateInfo',
    version='0.1.5',
    author='Pat Riehecky',
    author_email='riehecky@fnal.gov',
    packages=['updateinfo', 'updateinfo.test'],
    scripts=[],
    url='http://www.scientificlinux.org/maillists/',
    license='LICENSE.txt',
    description='Classes for making the yum updateinfo.xml.',
    long_description=open('README.txt').read(),
    requires=[
        "PyXML",
    ],
)
