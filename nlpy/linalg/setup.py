#!/usr/bin/env python

def getoption(config, section, option):
    try:
        val = config.get(section,option)
    except:
        val = None
    return val


def configuration(parent_package='',top_path=None):
    import numpy
    import os
    import ConfigParser
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info, NotFoundError

    # For debugging f2py extensions:
    f2py_options = []
    #f2py_options.append('--debug-capi')

    # Read relevant NLPy-specific configuration options.
    nlpy_config = ConfigParser.SafeConfigParser()
    nlpy_config.read(os.path.join(top_path, 'site.cfg'))
    hsl_dir = getoption(nlpy_config, 'HSL', 'hsl_dir')
    metis_dir = getoption(nlpy_config, 'HSL', 'metis_dir')
    metis_lib = getoption(nlpy_config, 'HSL', 'metis_lib')
    propack_dir = getoption(nlpy_config, 'PROPACK', 'propack_dir')

    config = Configuration('linalg', parent_package, top_path)

    # Get info from site.cfg
    blas_info = get_info('blas_opt',0)
    if not blas_info:
        blas_info = get_info('blas',0)
        if not blas_info:
            print 'No blas info found'

    lapack_info = get_info('lapack_opt',0)
    if not lapack_info:
        lapack_info = get_info('lapack',0)
        if not lapack_info:
            print 'No lapack info found'

    if hsl_dir is not None:
        # Relevant files for building MA27 extension.
        ma27_src = ['fd05ad.f', 'ma27ad.f']
        libma27_src = ['ma27fact.f']
        pyma27_src = ['ma27_lib.c','nlpy_alloc.c','_pyma27.c']

        # Relevant files for building MA57 extension.
        ma57_src = ['ddeps.f', 'ma57d.f']
        pyma57_src = ['ma57_lib.c','nlpy_alloc.c','_pyma57.c']

        # Build PyMA27.
        ma27_sources  = [os.path.join(hsl_dir,name) for name in ma27_src]
        ma27_sources += [os.path.join('src',name) for name in libma27_src]

        config.add_library(
            name='nlpy_ma27',
            sources=ma27_sources,
            include_dirs=[hsl_dir,'src'],
            extra_info=blas_info,
            )

        config.add_extension(
            name='_pyma27',
            sources=[os.path.join('src',name) for name in pyma27_src],
            depends=[],
            libraries=['nlpy_ma27'],
            include_dirs=['src'],
            extra_info=blas_info,
            )

        # Prepare to build PyMA57.
        ma57_sources = [os.path.join(hsl_dir,'ma57d',name) for name in ma57_src]
        pyma57_sources = [os.path.join('src',name) for name in pyma57_src]

        # See if source files are present.
        build57 = True
        for src_file in ma57_sources:
            if not os.access(src_file, os.F_OK):
                build57 = False
                break

        if build57:
            config.add_library(
                name='nlpy_ma57',
                sources=ma57_sources,
                libraries=[metis_lib],
                library_dirs=[metis_dir],
                include_dirs=[hsl_dir,'src'],
                extra_info=blas_info,
                )

            config.add_extension(
                name='_pyma57',
                sources=pyma57_sources,
                libraries=[metis_lib,'nlpy_ma57'],
                library_dirs=[metis_dir],
                include_dirs=['src'],
                extra_info=blas_info,
                )

    if propack_dir is not None:
        propack_src = ['dlanbpro.F', 'dreorth.F', 'dgetu0.F', 'dsafescal.F',
                       'dblasext.F', 'dlansvd.F', 'printstat.F', 'dgemm_ovwr.F',
                       'dlansvd_irl.F', 'dbsvd.F', 'dritzvec.F', 'dmgs.risc.F',
                       'second.F']

        propack_sources = [os.path.join(propack_dir, 'double', f) for f in propack_src]
        pypropack_sources = [os.path.join('src', 'propack.pyf')]

        config.add_library(
            name='nlpy_propack',
            sources=propack_sources,
            include_dirs=os.path.join(propack_dir, 'double'),
            extra_info=[blas_info, lapack_info],
            )

        config.add_extension(
            name='_pypropack',
            sources=pypropack_sources,
            libraries=['nlpy_propack'],
            extra_info=[blas_info, lapack_info],
            f2py_options=f2py_options,
        )

        config.add_subpackage('scaling')

    config.make_config_py()
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
