from flask import Flask, request, send_file, jsonify, render_template, Response, stream_with_context
import yt_dlp
import os
import uuid
import threading
import time
import subprocess
import glob
import requests
import zipfile
import shutil
import re

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
    """Download Instagram media (video, photo, story, carousel)"""
    try:
        download_status[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'filename': None,
            'error': None
        }
        
        if 'instagram.com' not in url:
            raise Exception("❌ فقط لینک‌های اینستاگرام پشتیبانی می‌شوند")
        
        print(f"Downloading Instagram media: {url}")
        
        # Try instaloader first (best for photos, stories, and carousel)
        try:
            import instaloader
            L = instaloader.Instaloader(
                download_videos=True,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                quiet=True
            )
            
            # Load cookies if available
            if os.path.exists('cookies.txt'):
                print("Loading session from cookies.txt")
                try:
                    with open('cookies.txt', 'r') as f:
                        for line in f:
                            if 'sessionid' in line:
                                parts = line.strip().split('\t')
                                if len(parts) >= 7:
                                    sessionid = parts[6]
                                    L.context._session.cookies.set('sessionid', sessionid, domain='.instagram.com')
                                    print("✅ Session loaded")
                                    break
                except Exception as cookie_err:
                    print(f"Cookie error: {cookie_err}")
            
            # Extract shortcode
            shortcode_match = re.search(r'/(p|reel|tv|stories)/([A-Za-z0-9_-]+)', url)
            if not shortcode_match:
                raise Exception("❌ لینک نامعتبر - فرمت صحیح: instagram.com/p/SHORTCODE")
            
            shortcode = shortcode_match.group(2)
            print(f"Downloading shortcode: {shortcode}")
            
            # Download to temp folder
            temp_folder = os.path.join(DOWNLOAD_FOLDER, download_id)
            os.makedirs(temp_folder, exist_ok=True)
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=temp_folder)
            
            # Find downloaded files (exclude metadata)
            files = [
                f for f in os.listdir(temp_folder) 
                if os.path.isfile(os.path.join(temp_folder, f)) 
                and not f.endswith('.txt') 
                and not f.endswith('.json')
                and not f.endswith('.xz')
            ]
            
            if not files:
                raise Exception("🚫 فایلی دانلود نشد")
            
            # Single file
            if len(files) == 1:
                source = os.path.join(temp_folder, files[0])
                ext = os.path.splitext(files[0])[1]
                final_name = f"{download_id}{ext}"
                dest = os.path.join(DOWNLOAD_FOLDER, final_name)
                shutil.move(source, dest)
                shutil.rmtree(temp_folder)
                
                download_status[download_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'filename': final_name,
                    'error': None,
                    'title': 'Instagram Media',
                    'type': 'single'
                }
                return
            
            # Multiple files - ZIP
            else:
                zip_name = f"{download_id}.zip"
                zip_path = os.path.join(DOWNLOAD_FOLDER, zip_name)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file in files:
                        file_path = os.path.join(temp_folder, file)
                        zipf.write(file_path, file)
                
                shutil.rmtree(temp_folder)
                
                download_status[download_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'filename': zip_name,
                    'error': None,
                    'title': f'Instagram Album ({len(files)} فایل)',
                    'type': 'multiple'
                }
                return
                
        except ImportError:
            print("⚠️ instaloader not installed, trying yt-dlp")
        except Exception as insta_error:
            error_str = str(insta_error)
            print(f"Instaloader error: {error_str}")
            
            # If it's a known instaloader error, don't try yt-dlp
            if 'login' in error_str.lower() or 'private' in error_str.lower():
                raise Exception("🔒 محتوا خصوصی - کوکی رو تازه کنید")
            elif 'فایلی' in error_str:
                raise insta_error
            # Otherwise try yt-dlp as fallback
        
        # Fallback: yt-dlp (better for videos)
        print("Trying yt-dlp as fallback")
        output_template = os.path.join(DOWNLOAD_FOLDER, f"{download_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }
        
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            downloaded_file = None
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(download_id) and os.path.isfile(os.path.join(DOWNLOAD_FOLDER, file)):
                    downloaded_file = file
                    break
            
            if downloaded_file:
                download_status[download_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'filename': downloaded_file,
                    'error': None,
                    'title': info.get('title', 'Instagram Media'),
                    'type': 'single'
                }
                return
            else:
                raise Exception("🚫 دانلود نشد - کوکی رو بررسی کنید")
        
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
            
            # Generate download ID for proxy
            download_id = str(uuid.uuid4())
            
            # Store info temporarily
            download_status[download_id] = {
                'video_url': video_url,
                'filename': f"{title}.{ext}",
                'title': title
            }
            
            return jsonify({
                'success': True,
                'download_id': download_id,
                'filename': f"{title}.{ext}"
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy-download/<download_id>')
def proxy_download(download_id):
    """Stream download through server with proper headers"""
    try:
        if download_id not in download_status:
            return jsonify({'error': 'Download not found'}), 404
        
        info = download_status[download_id]
        video_url = info['video_url']
        filename = info['filename']
        
        # Determine content type
        ext = os.path.splitext(filename)[1].lower()
        content_type = 'video/mp4' if ext in ['.mp4', '.mov'] else 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'application/octet-stream'
        
        # Stream the file from Instagram
        def generate():
            with requests.get(video_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
        
        # Clean up after download
        download_status.pop(download_id, None)
        
        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type
            }
        )
        
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
