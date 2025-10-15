from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

download_status = {}

def clean_old_files():
    while True:
        time.sleep(3600)
        try:
            now = time.time()
            for filename in os.listdir(DOWNLOAD_FOLDER):
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    if now - os.path.getmtime(filepath) > 3600:
                        os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning files: {e}")

cleanup_thread = threading.Thread(target=clean_old_files, daemon=True)
cleanup_thread.start()

def download_instagram_video(url, download_id):
    try:
        download_status[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'filename': None,
            'error': None
        }
        
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{download_id}_%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(download_id):
                    download_status[download_id] = {
                        'status': 'completed',
                        'progress': 100,
                        'filename': file,
                        'error': None,
                        'title': info.get('title', 'Instagram Video')
                    }
                    return
        
        download_status[download_id]['status'] = 'error'
        download_status[download_id]['error'] = 'File not found'
        
    except Exception as e:
        download_status[download_id] = {
            'status': 'error',
            'progress': 0,
            'filename': None,
            'error': str(e)
        }

def progress_hook(d, download_id):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress = int((downloaded / total) * 100)
                download_status[download_id]['progress'] = progress
        except:
            pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Instagram Downloader API is running'})

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please provide URL'}), 400
        
        if 'instagram.com' not in url:
            return jsonify({'error': 'Only Instagram URLs are supported'}), 400
        
        download_id = str(uuid.uuid4())
        
        thread = threading.Thread(
            target=download_instagram_video,
            args=(url, download_id)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<download_id>')
def status(download_id):
    if download_id in download_status:
        return jsonify(download_status[download_id])
    return jsonify({'error': 'Download not found'}), 404

@app.route('/file/<filename>')
def get_file(filename):
    try:
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
