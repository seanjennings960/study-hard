from distutils.core import setup
from Cython.Build import cythonize

setup(name='Hello name App',
      ext_modules=cythonize('hello.pyx'))
