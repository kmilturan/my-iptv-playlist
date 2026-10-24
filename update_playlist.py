import urllib.request
import re

# Bütün yoxlanılmış və ən zəngin mənbələr
SOURCES = [
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
    "https://raw.githubusercontent.com/Hero355/iptv/refs/heads/master/Azerbaijan",
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u",
    "https://iptv-org.github.io/iptv/countries/az.m3u",
    "https://iptv-org.github.io/iptv/countries/tr.m3u"
]

def normalize_channel_name(name):
    """Kanal adını təmizləyir ki, dublikatlar yaranmasın"""
    n = name.lower()
    # HD, FHD, HEVC, 4K və mötərizə içindəki simvolları təmizləyirik
    n = re.sub(r'\b(hd|fhd|hevc|sd|4k|hq)\b', '', n)
    n = re.sub(r'[\(\)\[\]\|\-\:]', ' ', n)
    return ' '.join(n.split())

def get_channel_group(channel_name):
    n = channel_name.lower()

    # beIN Sports kimi qorunan kanalları çıxarırıq
    if "bein sports" in n:
        return None

    # 1. Azərbaycan kanalları
    az_keywords = [
        "aztv", "ictimai", "itv", "azad azərbaycan", "azad azerbaijan", 
        "xəzər", "khazar", "arb", "space", "real tv", "baku tv", "baku", "lider", 
        "mədəniyyət", "medeniyyet", "dunya tv", "kanal s", "cbc sport", "idman", "atv azerbaijan", "az:"
    ]
    if any(kw in n for kw in az_keywords):
        return "🇦🇿 Azərbaycan"

    # 2. Türkiyə - Əsas kanallar
    tr_main = ["trt 1", "kanal d", "show tv", "star tv", "tv8", "tv8.5", "now", "fox", "kanal 7", "beyaz tv", "teve2", "360", "24 tv", "tgrt", "a2", "atv"]
    if any(kw in n for kw in tr_main) and not ("azerbaijan" in n or "azad" in n or "az:" in n):
        return "🇹🇷 Türkiyə - Əsas"

    # 3. İdman kanalları
    sport_keywords = ["sport", "trtspor", "aspor", "fb tv", "gs tv", "bjk", "tivibu"]
    if any(kw in n for kw in sport_keywords):
        return "⚽ İdman"

    # 4. Xəbər kanalları
    news_keywords = ["haber", "news", "cnn", "ntv", "bloomberg", "ekotürk", "sozcu", "sözcü", "tv100", "halk tv", "tele1"]
    if any(kw in n for kw in news_keywords):
        return "📰 Xəbər"

    # 5. Uşaq və Sənədli
    kids_doc_keywords = ["çocuk", "cocuk", "minika", "cartoon", "belgesel", "discovery", "national geographic", "history", "animal", "müzik", "muzik", "dream", "kral"]
    if any(kw in n for kw in kids_doc_keywords):
        return "🧸 Uşaq & Sənədli"

    return None

def main():
    final_playlist = ["#EXTM3U\n"]
    added_normalized_names = set()

    for source_url in SOURCES:
        try:
            print(f"Mənbə oxunur: {source_url}")
            req = urllib.request.Request(
                source_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)

            for extinf, stream_url in entries:
                channel_name = extinf.split(',')[-1].strip()
                matched_group = get_channel_group(channel_name)

                if matched_group:
                    norm_name = normalize_channel_name(channel_name)
                    
                    if norm_name and norm_name not in added_normalized_names:
                        clean_extinf = f'#EXTINF:-1 group-title="{matched_group}",{channel_name}\n'
                        final_playlist.append(f"{clean_extinf}{stream_url}\n")
                        added_normalized_names.add(norm_name)
                        print(f"Əlavə edildi [{matched_group}]: {channel_name}")

        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_normalized_names)} unikal işlək kanal toplandı.")

if __name__ == "__main__":
    main()
