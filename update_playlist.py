import urllib.request
import re

# 1. Mənbə M3U linkləri (Bura istədiyiniz qədər işlək mənbə əlavə edə bilərsiniz)
SOURCES = [
    "https://qazim.github.io/IPTV/all_channels.m3u"
]

# 2. Genişləndirilmiş Kanal Siyahısı (Azərbaycan və Türkiyə)
TARGET_CHANNELS = [
    # Azərbaycan
    "AzTV", "AZTV", "İctimai", "Ictimai", "İTV", "ITV", 
    "ATV", "ATV AZ", "ATV Azerbaijan", "Azad Azerbaijan", "Xazar", "Khazar", 
    "ARB", "ARB 24", "Space", "Real TV", "Baku TV", "Lider", 
    "Mədəniyyət", "Medeniyyet", "Dunya TV", "Kanal S", 
    "CBC Sport", "CBC SPORT", "Idman", "İdman Azerbaijan", "Idman TV",
    
    # Türkiyə (ATV və digərləri)
    "ATV TR", "ATV HD", "ATV Turkiye", "ATV Türkiye", "atv",
    "TRT 1", "TRT1", "Kanal D", "KANAL D", "Show TV", "SHOW TV", 
    "Star TV", "STAR TV", "TV8", "TV8.5", "TV8 5", "NOW", "FOX", 
    "Kanal 7", "KANAL 7", "Beyaz TV", "Flash Haber", "Teve2", "teve2",
    "360", "24 TV", "TGRT Haber", "A2", "a2",
    "TRT Spor", "TRT Spor Yildiz", "A Spor", "A SPOR", "S Sport", 
    "beIN Sports", "ASpor", "FB TV", "GS TV",
    "TRT Haber", "Haberturk", "Haber Türk", "CNN Turk", "CNN Türk", 
    "NTV", "A Haber", "A HABER", "Ekotürk", "Bloomberg HT", 
    "Ülke TV", "SZC", "Sozcu TV", "Sözcü TV", "TV100", "Halk TV", "Tele1",
    "TRT Çocuk", "TRT Cocuk", "Minika Çocuk", "Minika Cocuk", "Minika GO", "Cartoon Network",
    "TRT Belgesel", "TRT Müzik", "TRT Muzik", "TRT Avaz", "TRT Kurdi",
    "TMB", "Kral POP", "Power TV", "Dream Turk", "Dream Türk", "Number1"
]

def check_stream_working(url):
    """Linkin işlək olub-olmadığını yoxlayır (Timeout: 3 saniyə)"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status == 200
    except Exception:
        return False

def main():
    final_playlist = ["#EXTM3U\n"]
    added_channels = set()

    for source_url in SOURCES:
        try:
            print(f"Mənbə oxunur: {source_url}")
            req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)

            for extinf, stream_url in entries:
                channel_name = extinf.split(',')[-1].strip()

                is_selected = any(target.lower() in channel_name.lower() for target in TARGET_CHANNELS)

                if is_selected and channel_name not in added_channels:
                    print(f"Yoxlanılır: {channel_name}")
                    if check_stream_working(stream_url):
                        print(f" -> [İŞLƏK] {channel_name}")
                        final_playlist.append(f"{extinf}{stream_url}\n")
                        added_channels.add(channel_name)
                    else:
                        print(f" -> [İŞLƏMİR] {channel_name}")

        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    print("Yenilənmə tamamlandı! 'playlist.m3u' faylı yaradıldı.")

if __name__ == "__main__":
    main()
