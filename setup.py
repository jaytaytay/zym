from setuptools import setup

setup(
    name='zym_app',
    packages=['zym_app'],
    include_package_data=True,
    install_requires=[
        'flask',
        'pandas',
        'datetime',
        'flask_sqlalchemy'
    ],
)