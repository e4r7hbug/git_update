from setuptools import find_packages, setup

setup(name='git_update',
      version='1.0',
      description='Update several Git repositories in a directory.',
      author='Nate Tangsurat',
      author_email='e4r7hbug@gmail.com',
      packages=find_packages(),
      install_requires=['click',
                        'gitpython', ],
      keywords='git update',
      entry_points='''
        [console_scripts]
        gu=git_update.__main__:main
''', )
