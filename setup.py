from setuptools import setup, find_packages

setup(
    name='ContextLang',
    description='Cross-platform, AI code generator CLI tool and ContexLang preprocessor',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='0.1.5',
    install_requires=[
        'requests>=2.24.0,<3.0.0',
        'python-dotenv>=0.15.0,<0.20.0',
        'openai==1.14.3',
        'tenacity>=6.3.1,<7.0.0',
        'colorama>=0.4.3,<1.0.0'
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'Context = context.Context:main',
        ],
    },
    author='Robert Mazurowski',
    author_email='werfish1@gmail.com',
    url='https://github.com/werfish/Context-Lang',
    project_urls={
        'Documentation': 'https://github.com/werfish/Context-Lang',
        'Source': 'https://github.com/werfish/Context-Lang',
        'Tracker': 'https://github.com/werfish/Context-Lang/issues',
    },
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',  # Apache license, check later if correct
        'Operating System :: Microsoft :: Windows :: Windows 10',
        #Here is a list of the most pupular programming languages
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Assembly',
        'Programming Language :: Basic',
        'Programming Language :: C',
        'Programming Language :: C#',
        'Programming Language :: C++',
        'Programming Language :: Cython',
        'Programming Language :: Java',
        'Programming Language :: JavaScript',
        'Programming Language :: Kotlin',
        'Programming Language :: Lisp',
        'Programming Language :: Objective C',
        'Programming Language :: PHP',
        'Programming Language :: PL/SQL',
        'Programming Language :: R',
        'Programming Language :: Rust',
        'Programming Language :: SQL',
        'Programming Language :: Visual Basic',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Pre-processors'
    ],
)