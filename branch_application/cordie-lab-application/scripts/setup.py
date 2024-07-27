import os
from cx_Freeze import setup, Executable

# os.environ["PYTHONTZPATH"] = "lib\dateutil"

bdist_msi_options = {
    "add_to_path": True,
    "environment_variables": [
        ("PYTHONTZPATH", "[TARGETDIR]dateutil\\zoneinfo", "1", "TARGETDIR")
    ],    
}

build_exe_options = {"include_msvcr": True}

executables = (
    [
        Executable(
            "hello.py",
            copyright="Copyright (C) 2023 Dylan Powers",
            shortcut_name="Cordie Lab",
            shortcut_dir="CordieLab",
        ),
    ],
)

setup(
    name="cordie-lab",
    version="0.1",
    description="My GUI application!",
    executables=[Executable("server.py")],
    # executables=executables,
    data_files=[('.', ['C:\Users\powersd\Documents\Class\Spring 22-23\\\'Data Science Practicum\'\cordie-lab\scripts\build\exe.win-amd64-3.10\lib\dateutil'])],
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
)
