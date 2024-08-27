# -*- mode: python -*-
import os
import pymzml
import datetime
import platform
import zipfile
import time
import fnmatch
from multiprocessing import freeze_support
from os import listdir
from PyInstaller import compat
import matplotlib
import sys
import hashlib
import shutil


def hashfile(path):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha256.update(data)

    md5hash = md5.hexdigest()
    sha256hash = sha256.hexdigest()

    print("MD5: {0}".format(md5hash))
    print("SHA256: {0}".format(sha256hash))

    return md5hash, sha256hash

freeze_support()


def dir_files(path, rel, type='DATA'):
    ret = []
    for p, d, f in os.walk(path):
        relpath = p.replace(path, '')[1:]
        for fname in f:
            ret.append((os.path.join(rel, relpath, fname),
                        os.path.join(p, fname), type))
    return ret


# Some basics
tstart = time.perf_counter()
system = platform.system()
date = datetime.date.today().strftime("%y%m%d")

# Create names of files and directories
exename = 'GUI_UniDec'
if system == "Windows":
    exename += ".exe"
outputdir = 'UniDec_' + system
zipdirectory = outputdir + "_" + date + ".zip"


hiddenimportslist=['scipy.special._ufuncs_cxx', 'scipy.linalg.cython_blas', 'scipy.linalg.cython_lapack',
                 'scipy.special.cython_special','numpy',
                 'scipy._lib.messagestream','clr', 'pythonnet',
                 'encodings', 'encodings.__init__',
                 'packaging', 'packaging.version', 'packaging.specifiers',
                 'pubsub', 'pubsub.core', 'matplotlib.backends.backend_ps', 'matplotlib.backends.backend_pdf',
             ]


excludeslist = ['IPython', 'statsmodels', 'pyopenms', 'sklearn',
                       'GdkPixbuf', 'pyQT4', 'pygobject', 'pygtk', 'pyside', 'PySide2', 'shiboken2', 'PyQt5']

# Analysis of packages
a = Analysis(['unidec\\Launcher.py'],
             pathex=[os.getcwd()],
             excludes=excludeslist,
             hiddenimports=hiddenimportslist,
             hookspath=None,
             runtime_hooks=None)

# Add extra things
if system == "Windows":
    a.datas += [('UniDec.exe', 'unidec\\bin\\UniDec.exe', 'DATA')]
    a.datas += [('readme.md', 'readme.md', 'DATA')]
    a.datas += [('LICENSE', 'LICENSE', 'DATA')]
    a.datas += [('CDCReader.exe', 'unidec\\bin\\CDCReader.exe', 'DATA')]
    a.datas += [('h5repack.exe', 'unidec\\bin\\h5repack.exe', 'DATA')]
    a.datas += [('unimod.sqlite', 'unidec\\bin\\unimod.sqlite', 'DATA')]
    #a.datas += [('numpy/DLLs', 'unidec\\bin\\mkl_def.2.dll', 'BINARY')]
    #a.datas += [('numpy/DLLs', 'unidec\\bin\\mkl_avx2.2.dll', 'BINARY')]
    #a.datas += [('numpy/DLLs', 'unidec\\bin\\mkl_intel_thread.2.dll', 'BINARY')]
    a.datas += [('pymzml\\version.txt', compat.base_prefix + '\\Lib\\site-packages\\pymzml\\version.txt', 'DATA')]
    a.datas += [('massql\\msql.ebnf', compat.base_prefix + '\\Lib\\site-packages\\massql\\msql.ebnf', 'DATA')]

    # Copy over all the DLLs from the bin folder
    for file in os.listdir('unidec\\bin'):
        if fnmatch.fnmatch(file, '*.dll'):
            add = [(file, 'unidec\\bin\\' + file, 'BINARY')]
            a.datas += add
            # print add

    a.datas += [('RawFileReaderLicense.doc', 'unidec\\modules\\thermo_reader\\RawFileReaderLicense.doc', 'BINARY')]
    a.datas += [('ThermoFisher.CommonCore.Data.dll', 'unidec\\modules\\thermo_reader\\ThermoFisher.CommonCore.Data.dll', 'BINARY')]
    a.datas += [('ThermoFisher.CommonCore.RawFileReader.dll', 'unidec\\modules\\thermo_reader\\ThermoFisher.CommonCore.RawFileReader.dll', 'BINARY')]
    a.datas += [('ThermoFisher.CommonCore.MassPrecisionEstimator.dll', 'unidec\\modules\\thermo_reader\\ThermoFisher.CommonCore.MassPrecisionEstimator.dll', 'BINARY')]
    a.datas += [('ThermoFisher.CommonCore.BackgroundSubtraction.dll', 'unidec\\modules\\thermo_reader\\ThermoFisher.CommonCore.BackgroundSubtraction.dll', 'BINARY')]
    a.datas += [('Waters_MassLynxSDK_EULA.txt', 'unidec\\bin\\Waters_MassLynxSDK_EULA.txt', 'DATA')]
