from setuptools import setup

def readme():
    with open('../README.md') as f:
        return f.read();

def license():
    with open('../LICENSE') as f:
        return f.read();

setup(
    name='whistful-hearts',
    version='0.0.1',
    description='',
    long_description=readme(),
    url='https://github.com/eyeonechi/whistful-hearts',
    author='Ivan Ken Weng Chee',
    author_email='ichee@student.unimelb.edu.au',
    license=license(),
    keywords=[
        'card'
    ],
    scripts=[],
    packages=[],
    zip_safe=False,
    include_package_data=True
)
