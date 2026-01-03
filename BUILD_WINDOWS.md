# Building Volari for Windows

To build a standalone executable (`.exe`) for Windows, follow these steps.

**Note:** You must perform this build on a Windows machine. You cannot build a Windows `.exe` directly from macOS.

## Prerequisites

- Python 3.8+
- pip

## Build Instructions

1.  **Clone the repository** to your Windows machine.
2.  **Navigate** to the project directory in CMD or PowerShell.
3.  **Run the build script**:
    ```cmd
    cd windows
    build_exe.bat
    ```

    Or manually:
    ```cmd
    pip install -r requirements.txt
    pip install pyinstaller
    pyinstaller volari.spec --clean
    ```

## Output

The final executable will be generated at:
`dist\Volari.exe`

You can run this file directly to start the application.
