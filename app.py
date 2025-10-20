from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os
import uuid
import threading
import time
import subprocess
import glob

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
        
        # Check if cookies file exists or create from hardcoded cookies
        cookie_file = None
        if not os.path.exists('cookies.txt'):
            # Create cookies.txt with proper tab-separated format
            cookies_content = """# Netscape HTTP Cookie File
.instagram.com\tTRUE\t/\tTRUE\t1795082016\tdatr\tG2_vaD9tYtVx4SqkKJzzDf7z
.instagram.com\tTRUE\t/\tTRUE\t1792058016\tig_did\t9BB8BF56-463E-4711-8023-82D1153067DB
.instagram.com\tTRUE\t/\tTRUE\t1761135945\twd\t1444x810
.instagram.com\tTRUE\t/\tTRUE\t1761135945\tdpr\t1.5625
.instagram.com\tTRUE\t/\tTRUE\t1795090337\tmid\taO-PmQALAAGXneWYfU1Ia0VnmY6O
.instagram.com\tTRUE\t/\tTRUE\t1792066347\tig_nrcb\t1
.instagram.com\tTRUE\t/\tTRUE\t1795091132\tcsrftoken\tEVtrQdYv20xhB9dpQ2g1V4jLeZ7VyvuL
.instagram.com\tTRUE\t/\tTRUE\t1768307132\tds_user_id\t8756404558
.instagram.com\tTRUE\t/\tTRUE\t1792067114\tsessionid\t8756404558%3AUqZZ5S2dFGHSAm%3A4%3AAYhd4dwWJu8UNdgSlos_Ab827h7fZ-Mwo6TS5IPTgA
.instagram.com\tTRUE\t/\tTRUE\t1795091123\tps_l\t1
.instagram.com\tTRUE\t/\tTRUE\t1795091123\tps_n\t1
.instagram.com\tTRUE\t/\tTRUE\t0\trur\t\"LDC\\0548756404558\\0541792067127:01fecd0c9e281a40218e69b8c1c8f1e9aedef7b3aa60dacc24733f4ddec6505fa34192a5\"
"""
            with open('cookies.txt', 'w') as f:
                f.write(cookies_content)
            print("Created cookies.txt file")
        
        cookie_file = 'cookies.txt' if os.path.exists('cookies.txt') else None
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'extractor_args': {
                'generic': {
                    'impersonate': ['chrome']
                }
            },
            'referer': url,
            'geo_bypass': True,
            'check_certificate': False,
        }
        
        # Add cookies if available
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file
            print(f"Using cookies from {cookie_file}")
        
        try:
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
        except Exception as yt_error:
            # Fallback to gallery-dl for Instagram
            if 'instagram.com' in url:
                print(f"yt-dlp failed, trying gallery-dl: {yt_error}")
                try:
                    gallery_output = os.path.join(DOWNLOAD_FOLDER, download_id)
                    # Build gallery-dl command
                    cmd = ['gallery-dl', '--dest', DOWNLOAD_FOLDER, '--filename', f'{download_id}_{{filename}}.{{extension}}']
                    
                    # Add cookies if available
                    if os.path.exists('cookies.txt'):
                        cmd.extend(['--cookies', 'cookies.txt'])
                        print("Using cookies for gallery-dl")
                    
                    cmd.append(url)
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        for file in os.listdir(DOWNLOAD_FOLDER):
                            if file.startswith(download_id):
                                download_status[download_id] = {
                                    'status': 'completed',
                                    'progress': 100,
                                    'filename': file,
                                    'error': None,
                                    'title': 'Instagram Media'
                                }
                                return
                    raise Exception(f"gallery-dl failed: {result.stderr}")
                except Exception as gallery_error:
                    raise Exception(f"Both yt-dlp and gallery-dl failed. yt-dlp: {yt_error}, gallery-dl: {gallery_error}")
            else:
                raise yt_error
        
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

@app.route('/service-worker.js')
def service_worker():
    return send_file('static/service-worker.js', mimetype='application/javascript')

@app.route('/share')
def share():
    # دریافت URL از پارامترهای share
    shared_url = request.args.get('url', '') or request.args.get('text', '')
    return render_template('index.html', shared_url=shared_url)

@app.route('/thumbnail', methods=['POST'])
def get_thumbnail():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url or 'instagram.com' not in url:
            return jsonify({'error': 'Invalid URL'}), 400
        
        # استخراج اطلاعات با yt-dlp
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'extractor_args': {
                'generic': {
                    'impersonate': ['chrome']
                }
            },
        }
        
        # بررسی وجود کوکی
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            thumbnail = info.get('thumbnail')
            title = info.get('title', 'Instagram Media')
            
            return jsonify({
                'thumbnail': thumbnail,
                'title': title
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Instagram Downloader API is running'})

@app.route('/get-direct-link', methods=['POST'])
def get_direct_link():
    """Get direct download link without downloading to server"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'Please provide URL'}), 400
        
        if 'instagram.com' not in url:
            return jsonify({'error': 'Only Instagram URLs are supported'}), 400
        
        # Extract info without downloading
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'no_warnings': True,
            'extractor_args': {
                'generic': {
                    'impersonate': ['chrome']
                }
            },
        }
        
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get the best quality video URL
            video_url = info.get('url')
            title = info.get('title', 'Instagram Media')
            ext = info.get('ext', 'mp4')
            
            return jsonify({
                'success': True,
                'direct_url': video_url,
                'title': title,
                'filename': f"{title}.{ext}"
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
