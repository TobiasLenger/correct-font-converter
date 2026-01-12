# Correct Font Conversion Tool

<div align="center">

![App Screenshot](https://via.placeholder.com/800x400?text=Preview+of+Your+App+Here) 

**"Can't install webfont that you just stole from website on your expensive-ass mac? Convert it here correctly"**

</div>

## 🚀 Overview
**Correct Font Conversion Tool** is a robust, clean, and honest GUI application designed to fix and convert problematic web fonts (WOFF, WOFF2) into installable desktop fonts (TTF, OTF). 

It specifically addresses issues where fonts extracted from the web fail to install on macOS due to metadata errors, "hostile" web-specific tables, or bad checksums.

## ✨ Features
- **Batch Processing**: Drag & drop multiple files at once.
- **Smart Conversion**: Automatically fixes name tables, permissions, and checksums to ensure compatibility with macOS Font Book and Windows.
- **Support**: Input `WOFF`, `WOFF2`, `TTF`, `OTF` -> Output `TTF`, `OTF`, `WOFF`, `WOFF2`.
- **Live Preview**: See what the font looks like before converting (supports Latin, Cyrillic, Chinese, Japanese, Arabic).
- **No Installation Needed**: Runs as a standalone `.app` on macOS.

## 📦 Installation
### macOS (Apple Silicon)
1. Download the latest release (or use the `dist/FontConverter.app.zip` if you built it).
2. Unzip the file.
3. Move **Correct Font Converter.app** to your Applications folder.
4. *First Run*: Right-click the app -> **Open** -> Click **Open** (required for unsigned apps).

## 🛠 Building from Source
If you want to modify the code or build for Intel Macs/Windows:

### Prerequisites
- Python 3.9+
- `pip`

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/correct-font-converter.git
cd correct-font-converter

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python3 gui_app.py
# or
./start_gui.sh
```

### 3. Build Standalone App
To create a frozen `.app` or `.exe`:
```bash
python3 build_macos.py
# The output will be in the /dist folder
```

## 📜 How it Works
1. **Decompression**: Expands WOFF2/WOFF into raw OpenType structure.
2. **Sanitization**: Uses `fontTools` and `XML` intermediate representation to strip garbage data.
3. **Metadata Fix**: Reconstructs the `name` table to be compatible with Mac OS restrictions.
4. **Recompilation**: Compiles back to clean binary TTF/OTF.

## 📄 License
MIT License. Use responsibly.
