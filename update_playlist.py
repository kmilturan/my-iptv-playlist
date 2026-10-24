import urllib.request
import re

# Ən aktiv, güncəl və geniş IPTV mənbələri (Azərbaycan, Türkiyə və xüsusi kateqoriyalar)
SOURCES = [
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://iptv-org.github.io/iptv/languages/aze.m3u",
    "https://iptv-org.github.io/iptv/languages/tur.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://iptv-org.github.io/iptv/categories/news.m3u",
    "https://iptv-org.github.io/iptv/categories/documentary.m3u"
]

def get_channel_group(channel_name):
    n = channel_name.lower()

    # 1. Türkiyə - Əsas kanallar
    tr_main = ["trt 1", "kanal d", "show tv", "star tv", "tv8", "tv8.5", "now", "fox", "kanal 7", "beyaz tv", "teve2", "360", "24 tv", "tgrt", "a2", "atv"]
    if any(kw in n for kw in tr_main) and not ("azerbaijan" in n or "azad" in n or "az:" in n):
        return "🇹🇷 Türkiyə - Əsas"

    # 2. Azərbaycan kanalları
    az_keywords = [
        "aztv", "ictimai", "itv", "azad azərbaycan", "azad azerbaijan", 
        "xəzər", "khazar", "arb", "space", "real tv", "baku tv", "lider", 
        "mədəniyyət", "medeniyyet", "dunya tv", "kanal s", "cbc sport", "idman tv", "atv azerbaijan", "az:"
    ]
    if any(kw in n for kw in az_keywords):
        return "🇦🇿 Azərbaycan"

    # 3. İdman kanalları (beIN, S Sport, TRT Spor, CBC Sport və s.)
    sport_keywords = ["sport", "bein", "s sport", "aspor", "fb tv", "gs tv", "trtspor", "tivibu spor", "smart spor"]
    if any(kw in n for kw in sport_keywords):
        return "⚽ İdman"

    # 4. Xəbər kanalları
    news_keywords = ["haber", "news", "cnn", "ntv", "bloomberg", "ekotürk", "sozcu", "sözcü", "tv100", "halk tv", "tele1", "trthaber"]
    if any(kw in n for kw in news_keywords):
        return "📰 Xəbər"

    # 5. Uşaq və Sənədli (Discovery, National Geographic, Belgesel, Çocuk)
    kids_doc_keywords = ["çocuk", "cocuk", "minika", "cartoon", "belgesel", "discovery", "national geographic", "history", "animal planet", "müzik", "muzik", "dream", "kral"]
    if any(kw in n for kw in kids_doc_keywords):
        return "🧸 Uşaq & Sənədli"

    return None

def is_stream_working(url):
    """Yayımın işlək olub-olmadığını yoxlayır"""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                return True
    except Exception:
        pass
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

                matched_group = get_channel_group(channel_name)

                if matched_group and channel_name not in added_channels:
                    print(f"Yoxlanılır [{matched_group}]: {channel_name}...")
                    if is_stream_working(stream_url):
                        print(f" -> [İŞLƏK] {channel_name}")
                        clean_extinf = f'#EXTINF:-1 group-title="{matched_group}",{channel_name}\n'
                        final_playlist.append(f"{clean_extinf}{stream_url}\n")
                        added_channels.add(channel_name)
                    else:
                        print(f" -> [İŞLƏMİR - SİLİNDİ] {channel_name}")

        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_channels)} aktiv və işlək kanal toplandı.")

if __name__ == "__main__":
    main()
