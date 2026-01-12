import PyInstaller.__main__
import os
import shutil

# 1. Clean previous build
if os.path.exists('build'): shutil.rmtree('build')
if os.path.exists('dist'): shutil.rmtree('dist')

# 2. Run PyInstaller
args = [
    'gui_app.py',
    '--name=FontConverter',
    '--onefile',
    '--windowed',  # Hide console (macOS .app)
    '--add-data=templates:templates',
    '--add-data=static:static',
    '--clean'
]

if os.path.exists('static/icon.icns'):
    args.append('--icon=static/icon.icns')

PyInstaller.__main__.run(args)

print("\n\nBuild Complete!")
print("Look in the 'dist' folder for your executable.")
