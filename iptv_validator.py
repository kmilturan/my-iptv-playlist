import re
import subprocess
import os

def validate_and_update_playlist():
    target_file = "playlist.m3u"
    
    if not os.path.exists(target_file):
        print(f"{target_file} bulunamadı! Önce ana scripti çalıştırmalısınız.")
        return

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # #EXTINF satırları ile altındaki stream URL'lerini eşleştir
    pattern = r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)'
    matches = re.findall(pattern, content)

    print(f"Toplam {len(matches)} kanal kontrol ediliyor (FFmpeg ile test ediliyor)...")

    updated_playlist = ["#EXTM3U\n"]
    working_count = 0
    broken_count = 0

    for extinf, url in matches:
        # FFmpeg ile yayın akışının açılıp açılmadığını test et (3 saniye timeout)
        try:
            cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height', '-of', 'default=noprint_wrappers=1:nokey=1',
                '-timeout', '3000000', url
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                dims = result.stdout.strip().split('\n')
                resolution = ""
                if len(dims) >= 2 and dims[0].isdigit() and dims[1].isdigit():
                    resolution = f" ({dims[0]}x{dims[1]})"
                
                # İsimde çözünürlük yoksa ekleyebiliriz veya orijinali koruyabiliriz
                clean_extinf = extinf.rstrip()
                if resolution and "x" not in clean_extinf:
                    clean_extinf += resolution
                
                updated_playlist.append(f"{clean_extinf}\n{url}\n")
                working_count += 1
                print(f"✅ Çalışıyor: {url}")
            else:
                broken_count += 1
                print(f"❌ Kırık Link (Temizleniyor): {url}")
        except Exception:
            broken_count += 1
            print(f"❌ Zaman Aşımı/Hata (Temizleniyor): {url}")

    # Doğrudan aynı dosyaya (playlist.m3u) üzerine yazıyoruz
    with open(target_file, "w", encoding="utf-8") as f:
        f.writelines(updated_playlist)

    print(f"\nİşlem tamamlandı!")
    print(f"✔️ Kalan (Çalışan) Kanal: {working_count}")
    print(f"❌ Silinen (Kırık) Kanal: {broken_count}")
    print(f"📁 Güncellenen dosya: {target_file}")

if __name__ == "__main__":
    validate_and_update_playlist()
