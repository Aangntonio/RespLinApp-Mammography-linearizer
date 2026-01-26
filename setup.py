#progrma para convertir a exe

from cx_Freeze import setup, Executable



# os.environ['TCL_LIBRARY'] = r'C:\Users\Eduardo\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Users\Eduardo\AppData\Local\Programs\Python\Python36\tcl\tk8.6'


base = 'Win32GUI'    

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "RespLin App",                 # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]app_estilizada.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),
                  
    ("ProgramMenuShortcut",        # Shortcut
     "ProgramMenuFolder",          # Directory_
     "RespLin App",     # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]app_estilizada.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     ),

    ]

msi_data = {"Shortcut": shortcut_table}



executables = [Executable("app_estilizada.py", base=base,icon="icono.ico")]

packages = [ "wx", "numpy", "pydicom", "matplotlib", "pandas", "sklearn", 'scipy'] #aquí se deben poner los paquetes que se importan

includefiles = ['Modulo_FR.py', 'icono.ico']
# namespacepackages=['mpl_toolkits']

# excludes = ['gtk','PyQt4', 'PyQt5', 'Tkinter', 'tkinter', 'pandas', 'xlrd', 'whichcraft', 'sympy',
#               'toolz', 'sklearn', 'scikit-learn', 's<cikit-image', 'pywin32', 'pywin32-ctypes',
#           'pyserial', 'pydicom', 'altgraph', 'appdirs', 'auto-py-to-exe', 'bottle','bottle-websocket',
#             'cffi', 'cloudpickle', 'cx-Freeze', 'dask', 'Pillow', 'macholib', 'pyInstaller', 
#               'PyQt5-sip', 'pip', 'setuptools', 'xml', 'xmlrpc', 'pkg_resources']
excludes = [
    # --- Otros toolkits de GUI que no se usan ---
    "tkinter", "PyQt5", "PyQt4", "PySide", "gtk",

    # --- Herramientas de desarrollo, construcción y empaquetado ---
    "setuptools", "pkg_resources", "distutils", "lib2to3", "Cython",
    "cx_Freeze", "cx_Logging", "lief", "packaging", "cabarchive",

    # --- Módulos de prueba y documentación que no son necesarios en producción ---
    "unittest", "doctest", "test", "pydoc_data", "pydoc",
    # Excluir los módulos de prueba de las librerías científicas ahorra mucho espacio
    "numpy.core.tests",
    "pandas.tests",
    "scipy.linalg.tests",
    "sklearn.tests",

    # --- Librerías completas del entorno que no son dependencias directas ---
    "pygame",
    "opencv-python", "cv2",  # 'cv2' es como se importa opencv-python
    "reportlab",
    "striprtf",
    "filelock",
    "pillow",  # Se puede excluir si solo usas wxPython para imágenes.
               # Si matplotlib la necesita para guardar en formatos como JPG/PNG,
               # considera quitarla de esta lista.

    # --- Módulos de la librería estándar que rara vez se usan en apps de escritorio ---
    "email", "http", "xmlrpc", "pdb", "zipfile", "tarfile",
]

options = {
    'build_exe': {    
        'packages':packages,
        'include_files':includefiles,
        # "namespace_packages":namespacepackages,
        #'excludes':excludes,
        "optimize":0,  #Compresion del archivo
    },
    'bdist_msi': {
            'data': msi_data,
            }    
}

setup(
    name = "RespLin App",
    options = options,
    version = "2.0",
    description = 'Programa para linerizacion de imagenes DICOM',	
    executables = executables
)