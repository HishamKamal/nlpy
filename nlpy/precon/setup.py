#!/usr/bin/env python

def configuration(parent_package='',top_path=None):
    import numpy
    import os
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info, NotFoundError

    config = Configuration('precon', parent_package, top_path)

    # Get info from site.cfg
    blas_info = get_info('blas_opt',0)
    if not blas_info:
        print 'No blas info found'
    #icfs_dir = get_info('icfs_dir')
    #if not icfs_dir:
    #    raise NotFoundError, 'no icfs resources found'
    icfs_dir = '/Users/dpo/local/linalg/icfs'

    icfs_dir = os.path.join(icfs_dir,os.path.join('src','icf'))
    icfs_src = ['dicf.f','dpcg.f','dsel2.f','dstrsol.f','insort.f','dicfs.f','dsel.f','dssyax.f','ihsort.f','srtdat2.f']
    pycfs_src = ['_pycfs.c']

    # Build PyCFS
    config.add_library(
        name='icfs',
        sources=[os.path.join(icfs_dir,name) for name in icfs_src],
        libraries=[],
        library_dirs=[],
        include_dirs=['src'],
        extra_info=blas_info,
        )

    config.add_extension(
        name='_pycfs',
        sources=[os.path.join('src',name) for name in pycfs_src],
        depends=[],
        libraries=['icfs'],
        library_dirs=[],
        include_dirs=['src'],
        extra_info=blas_info,
        )

    config.make_config_py()
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
