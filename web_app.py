import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
import re
import subprocess

# إعدادات صفحة الموقع
st.set_page_config(page_title="YouTube Downloader PRO", page_icon="⬇️", layout="centered")

# --- فحص محركات النظام (Node.js و FFmpeg) في القائمة الجانبية ---
with st.sidebar:
    st.write("### ⚙️ حالة أدوات السيرفر")
    try:
        node_version = subprocess.check_output(["node", "-v"]).decode().strip()
        st.success(f"✅ محرك فك التشفير (Node.js) يعمل: {node_version}")
    except Exception:
        st.error("❌ تحذير: Node.js غير مثبت! يرجى عمل Rebuild أو Delete ثم Create للتطبيق ليقرأ ملف packages.txt.")
        
    try:
        ffmpeg_version = subprocess.check_output(["ffmpeg", "-version"]).decode().split('\n')[0].split()[2]
        st.success(f"✅ محرك دمج الصوت (FFmpeg) يعمل: {ffmpeg_version}")
    except Exception:
        st.error("❌ تحذير: FFmpeg غير مثبت! يرجى التأكد من ملف packages.txt.")

# --- إعدادات اللغة ---
if 'language' not in st.session_state:
    st.session_state['language'] = 'English'

def toggle_language():
    if st.session_state['language'] == 'English':
        st.session_state['language'] = 'العربية'
    else:
        st.session_state['language'] = 'English'

lang = st.session_state['language']
text = {
    "English": {
        "title": "🎬 YouTube Downloader PRO",
        "dev": "**Developed by George Gamal**",
        "mode_label": "Choose Download Mode:",
        "mode_single": "Single Video",
        "mode_playlist": "Complete Playlist",
        "mode_batch": "Multiple Videos (Batch)",
        "url_label": "🔗 Paste your YouTube URL here:",
        "url_area_label": "🔗 Paste your URLs here (each on a new line):",
        "zip_name_label": "📦 Custom ZIP File Name (Optional):",
        "format_label": "Choose Format:",
        "vid_format": "Video (MP4)",
        "aud_format": "Audio (MP3)",
        "codec_label": "Select Video Codec:",
        "codec_h264": "Standard (H.264) - Best for old devices",
        "codec_av1": "Modern (AV1) - Best quality & smallest size",
        "vid_quality": "Select Video Quality:",
        "aud_quality": "Select Audio Quality (kbps):",
        "btn_download": "🚀 Start Download",
        "warn_url": "⚠️ Please enter a valid URL first!",
        "show_logs": "🛠️ Show/Hide Logs",
        "log_start": "Starting process...\n",
        "downloading": "Downloading...",
        "speed": "Speed",
        "eta": "ETA",
        "file": "File",
        "of": "of",
        "finish_process": "✅ Download finished, processing...",
        "zipping": "📦 Compressing files into a ZIP...",
        "success_all": "🎉 All Processing Completed Successfully!",
        "btn_save_single": "💾 Click here to save the file",
        "btn_save_zip": "💾 Click here to save the ZIP file",
        "error": "❌ An error occurred:",
        "lang_btn": "🌐 تغيير للغة العربية"
    },
    "العربية": {
        "title": "🎬 محمل يوتيوب برو (PRO)",
        "dev": "**تطوير: جورج جمال**",
        "mode_label": "اختر وضع التحميل:",
        "mode_single": "فيديو واحد",
        "mode_playlist": "قائمة تشغيل (Playlist)",
        "mode_batch": "مجموعة روابط متعددة",
        "url_label": "🔗 ضع رابط اليوتيوب هنا:",
        "url_area_label": "🔗 ضع الروابط هنا (كل رابط في سطر جديد):",
        "zip_name_label": "📦 اسم ملف الـ ZIP (اختياري):",
        "format_label": "اختر الصيغة:",
        "vid_format": "فيديو (MP4)",
        "aud_format": "صوت (MP3)",
        "codec_label": "اختر تكويد الفيديو (Codec):",
        "codec_h264": "عادي (H.264) - الأفضل للأجهزة القديمة",
        "codec_av1": "حديث (AV1) - أعلى جودة وأقل مساحة",
        "vid_quality": "اختر جودة الفيديو:",
        "aud_quality": "اختر جودة الصوت (kbps):",
        "btn_download": "🚀 ابدأ التحميل",
        "warn_url": "⚠️ يرجى إدخال رابط صحيح أولاً!",
        "show_logs": "🛠️ إظهار/إخفاء السجل (Logs)",
        "log_start": "جاري بدء العملية...\n",
        "downloading": "جاري التحميل...",
        "speed": "السرعة",
        "eta": "الوقت المتبقي",
        "file": "الملف",
        "of": "من",
        "finish_process": "✅ انتهى التحميل، جاري المعالجة (قد يستغرق بعض الوقت)...",
        "zipping": "📦 جاري ضغط الملفات في مجلد ZIP...",
        "success_all": "🎉 تمت جميع العمليات بنجاح!",
        "btn_save_single": "💾 اضغط هنا لحفظ الملف",
        "btn_save_zip": "💾 اضغط هنا لحفظ ملف الـ ZIP",
        "error": "❌ حدث خطأ:",
        "lang_btn": "🌐 Switch to English"
    }
}

