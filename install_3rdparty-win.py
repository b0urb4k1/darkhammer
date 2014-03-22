#!/usr/bin/env python

import os, sys, subprocess, inspect, shutil, glob, optparse

ROOTDIR = os.path.abspath(os.path.dirname(inspect.getframeinfo(inspect.currentframe())[0]))
WAFPATH = os.path.join(ROOTDIR, 'var', 'waf')
LIBDIR = ''
INCLUDEDIR = ''
PREFIX = ROOTDIR
ARCH = ''
MSVC = ''

def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def install_lua():
    lua_srcfiles = {\
        'x86-vc12': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win32_dll12_lib.zip/download',
        'x64-vc12': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win64_dll12_lib.zip/download',
        'x64-vc11': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win64_dll11_lib.zip/download',
        'x86-vc11': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win32_dll11_lib.zip/download',
        'x86-vc9': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win32_dll9_lib.zip/download',
        'x64-vc9': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win64_dll9_lib.zip/download',
        'x64-vc10': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win64_dll10_lib.zip/download',
        'x86-vc10': 'http://sourceforge.net/projects/luabinaries/files/5.2.1/Windows%20Libraries/Dynamic/lua-5.2.1_Win32_dll10_lib.zip/download'
        }
    
    luadir = os.path.join(ROOTDIR, '3rdparty', 'tmp', 'lua')
    libfile = os.path.join(LIBDIR, 'lua.lib')
    log('looking for lua...')
    if os.path.isfile(libfile):
        log('\t\tfound\n')
        return True
    log('\t\tnot found\n')        
    
    url = lua_srcfiles[ARCH + '-vc' + MSVC]
    log('downloading lua binaries from "http://sourceforge.net/projects/luabinaries"...\n')
    log('')

    os.makedirs(luadir, exist_ok=True)
    os.chdir(luadir)
    if os.system('wget -N --no-check-certificate {0}'.format(url)) != 0:
        os.chdir(ROOTDIR)
        return False
        
    # extract file name from url
    urlsplit = url.split('/')
    filename = ''
    for u in urlsplit:
        if '.zip' in u:
            filename = u
            break
            
    if os.system('unzip -o ' + filename) != 0:
        os.chdir(ROOTDIR)
        return False

    # copy important files
    shutil.copyfile('lua52.dll', libfile)
    shutil.copyfile('lua52.lib', os.path.join(LIBDIR, 'lua.lib'))

    # headers
    includes = os.path.join(INCLUDEDIR, 'lua')
    headers = glob.glob('include/*.h')
    os.makedirs(includes, exist_ok=True)
    for header in headers:
        shutil.copyfile(header, os.path.join(includes, os.path.basename(header)))

    os.chdir(ROOTDIR)
    return True

def install_assimp():
    log('looking for assimp...')
    if os.path.isfile(os.path.join(LIBDIR, 'assimp.lib')):
        log('\t\tfound\n')
        return True
    log('\t\tnot found\n')

    url = 'http://sourceforge.net/projects/assimp/files/assimp-3.0/assimp--3.0.1270-full.zip/download'
    log('downloading assimp binaries from "http://sourceforge.net/projects/assimp"...\n')

    assimpdir = os.path.join(ROOTDIR, '3rdparty', 'tmp', 'assimp')
    os.makedirs(assimpdir, exist_ok=True)
    os.chdir(assimpdir)
    if os.system('wget -N --no-check-certificate {0}'.format(url)) != 0:
        os.chdir(ROOTDIR)
        return False
        
    # extract file name from url
    urlsplit = url.split('/')
    filename = ''
    for u in urlsplit:
        if '.zip' in u:
            filename = u
            break
            
    if os.system('unzip -o ' + filename) != 0:
        os.chdir(ROOTDIR)
        return False
    
    os.chdir('assimp--3.0.1270-sdk')

    # copy important files
    # libs
    dirs = {'x64': 'assimp_release-dll_x64', 'x86': 'assimp_release-dll_win32'}
    d = dirs[ARCH]
    libs = glob.glob(os.path.join('bin', d, '*.dll'))
    libs.extend(glob.glob(os.path.join('lib', d, '*.lib')))
    for lib in libs:
        shutil.copyfile(lib, os.path.join(LIBDIR, os.path.basename(lib)))

    # headers
    includes = os.path.join(INCLUDEDIR, 'assimp')
    headers = glob.glob('include/assimp/*')
    os.makedirs(includes, exist_ok=True)
    for header in headers:
        if os.path.isfile(header):
            shutil.copyfile(header, os.path.join(includes, os.path.basename(header)))
    os.makedirs(os.path.join(includes, 'Compiler'), exist_ok=True)
    headers = glob.glob('include/assimp/Compiler/*')
    for header in headers:
        shutil.copyfile(header, os.path.join(includes, 'Compiler', os.path.basename(header)))

    os.chdir(ROOTDIR)
    return True

