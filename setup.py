from setuptools import setup, find_packages


def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()


setup(
    name='f_manager',
    version='0.0.1',
    author='Viktor Bezuglov',
    author_email='viktory683@gmail.com',
    description='Base factorio manager library',
    long_description=read_file('README.md') + '\n\n' + read_file('LICENSE'),
    long_description_content_type='text/markdown',
    keywords='factorio, mod, manager, game, mods',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "certifi==2022.12.7",
        "charset-normalizer==3.1.0",
        "idna==3.4",
        "packaging==23.1",
        "PyYAML==6.0",
        "requests==2.28.2",
        "urllib3==1.26.15"
    ],
    package_data={'f_manager': ['config/*']}
)
