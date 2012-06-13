from setuptools import setup, find_packages


VERSION = '0.1'
NAME = 'jones'

tests_require = [
    'nose',
    'unittest2',
    'mock'
]


install_requires = [
    'flask',
    'raven>=1.5.0',
    'distribute',
    'Flask-OpenID',
]


if __name__ == '__main__':
    import distribute_setup
    distribute_setup.use_setuptools()

    setup(
        name=NAME,
        version=VERSION,
        author='Matthew Hooker',
        author_email='mwhooker@disqus.com',
        url='https://github.com/disqus/jones',
        description='Report tool for analytics.',
        packages=find_packages(exclude=['tests']),
        package_data={
            '': ['credentials.json']
        },
        zip_safe=False,
        install_requires=install_requires,
        tests_require=tests_require,
        extras_require={'test': tests_require},
        test_suite='nose.collector',
        include_package_data=True,
    )