def install_glfwext():
    log('looking for glfwext...')
    if os.path.isfile(os.path.join(LIBDIR, 'glfwext.lib')):
        log('\t\tfound\n')
        return True
    log('\t\tnot found\n')

    url = 'https://github.com/septag/glfw/archive/master.zip'
    log('downloading glfwext source from "https://github.com/septag/glfw"...\n')

    glfwdir = os.path.join(ROOTDIR, '3rdparty', 'tmp', 'glfwext')
    os.makedirs(glfwdir, exist_ok=True)
    os.chdir(glfwdir)
    if os.system('wget -N --no-check-certificate {0}'.format(url)) != 0:
        os.chdir(ROOTDIR)
        return False
    if os.system('unzip -o master') != 0:
        os.chdir(ROOTDIR)
        return False

    os.chdir('glfw-master')
    if os.system('python {0} configure build install'.format(WAFPATH)) != 0:
        os.chdir(ROOTDIR)
        return False

    # copy important files
    # libs
    libs = ['lib/glfwext.dll', 'build/src/glfwext.lib']
    for lib in libs:
        shutil.copyfile(lib, os.path.join(LIBDIR, os.path.basename(lib)))

    # headers
    includes = os.path.join(INCLUDEDIR, 'GLFWEXT')
    headers = glob.glob('include/GLFW/*.h')
    os.makedirs(includes, exist_ok=True)
    for header in headers:
        shutil.copyfile(header, os.path.join(includes, os.path.basename(header)))

    os.chdir(ROOTDIR)
    return True

def install_glew():
    log('looking for glew...')
    if os.path.isfile(os.path.join(LIBDIR, 'glew.lib')):
        log('\t\tfound\n')
        return True
    log('\t\tnot found\n')

    url = 'https://sourceforge.net/projects/glew/files/glew/1.10.0/glew-1.10.0-win32.zip/download'
    log('downloading glew binaries from "https://sourceforge.net/projects/glew"...\n')

    glewdir = os.path.join(ROOTDIR, '3rdparty', 'tmp', 'glew')
    os.makedirs(glewdir, exist_ok=True)
    os.chdir(glewdir)
    if os.system('wget -N --no-check-certificate {0}'.format(url)) != 0:
        os.chdir(ROOTDIR)
        return False
        
    # extract file name from url
    urlsplit = url.split('/')
    filename = ''
    for u in urlsplit:
        if '.zip' in u:
            filename = u
            break        
    if os.system('unzip -o ' + filename) != 0:
        os.chdir(ROOTDIR)
        return False

    dirs = glob.glob('*')
    for d in dirs:
        if os.path.isdir(d):
            os.chdir(d)
            break

    # copy important files
    dirs = {'x64': 'x64', 'x86': 'Win32'}
    d = dirs[ARCH]
    # libs    
    libs = [os.path.join('bin', 'Release', d, 'glew32.dll'), 
        os.path.join('lib', 'Release', d, 'glew32.lib')]
    for lib in libs:
        shutil.copyfile(lib, os.path.join(LIBDIR, 'glew' + os.path.splitext(lib)[-1]))

    # headers
    includes = os.path.join(INCLUDEDIR, 'GL')
    headers = glob.glob('include/GL/*.h')
    os.makedirs(includes, exist_ok=True)
    for header in headers:
        shutil.copyfile(header, os.path.join(includes, os.path.basename(header)))

    os.chdir(ROOTDIR)
    return True

