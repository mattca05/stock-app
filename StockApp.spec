# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Copies your .env next to the exe at runtime
        ('.env', '.'),
    ],
    hiddenimports=[
        # PyQt6
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',

        # SQLAlchemy — dialect must be explicit
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlalchemy.orm',
        'sqlalchemy.sql.default_comparator',

        # scipy optimizer backend
        'scipy.optimize',
        'scipy.optimize._minimize',
        'scipy.optimize._slsqp_py',
        'scipy._lib.messagestream',

        # scikit-learn Ledoit-Wolf
        'sklearn.covariance',
        'sklearn.covariance._shrunk_covariance',
        'sklearn.utils._cython_blas',
        'sklearn.utils._weight_vector',
        'sklearn.utils._bunch',

        # numpy internals
        'numpy.core._methods',
        'numpy.lib.format',

        # python-dotenv
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Trim unused heavy packages to reduce exe size
        'matplotlib',
        'IPython',
        'jupyter',
        'tkinter',
        'test',
        'unittest',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='StockApp-1.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # UPX can corrupt these — always exclude
        'vcruntime140.dll',
        'python3*.dll',
        'Qt6*.dll',
    ],
    runtime_tmpdir=None,
    console=False,          # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Replace with 'assets/icon.ico' if you have one
)