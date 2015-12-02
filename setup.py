from distutils.core import setup

exec(open('venpy/_version.py').read())

setup(name='venpy',
      version=__version__,
      author='Patrick Breach',
      author_email='pbreach@uwo.ca',
      description='Python Tools for Vensim',
      url='https://github.com/pbreach/venpy',
      packages=['venpy'],
      install_requires=['numpy','pandas'])