if lang == 'العربية':
    st.markdown("""
        <style>
        .stApp { direction: rtl; text-align: right; }
        p, div, h1, h2, h3, h4, h5, h6, label { text-align: right; direction: rtl; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { direction: ltr; text-align: left; }
        .stButton>button { direction: ltr; }
        </style>
    """, unsafe_allow_html=True)

col_empty, col_lang = st.columns([3, 1])
with col_lang:
    st.button(text[lang]["lang_btn"], on_click=toggle_language, use_container_width=True)

st.title(text[lang]["title"])
st.markdown(text[lang]["dev"])
st.write("---")

mode_choice = st.radio(text[lang]["mode_label"], [text[lang]["mode_single"], text[lang]["mode_playlist"], text[lang]["mode_batch"]], horizontal=True)

custom_zip_name = ""
if mode_choice == text[lang]["mode_batch"]:
    url_input = st.text_area(text[lang]["url_area_label"], height=100)
    custom_zip_name = st.text_input(text[lang]["zip_name_label"])
else:
    url_input = st.text_input(text[lang]["url_label"])

urls = [u.strip() for u in url_input.split('\n') if u.strip()]

col1, col2 = st.columns(2)
with col1:
    format_choice = st.radio(text[lang]["format_label"], [text[lang]["vid_format"], text[lang]["aud_format"]])

codec_choice = None
with col2:
    if format_choice == text[lang]["vid_format"]:
        quality_full = st.selectbox(text[lang]["vid_quality"], ["4320p (8K)", "2160p (4K)", "1440p (2K)", "1080p", "720p", "480p", "360p", "144p"])
        quality = quality_full.split('p')[0]
        codec_choice = st.radio(text[lang]["codec_label"], [text[lang]["codec_h264"], text[lang]["codec_av1"]])
    else:
        quality_full = st.selectbox(text[lang]["aud_quality"], ["320kbps", "256kbps", "192kbps", "128kbps", "64kbps"])
        quality = quality_full.replace('kbps', '')

st.write("---")