def install_efsw():
    log('looking for efsw...')
    if os.path.isfile(os.path.join(LIBDIR, 'efsw.lib')):
        log('\t\tfound\n')
        return True
    log('\t\tnot found\n')

    url = 'https://bitbucket.org/sepul/efsw/get/9e7b94e606c4.zip'
    log('downloading efsw source from "https://bitbucket.org/sepul/efsw"...\n')

    efswdir = os.path.join(ROOTDIR, '3rdparty', 'tmp', 'efsw')
    os.makedirs(efswdir, exist_ok=True)
    os.chdir(efswdir)
    if os.system('wget -N --no-check-certificate {0}'.format(url)) != 0:
        os.chdir(ROOTDIR)
        return False
    if os.system('unzip -o ' + os.path.basename(url)) != 0:
        os.chdir(ROOTDIR)
        return False

    dirs = glob.glob('*')
    for d in dirs:
        if os.path.isdir(d):
            os.chdir(d)
            break

    if os.system('python {0} configure build install'.format(WAFPATH)) != 0:
        os.chdir(ROOTDIR)
        return False

    # copy important files
    # libs
    libs = ['lib/efsw.dll', 'build/release/efsw.lib']
    for lib in libs:
        shutil.copyfile(lib, os.path.join(LIBDIR, os.path.basename(lib)))

    # headers
    includes = os.path.join(INCLUDEDIR, 'efsw')
    headers = glob.glob('include/efsw/*.h*')
    os.makedirs(includes, exist_ok=True)
    for header in headers:
        shutil.copyfile(header, os.path.join(includes, os.path.basename(header)))

    os.chdir(ROOTDIR)
    return True

def main():
    parser = optparse.OptionParser()
    parser.add_option('--prefix', action='store', type='string', dest='PREFIX',
        help='prefix path for existing and to be installed libs', default='')
    parser.add_option('--msvc', action='store', type='choice', choices=['9', '10', '11', '12'], 
        dest='MSVC', help='define visual studio version (active compiler)')
    parser.add_option('--arch', action='store', type='choice', choices=['x86', 'x64'], 
        dest='ARCH', help='define target architecture that you want to build')
        
    (options, args) = parser.parse_args()
    if not options.ARCH:
        parser.error('--arch argument is not given')
    if not options.MSVC:
        parser.error('--msvc argument is not given')
    
    global LIBDIR, INCLUDEDIR, PREFIX, MSVC, ARCH
    PREFIX = os.path.abspath(options.PREFIX)
    LIBDIR = os.path.join(PREFIX, 'lib')
    INCLUDEDIR = os.path.join(PREFIX, 'include')
    ARCH = options.ARCH
    MSVC = options.MSVC

    log('library install path: ' + LIBDIR + '\n')
    log('include install path: ' + INCLUDEDIR + '\n')

    os.makedirs(INCLUDEDIR, exist_ok=True)
    os.makedirs(LIBDIR, exist_ok=True)

    if not install_lua():
        log('error: could not install lua\n')
        return False
    
    if not install_assimp():
        log('error: could not install assimp\n')
        return False

    if not install_glfwext():
        log('error: could not install glfwext\n')
        return False

    if not install_glew():
        log('error: could not install glew\n')
        return False

    if not install_efsw():
        log('error: could not install efsw\n')
        return False
    
    log('ok, ready for build.\n')

r = main()
if r:    sys.exit(0)
else:    sys.exit(-1)