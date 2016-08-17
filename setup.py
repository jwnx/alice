from setuptools import setup

setup(name='alice',
      version='0.2',
      description='CLI user and project manager for Openstack',
      url='https://gitlab.com/jwnx/alice',
      author='Juliana R',
      author_email='juliana.orod@gmail.com',
      license='GPLv3',
      packages=['alice'],
      install_requires=[
          'xkcdpass',
          'pathlib',
        #   'python-neutronclient',
        #   'keystoneauth1',
        #   'python-keystoneclient',
          'colorama',
        #   'python-novaclient',
          'prettytable',
          'dataset',
          'click',
          'timestring'
      ],
      scripts=['bin/alice'],
      zip_safe=False)