if st.button(text[lang]["btn_download"], use_container_width=True):
    if not urls:
        st.warning(text[lang]["warn_url"])
    else:
        st.write("---")
        file_tracking_placeholder = st.empty() 
        status_text_placeholder = st.empty()   
        progress_bar_placeholder = st.empty()  
        
        log_expander = st.expander(text[lang]["show_logs"], expanded=False)
        log_placeholder = log_expander.empty()
        
        if 'download_logs' not in st.session_state:
            st.session_state['download_logs'] = ""
        st.session_state['download_logs'] = text[lang]["log_start"]
        log_placeholder.code(st.session_state['download_logs'], language='bash')

        class StreamlitLogger:
            def debug(self, msg):
                if not msg.startswith('[download]') or 'Destination' in msg or 'has already been downloaded' in msg:
                    st.session_state['download_logs'] += f"{msg}\n"
                    log_placeholder.code(st.session_state['download_logs'], language='bash')
            def info(self, msg):
                st.session_state['download_logs'] += f"{msg}\n"
                log_placeholder.code(st.session_state['download_logs'], language='bash')
            def warning(self, msg):
                st.session_state['download_logs'] += f"{msg}\n"
                log_placeholder.code(st.session_state['download_logs'], language='bash')
            def error(self, msg):
                st.session_state['download_logs'] += f"{msg}\n"
                log_placeholder.code(st.session_state['download_logs'], language='bash')

        def my_hook(d):
            if mode_choice == text[lang]["mode_playlist"]:
                info = d.get('info_dict', {})
                current_idx = info.get('playlist_index')
                total_count = info.get('playlist_count')
                if current_idx and total_count:
                    file_tracking_placeholder.markdown(f"#### 📂 {text[lang]['file']} {current_idx} {text[lang]['of']} {total_count}")

            if d['status'] == 'downloading':
                try:
                    percent_str = d.get('_percent_str', '0%').replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip()
                    percent_float = float(percent_str.replace('%', '')) / 100.0
                    speed = d.get('_speed_str', 'N/A').replace('\x1b[0;32m', '').replace('\x1b[0m', '').strip()
                    eta = d.get('_eta_str', 'N/A').replace('\x1b[0;33m', '').replace('\x1b[0m', '').strip()
                    
                    progress_bar_placeholder.progress(percent_float)
                    status_text_placeholder.info(f"⏳ {text[lang]['downloading']} {percent_str} | {text[lang]['speed']}: {speed} | {text[lang]['eta']}: {eta}")
                except Exception:
                    pass
            elif d['status'] == 'finished':
                progress_bar_placeholder.progress(1.0)
                status_text_placeholder.warning(text[lang]["finish_process"])

        try:
            # التعديل الهجومي لتخطي الحماية عن طريق استخدام تطبيق أندرويد فقط وإلغاء الويب
            opts = {
                'quiet': True,
                'no_warnings': True,
                'logger': StreamlitLogger(),
                'progress_hooks': [my_hook],
                'extractor_retries': 4,
                # إرجاع سكربتات فك التشفير لتعمل مع محرك Node.js الموجود على السيرفر
                'remote_components': ['ejs:github'],
                'extractor_args': {
                    'youtube': ['player_client=android,web']
                }
            }

            if "youtube_cookies" in st.secrets:
                cookie_fd, cookie_path = tempfile.mkstemp(suffix=".txt")
                with os.fdopen(cookie_fd, 'w') as f:
                    f.write(st.secrets["youtube_cookies"])
                opts['cookiefile'] = cookie_path
            
            if format_choice == text[lang]["vid_format"]:
                if codec_choice == text[lang]["codec_av1"]:
                    opts['format'] = f'bestvideo[vcodec^=av01][height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'
                else:
                    opts['format'] = f'bestvideo[vcodec^=avc][height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'
            else:
                opts['format'] = 'bestaudio/best'
                opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }]

            if mode_choice == text[lang]["mode_single"]:
                file_tracking_placeholder.markdown(f"#### 📂 {text[lang]['file']} 1 {text[lang]['of']} 1")
                opts['noplaylist'] = True
                opts['outtmpl'] = '%(title)s.%(ext)s'
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(urls[0], download=True)
                    filename = ydl.prepare_filename(info)
                    if format_choice == text[lang]["aud_format"]:
                        filename = filename.rsplit('.', 1)[0] + '.mp3'
                
                status_text_placeholder.success(text[lang]["success_all"])
                with open(filename, "rb") as file:
                    st.download_button(label=text[lang]["btn_save_single"], data=file, file_name=filename, mime="video/mp4" if format_choice == text[lang]["vid_format"] else "audio/mpeg", use_container_width=True)
            
            else:
                temp_dir = tempfile.mkdtemp(prefix="ytdl_")
                zip_filename = "Downloads" 
                
                if mode_choice == text[lang]["mode_playlist"]:
                    opts['outtmpl'] = os.path.join(temp_dir, '%(playlist_index)s - %(title)s.%(ext)s')
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        for idx, u in enumerate(urls):
                            info = ydl.extract_info(u, download=True)
                            if idx == 0 and info:
                                zip_filename = info.get('title', 'Playlist')
                else:
                    opts['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
                    total_urls = len(urls)
                    if custom_zip_name.strip():
                        zip_filename = custom_zip_name.strip()
                        
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        for idx, u in enumerate(urls, 1):
                            file_tracking_placeholder.markdown(f"#### 📂 {text[lang]['file']} {idx} {text[lang]['of']} {total_urls}")
                            info = ydl.extract_info(u, download=True)
                            if idx == 1 and not custom_zip_name.strip() and info:
                                zip_filename = info.get('title', 'Batch_Download')
                
                zip_filename = re.sub(r'[\\/*?:"<>|]', "", zip_filename).strip()
                if not zip_filename:
                    zip_filename = "Downloads"
                zip_filename += ".zip"
                
                status_text_placeholder.info(text[lang]["zipping"])
                zip_path = shutil.make_archive(temp_dir, 'zip', temp_dir)
                
                file_tracking_placeholder.empty()
                status_text_placeholder.success(text[lang]["success_all"])
                
                with open(zip_path, "rb") as file:
                    st.download_button(label=text[lang]["btn_save_zip"], data=file, file_name=zip_filename, mime="application/zip", use_container_width=True)
                    
        except Exception as e:
            status_text_placeholder.error(f"{text[lang]['error']} {e}")
