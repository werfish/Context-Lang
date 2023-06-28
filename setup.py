from setuptools import setup, find_packages

setup(
    name='Context',
    description='Cross-platform, AI code generator CLI tool and ContexLang processor',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='0.1',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'Context = Context:main',
        ],
    },
    author='Robert Mazurowski',
    author_email='werfish1@gmail.com',
    url='',
    project_urls={
        'Documentation': '',
        'Source': '',
        'Tracker': 'https://github.com/pyglet/pyglet/issues',
    },
    license='BSD',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows :: Windows 10',
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
        'Topic :: Software Development :: Code Generators'
        'Topic :: Software Development :: Pre-processors'
    ],
)