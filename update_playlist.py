import urllib.request
import re

# Azərbaycan kanalları üçün xüsusi stabil mənbələr və ümumi siyahılar
SOURCES = [
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]

def get_channel_group(channel_name):
    n = channel_name.lower()

    # beIN Sports kimi saxta/ölü idman kanallarını qəti şəkildə çıxarırıq
    if "bein sports" in n:
        return None

    # 1. Azərbaycan kanalları (prioritet)
    az_keywords = [
        "aztv", "ictimai", "itv", "azad azərbaycan", "azad azerbaijan", 
        "xəzər", "khazar", "arb", "space", "real tv", "baku tv", "lider", 
        "mədəniyyət", "medeniyyet", "dunya tv", "kanal s", "cbc sport", "idman", "atv azerbaijan", "az:"
    ]
    if any(kw in n for kw in az_keywords):
        return "🇦🇿 Azərbaycan"

    # 2. Türkiyə - Əsas kanallar
    tr_main = ["trt 1", "kanal d", "show tv", "star tv", "tv8", "tv8.5", "now", "fox", "kanal 7", "beyaz tv", "teve2", "360", "24 tv", "tgrt", "a2", "atv"]
    if any(kw in n for kw in tr_main) and not ("azerbaijan" in n or "azad" in n or "az:" in n):
        return "🇹🇷 Türkiyə - Əsas"

    # 3. İdman kanalları
    sport_keywords = ["trt spor", "a spor", "s sport", "aspor", "fb tv", "gs tv", "cbc sport"]
    if any(kw in n for kw in sport_keywords):
        return "⚽ İdman"

    # 4. Xəbər kanalları
    news_keywords = ["trt haber", "haberturk", "haber türk", "cnn turk", "cnn türk", "ntv", "a haber", "ekotürk", "bloomberg", "ülke tv", "sozcu", "sözcü", "tv100", "halk tv", "tele1"]
    if any(kw in n for kw in news_keywords):
        return "📰 Xəbər"

    # 5. Uşaq və Sənədli
    kids_doc_keywords = ["trt çocuk", "cocuk", "minika", "cartoon network", "trt belgesel", "trt müzik", "muzik", "trt avaz", "tmb", "kral pop", "power tv", "dream"]
    if any(kw in n for kw in kids_doc_keywords):
        return "🧸 Uşaq & Sənədli"

    return None

def is_stream_working(url):
    """Yayımın işlək olub-olmadığını daha etibarlı yoxlayır (vaxt limitini artırırıq)"""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        # Bəzi serverlər gec cavab verdiyi üçün vaxtı 6 saniyəyə qaldırırıq
        with urllib.request.urlopen(req, timeout=6) as response:
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
            with urllib.request.urlopen(req, timeout=15) as response:
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
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_channels)} kanal əlavə edildi.")

if __name__ == "__main__":
    main()