elif system == "Linux":
    a.datas += [('unideclinux', 'unidec/bin/unideclinux', 'BINARY')]

a.datas += [('cacert.pem', os.path.join('unidec\\bin', 'cacert.pem'), 'DATA')]
a.datas += [('logo.ico', 'unidec\\bin\\logo.ico', 'DATA')]
a.datas += [('mass_table.csv', 'unidec\\bin\\mass_table.csv', 'DATA')]
a.datas += [('metaunidec/images/allButton.png', 'metaunidec\\images\\allButton.png', 'DATA')]
a.datas += [('metaunidec/images/peakRightClick.png', 'metaunidec\\images\\peakRightClick.png', 'DATA')]
a.datas += [('metaunidec/images/rightClick.png', 'metaunidec\\images\\rightClick.png', 'DATA')]
a.datas += [('UniDecLogoMR.png', 'unidec\\bin\\UniDecLogoMR.png', 'DATA')]

a.datas.extend(dir_files(os.path.join(os.path.dirname(pymzml.__file__), 'obo'), 'obo'))

a.datas.extend(dir_files("unidec\\bin\\multiplierz", 'multiplierz'))

a.datas.extend(dir_files("unidec\\bin\\Presets", 'Presets'))
a.datas.extend(dir_files("unidec\\bin\\Example Data", 'Example Data'))
a.datas.extend(dir_files(compat.base_prefix + '\\Lib\\site-packages\\matchms\\data', "matchms\\data"))

mkldir = compat.base_prefix + "/Lib/site-packages/numpy/DLLs"
newdir = "numpy/DLLs"
a.datas.extend(dir_files(mkldir, newdir, type="BINARY"))
#a.datas.extend(
#    [(mkldir + "/" + mkl, newdir, 'BINARY') for mkl in listdir(mkldir) if mkl.startswith('mkl_') or mkl.startswith('libio')])

rdkitlibs = compat.base_prefix + "/Lib/site-packages/rdkit.libs"
a.datas.extend(dir_files(rdkitlibs, ''))

# Assemble and build
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=exename,
          debug=False,
          strip=None,
          upx=False,
          console=True, icon='unidec\\bin\\logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=False,
               name=outputdir)

path = "C:\\Python\\UniDec3\\dist\\UniDec_Windows\\GUI_UniDec.exe"
import subprocess

dst = "C:\\Python\\UniDec3\\dist\\UniDec_Windows\\obo"
src = "C:\\Python\\UniDec3\\dist\\UniDec_Windows\\_internal\\obo"

shutil.copytree(src, dst)

print("Testing Software...", path)

out = subprocess.call(path)
if out != 0:
    exit()

# exit()

print("Zipping...")
# Zip up the final file
os.chdir("dist")

zipf = zipfile.ZipFile(zipdirectory, 'w')
for root, dirs, files in os.walk(outputdir):
    for file in files:
        zipf.write(os.path.join(root, file), compress_type=zipfile.ZIP_DEFLATED)
zipf.close()
print("Zipped to", zipdirectory, "from", outputdir)

hashfile(zipdirectory)

tend = time.perf_counter()
print("Build Time: %.2gm" % ((tend - tstart) / 60.0))
