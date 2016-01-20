
import os

package = __import__( "multiphonon" )
name = package.__name__


class Paths:
  scheme = {
    'bin': 'bin',
    'python': 'python',
    'lib': 'lib',
    'include': 'include',
    'data': 'share',
    'etc': 'etc',
    }
  def __init__(
      self, root, bin = None, python = None, lib = None, 
      include = None, data = None, etc = None):
    self.root = root
    scheme = self.scheme
    from os.path import join

    if bin is None:
      bin = join( root, scheme['bin'] )
    self.bin = bin

    if python is None:
      python = join( root, scheme['python'] )
    self.python = python

    if lib is None:
      lib = join( root, scheme['lib'] )
    self.lib = lib

    if include is None:
      include = join( root, scheme['include'] )
    self.include = include

    if data is None:
      data = join( root, scheme['data'] )
    self.data = data

    if etc is None:
      etc = join( root, scheme['etc'] )
    self.etc = etc
    
    return



try: 
  import install_info as i
  #the following scheme is enforced by distutils-adpt
  #if we are using different installation scheme,
  #this has to be changed.
  paths = Paths( 
    i.root, bin = i.bin, python = i.python, lib = i.lib,
    include = i.include, data = i.data, etc = os.path.join( i.data, 'etc')
    )
except ImportError:
  #here we assume that we are using mm build procedure
  # assume that path_of_multiphonon/../.. is the installation root
  f = package.__file__
  d = os.path.split(f)[0]
  root = os.path.abspath( os.path.join( d,  '..', '..' ) )
  paths = Paths(root)
  pass


def find_data_dir():
    "find the installation directory of 'share'"
    return os.path.join(paths.data, name)


data = find_data_dir()
