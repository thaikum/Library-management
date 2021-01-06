from cx_Freeze import setup, Executable

setup(
    name='Library-management',
    version='1.0.0',
    packages=['src'],
    url='',
    license='MIT',
    author='Fredrick',
    author_email='fredthaiku@gmail.com',
    description='A library management system',
    executables=[Executable("src/main.py")]
)
