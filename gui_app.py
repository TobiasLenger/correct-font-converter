import os
import sys
import threading
from flask import Flask, render_template, request, jsonify, send_file
import webview
from convert import convert_font

# Get absolute path for drag-and-drop safety
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# PyInstaller compatibility: When frozen, resources are in sys._MEIPASS
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # 'file' can be multiple
    if 'file' not in request.files:
         return jsonify({'success': False, 'error': 'No file part'})
         
    files = request.files.getlist('file')
    target_format = request.form.get('targetFormat', 'ttf')
    
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    import tempfile
    import shutil
    import zipfile
    import time

    try:
        downloads_path = os.path.expanduser("~/Downloads")
        converted_paths = []
        
        # Use a temp directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                if not file: continue
                # Basic safety
                safe_name = os.path.basename(file.filename)
                save_path = os.path.join(temp_dir, safe_name)
                file.save(save_path)
                
                # Convert
                out_path = convert_font(save_path, target_format)
                if out_path and os.path.exists(out_path):
                     converted_paths.append(out_path)
            
            if not converted_paths:
                return jsonify({'success': False, 'error': 'Conversion failed'})

            # If single file, save directly
            if len(converted_paths) == 1:
                src = converted_paths[0]
                fname = os.path.basename(src)
                final_path = os.path.join(downloads_path, fname)
                
                # Ensure unique if exists? Overwrite is probably fine as requested by user usually
                shutil.copy2(src, final_path)
                
                return jsonify({'success': True, 'file': final_path, 'message': 'Saved to Downloads'})
            
            else:
                # Multiple files -> ZIP
                timestamp = int(time.time())
                zip_name = f"converted_fonts_{timestamp}.zip"
                final_path = os.path.join(downloads_path, zip_name)
                
                with zipfile.ZipFile(final_path, 'w') as zf:
                    for cp in converted_paths:
                        zf.write(cp, os.path.basename(cp))
                        
                return jsonify({'success': True, 'file': final_path, 'message': 'Saved ZIP to Downloads'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_file')
def download_file():
    path = request.args.get('path')
    if not path or not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)

def start_server():
    app.run(port=54321, debug=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    webview.create_window('Correct Font Conversion Tool', 'http://127.0.0.1:54321', width=900, height=700, resizable=True, min_size=(800, 600), background_color='#0f0f12')
    webview.start()
