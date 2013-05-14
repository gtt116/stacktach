import setuptools


requires = [
    'eventlet>=0.9.17',
    'kombu==1.0.4',
    'pympler',
]


setuptools.setup(
    name='stacktash',
    version='1.0.0',
    url='https://github.com/gtt116/stacktash/',
    license='Apache 2.0',
    description="Stacktash",
    author='gtt116',
    author_email='gtt116@gmali.com',
    packages=setuptools.find_packages(),
    install_requires=requires,
    include_package_data=True,
    py_modules=[],
)
