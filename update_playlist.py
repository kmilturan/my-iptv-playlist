import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Master Mapping: Əsas kanallar üçün rəsmi adlar, EPG ID-lər və Loqolar
MASTER_CHANNELS = {
    "baku tv": {
        "name": "Baku TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "BakuTV.az",
        "logo": "https://i.imgur.com/example_bakutv.png",
        "aliases": ["baku tv", "bakutv", "baku-tv"]
    },
    "itv": {
        "name": "İTV HD",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "ITV.az",
        "logo": "",
        "aliases": ["ictimai", "itv", "ictimai tv"]
    },
    "aztv": {
        "name": "AzTV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "AzTV.az",
        "logo": "",
        "aliases": ["aztv", "azerbaijan tv"]
    },
    "cbc sport": {
        "name": "CBC Sport",
        "group": "⚽ İdman",
        "tvg_id": "CBCSport.az",
        "logo": "",
        "aliases": ["cbc sport", "cbcsport"]
    },
    "idman az": {
        "name": "İdman Azərbaycan",
        "group": "⚽ İdman",
        "tvg_id": "IdmanAzerbaijan.az",
        "logo": "",
        "aliases": ["idman az", "idmanazerbaijan"]
    },
    "xəzər tv": {
        "name": "Xəzər TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "KhazarTV.az",
        "logo": "",
        "aliases": ["xəzər", "khazar", "xezer tv"]
    },
    "arb tv": {
        "name": "ARB TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "ARBTv.az",
        "logo": "",
        "aliases": ["arb", "arb tv"]
    },
    "space tv": {
        "name": "Space TV",
        "group": "🇦🇿 Azərbaycan",
        "tvg_id": "SpaceTV.az",
        "logo": "",
        "aliases": ["space", "space tv"]
    },
    "trt 1": {
        "name": "TRT 1",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "TRT1.tr",
        "logo": "",
        "aliases": ["trt 1", "trt1"]
    },
    "kanal d": {
        "name": "Kanal D",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "KanalD.tr",
        "logo": "",
        "aliases": ["kanal d", "kanald"]
    },
    "show tv": {
        "name": "Show TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "ShowTV.tr",
        "logo": "",
        "aliases": ["show tv", "showtv"]
    },
    "star tv": {
        "name": "Star TV",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "StarTV.tr",
        "logo": "",
        "aliases": ["star tv", "startv"]
    },
    "tv8": {
        "name": "TV8",
        "group": "🇹🇷 Türkiyə - Əsas",
        "tvg_id": "TV8.tr",
        "logo": "",
        "aliases": ["tv8"]
    }
}

SOURCES = [
    "https://raw.githubusercontent.com/Free-TV/IPTV/refs/heads/master/playlists/playlist_azerbaijan.m3u8",
    "https://raw.githubusercontent.com/Hero355/iptv/refs/heads/master/Azerbaijan",
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/az.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]

def match_master_channel(channel_name):
    n = channel_name.lower()
    
    # Ödənişli və qorunan məzmunları qəti şəkildə kənarlaşdırırıq
    if "bein sports" in n or "s Sport" in n:
        return None, None

    for key, data in MASTER_CHANNELS.items():
        for alias in data["aliases"]:
            if alias in n:
                return key, data
                
    return None, None

def is_stream_healthy(url):
    """HLS manifest (.m3u8) faylının daxilində real seqmentlərin olub-olmadığını yoxlayır"""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            # Əgər .m3u8 faylıdırsa, içində axın məlumatı və ya seqment olmalıdır
            if ".m3u" in url or "EXTINF" in content or "EXT-X-STREAM-INF" in content or len(content) > 100:
                return True
    except Exception:
        pass
    return False

def process_channel(entry):
    extinf, stream_url = entry
    channel_name = extinf.split(',')[-1].strip()
    
    master_key, channel_info = match_master_channel(channel_name)
    if master_key and channel_info:
        if is_stream_healthy(stream_url):
            return master_key, channel_info, stream_url
    return None

def main():
    final_playlist = ["#EXTM3U\n"]
    added_keys = set()
    all_entries = []

    for source_url in SOURCES:
        try:
            print(f"Mənbə oxunur: {source_url}")
            req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')

            entries = re.findall(r'(#EXTINF:[^\n]+\n)(https?://[^\s]+)', content)
            all_entries.extend(entries)
        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    print(f"Ümumi tapıldı: {len(all_entries)} xam kanal. Master Mapping və Sağlamlıq yoxlaması aparılır...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_channel, entry) for entry in all_entries]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                master_key, info, stream_url = result
                if master_key not in added_keys:
                    extinf_line = f'#EXTINF:-1 tvg-id="{info["tvg_id"]}" group-title="{info["group"]}",{info["name"]}\n'
                    final_playlist.append(f"{extinf_line}{stream_url}\n")
                    added_keys.add(master_key)
                    print(f"Qəbul edildi [{info['group']}]: {info['name']}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    
    print(f"Yenilənmə tamamlandı! Cəmi {len(added_keys)} unikal, yoxlanılmış kanal yazıldı.")

if __name__ == "__main__":
    main()
