#!/bin/bash
set -e

# Build Volari AppImage
# NOTE: This script must be run on a Linux machine (Ubuntu 20.04/22.04 recommended)

# Ensure dependencies are installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 could not be found, please install python3-pip"
    exit 1
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "Building executable with PyInstaller..."
rm -rf dist/volari build/volari
pyinstaller volari.spec --clean

# Setup AppDir
echo "Setting up AppDir..."
mkdir -p dist/AppDir/usr/bin
mkdir -p dist/AppDir/usr/share/applications
mkdir -p dist/AppDir/usr/share/icons/hicolor/256x256/apps

# Copy binaries
cp -r dist/volari/* dist/AppDir/usr/bin/

# Copy desktop file and icon
cp linux/volari.desktop dist/AppDir/usr/share/applications/
cp volatility_gui/resources/volari_icon.png dist/AppDir/usr/share/icons/hicolor/256x256/apps/volari.png
cp volatility_gui/resources/volari_icon.png dist/AppDir/volari.png

# Create AppRun
cat > dist/AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/volari" "$@"
EOF
chmod +x dist/AppDir/AppRun

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Creating AppImage..."
export ARCH=x86_64
./appimagetool-x86_64.AppImage dist/AppDir dist/Volari-x86_64.AppImage

echo "Build complete! AppImage is located at dist/Volari-x86_64.AppImage"
