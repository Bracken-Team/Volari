# Building Volari for Linux (AppImage)

To build a standalone AppImage for Linux, follow these steps. 

**Note:** You must perform this build on a Linux machine (e.g., Ubuntu 20.04 or 22.04) or inside a Docker container. You cannot build a Linux AppImage directly from macOS.

## Prerequisites

- Python 3.8+
- pip
- `wget` and `fuse` (required for appimagetool)

```bash
sudo apt update
sudo apt install python3-pip python3-venv wget fuse libfuse2
```

## Build Instructions

1.  **Clone the repository** to your Linux machine.
2.  **Navigate** to the project directory.
3.  **Run the build script**:

```bash
cd linux
./build_appimage.sh
```

## Output

The final AppImage will be generated in the `dist` folder:
`dist/Volari-x86_64.AppImage`

You can verify it by running:
```bash
chmod +x dist/Volari-x86_64.AppImage
./dist/Volari-x86_64.AppImage
```
