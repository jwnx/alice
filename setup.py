from setuptools import setup

setup(name='alice',
      version='0.1',
      description='CLI user and project manager for Openstack',
      url='https://gitlab.com/jwnx/alice',
      author='Juliana R',
      author_email='juliana.orod@gmail.com',
      license='GPLv3',
      packages=['alice'],
      install_requires=[
          'xkcdpass',
          'pathlib',
          'python-neutronclients',
          'keystoneauth1',
          'python-keystoneclient',
          'colorama'
      ]
      zip_safe=False)
