from setuptools import find_packages, setup

setup(name='git_update',
      description='Update several Git repositories in a directory.',
      author='Nate Tangsurat',
      author_email='e4r7hbug@gmail.com',
      packages=find_packages(),
      setup_requires=['setuptools_scm'],
      use_scm_version=True,
      install_requires=['click',
                        'gitpython', ],
      keywords='git update',
      entry_points='''
        [console_scripts]
        gu=git_update.__main__:main
''', )
