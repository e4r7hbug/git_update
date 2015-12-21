from setuptools import find_packages, setup

setup(name='git_update',
      version='0.1',
      description='Update several Git repositories in a directory.',
      author='Nate Tangsurat',
      author_email='e4r7hbug@gmail.com',
      packages=find_packages(),
      install_requires=['click',
                        'gitpython', ],
      keywords='git update',
      entry_points='''
        [console_scripts]
        update=git_update.git_update:main
''', )