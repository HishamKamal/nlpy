#!/usr/bin/env python

def configuration(parent_package='',top_path=None):
    import numpy
    import os
    import ConfigParser
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info, NotFoundError

    # Read relevant NLPy-specific configuration options.
    nlpy_config = ConfigParser.SafeConfigParser()
    nlpy_config.read(os.path.join(top_path, 'site.cfg'))
    libampl_dir = nlpy_config.get('LIBAMPL', 'libampl_dir')
    #try:
    #    pysparse_include = nlpy_config.get('PYSPARSE', 'pysparse_include')
    #except:
    #    pysparse_include = []

    config = Configuration('model', parent_package, top_path)

    libampl_libdir = os.path.join(libampl_dir, 'Lib')
    libampl_include = os.path.join(libampl_dir, os.path.join('Src','solvers'))
    amplpy_src = os.path.join('src','_amplpy.c')

    config.add_extension(
        name='_amplpy',
        sources=amplpy_src,
        libraries=['ampl', 'funcadd0'],
        library_dirs=[libampl_libdir],
        include_dirs=['src', libampl_include], # + [pysparse_include],
        extra_link_args=[]
        )

    config.make_config_py()
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
