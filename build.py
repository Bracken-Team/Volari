#!/usr/bin/env python3
"""
Volari Build Script
Builds the application for the current platform.

Usage:
    python build.py [--clean] [--dmg]

Options:
    --clean     Clean build directories before building
    --dmg       Create DMG file (macOS only)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "volari.spec"


def clean():
    """Remove build directories."""
    print("🧹 Cleaning build directories...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"   Removed {d}")


def install_requirements():
    """Install required packages."""
    print("📦 Checking dependencies...")
    try:
        import PyInstaller
        print(f"   PyInstaller {PyInstaller.__version__} ✓")
    except ImportError:
        print("   Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


def build():
    """Run PyInstaller build."""
    print(f"🔨 Building for {sys.platform}...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        str(SPEC_FILE)
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode != 0:
        print("❌ Build failed!")
        sys.exit(1)
    
    print("✅ Build completed!")


def create_dmg():
    """Create DMG file (macOS only)."""
    if sys.platform != "darwin":
        print("⚠️  DMG creation is only supported on macOS")
        return
    
    app_path = DIST_DIR / "Volari.app"
    dmg_path = DIST_DIR / "Volari.dmg"
    
    if not app_path.exists():
        print("❌ Volari.app not found. Run build first.")
        return
    
    print("📀 Creating DMG...")
    
    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()
    
    cmd = [
        "hdiutil", "create",
        "-volname", "Volari",
        "-srcfolder", str(app_path),
        "-ov",
        "-format", "UDZO",
        str(dmg_path)
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"✅ DMG created: {dmg_path}")
    else:
        print("❌ DMG creation failed!")


def print_result():
    """Print build results."""
    print("\n" + "=" * 50)
    print("📁 Build Output:")
    
    if sys.platform == "darwin":
        app = DIST_DIR / "Volari.app"
        dmg = DIST_DIR / "Volari.dmg"
        if app.exists():
            print(f"   macOS App: {app}")
        if dmg.exists():
            print(f"   macOS DMG: {dmg}")
    elif sys.platform == "win32":
        exe = DIST_DIR / "Volari.exe"
        if exe.exists():
            print(f"   Windows EXE: {exe}")
    else:
        binary = DIST_DIR / "volari"
        if binary.exists():
            print(f"   Linux Binary: {binary}")
    
    print("=" * 50)


def main():
    args = sys.argv[1:]
    
    print("=" * 50)
    print("🚀 Volari Build Script")
    print("=" * 50)
    
    if "--clean" in args:
        clean()
    
    install_requirements()
    build()
    
    if "--dmg" in args:
        create_dmg()
    
    print_result()


if __name__ == "__main__":
    main()
