from pathlib import Path
from .config import ROOT, CONFIG

def upload_video(video_path: Path, description: str) -> bool:
    try:
        from tiktok_uploader.upload import upload_video as tiktok_upload
    except ImportError:
        print("    [Error] tiktok-uploader tidak terinstal. Jalankan: pip install tiktok-uploader")
        return False

    session_file = CONFIG.get("upload_tiktok", {}).get("session_file", "tiktok_cookies.txt")
    session_path = ROOT / session_file
    
    if not session_path.exists():
        print(f"    [Error] File cookies TikTok tidak ditemukan: {session_path}")
        print("    Silakan export cookies TikTok Anda (Netscape format) menggunakan ekstensi browser")
        print("    seperti 'Get cookies.txt LOCALLY' dan simpan di root folder sebagai 'tiktok_cookies.txt'.")
        return False
        
    try:
        # tiktok-uploader expects the description to be the caption
        failed = tiktok_upload(
            str(video_path),
            description=description,
            cookies=str(session_path),
            headless=True
        )
        if failed:
            print("    [Error] Gagal upload ke TikTok. Periksa format cookies atau coba update library.")
            return False
            
        print("    [Sukses] Video berhasil di-upload ke TikTok.")
        return True
    except Exception as e:
        print(f"    [Error] Exception saat upload TikTok: {e}")
        return False
