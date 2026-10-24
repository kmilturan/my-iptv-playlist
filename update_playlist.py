import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Bütün mənbələr
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
    n = re.sub(r'\b(hd|fhd|hevc|sd|4k|hq)\b', '', n)
    n = re.sub(r'[\(\)\[\]\|\-\:]', ' ', n)
    return ' '.join(n.split())

def get_channel_group(channel_name):
    n = channel_name.lower()

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

def is_stream_working(url):
    """Linkin həqiqətən işlək olub-olmadığını real sorğu ilə yoxlayır"""
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*'
            }
        )
        # Qısa timeout (4 saniyə) - işləməyən link dərhal rədd edilir
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status in [200, 301, 302]:
                return True
    except Exception:
        pass
    return False

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    matched_group = get_channel_group(channel_name)
    
    if matched_group:
        # Həqiqətən yoxlayırıq ki, bu stream işləyirmi?
        if is_stream_working(stream_url):
            norm_name = normalize_channel_name(channel_name)
            return (norm_name, matched_group, channel_name, stream_url)
    return None

def main():
    all_entries = []

    # 1. Bütün mənbələrdən xam siyahını çəkirik
    for source_url in SOURCES:
        try:
            print(f"Mənbə oxunur: {source_url}")
            req = urllib.request.Request(
                source_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)
        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    print(f"Ümumi tapıldı: {len(all_entries)} kanal. Paralel yoxlama başlanır...")

    final_playlist = ["#EXTM3U\n"]
    added_normalized_names = set()

    # 2. 20 fərqli axın (thread) ilə eyni anda kanalları yoxlayırıq (çox sürətli işləyir)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_channel, entry) for entry in all_entries]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                norm_name, matched_group, channel_name, stream_url = result
                if norm_name not in added_normalized_names:
                    clean_extinf = f'#EXTINF:-1 group-title="{matched_group}",{channel_name}\n'
                    final_playlist.append(f"{clean_extinf}{stream_url}\n")
                    added_normalized_names.add(norm_name)
                    print(f"İşlək tapıldı [{matched_group}]: {channel_name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_normalized_names)} həqiqi işlək kanal qaldı.")

if __name__ == "__main__":
    main()
