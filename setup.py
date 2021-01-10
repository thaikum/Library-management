from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "PyQt5",
        "qtawesome",
        "pyqtgraph",
        "numpy"
    ],
    "excludes": [
        'venv',
        '.idea',
        'tkinter',
        "data",
        "UI"
    ],
    "include_files": [
        "src/main.db"
    ]

}

if 'bdist_msi' in sys.argv:
    sys.argv += ['--initial-target-dir', 'c:\Program Files\Lib-Management']

setup(
    name='Library-management',
    version='1.0.0',
    packages=['src'],
    url='',
    license='MIT',
    author='Fredrick',
    author_email='fredthaiku@gmail.com',
    description='A library management system',
    options={"build_exe": build_exe_options},
    executables=[Executable("src/main.py", base='Win32Gui')]
)
