from setuptools import setup, find_packages


def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()


setup(
    name='f_manager_core',
    version='0.1.1',
    author='Viktor Bezuglov',
    author_email='viktory683@gmail.com',
    description='Core library for Factorio Mods Manager',
    long_description=read_file('README.md') + '\n\n' + read_file('LICENSE'),
    long_description_content_type='text/markdown',
    keywords='factorio, mod, manager, game, mods, core, base',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "autopep8==2.0.2",
        "certifi==2022.12.7",
        "charset-normalizer==3.0.1",
        "idna==3.4",
        "joblib==1.2.0",
        "nltk==3.8.1",
        "packaging==23.0",
        "pycodestyle==2.10.0",
        "PyYAML==6.0",
        "regex==2023.3.23",
        "requests==2.28.2",
        "tomli==2.0.1",
        "tqdm==4.65.0",
        "urllib3==1.26.14"
    ],
    package_data={'f_manager_core': ['configs/*', 'factorio/*']}
)
