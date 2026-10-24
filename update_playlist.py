import urllib.request
import re

# Bir neçə stabil və işlək mənbəni bura əlavə edirik
SOURCES = [
    "https://qazim.github.io/IPTV/all_channels.m3u",
    "https://raw.githubusercontent.com/funcen/IPTV/main/index.m3u",
]

# Kanalları kateqoriyalara (qruplara) bölürük
CHANNEL_GROUPS = {
    "🇦🇿 Azərbaycan": [
        "AzTV", "AZTV", "İctimai", "Ictimai", "İTV", "ITV", 
        "ATV", "ATV AZ", "ATV Azerbaijan", "Azad Azerbaijan", "Xazar", "Khazar", 
        "ARB", "ARB 24", "Space", "Real TV", "Baku TV", "Lider", 
        "Mədəniyyət", "Medeniyyet", "Dunya TV", "Kanal S", 
        "CBC Sport", "CBC SPORT", "Idman", "İdman Azerbaijan", "Idman TV"
    ],
    "🇹🇷 Türkiyə - Əsas": [
        "TRT 1", "TRT1", "Kanal D", "KANAL D", "Show TV", "SHOW TV", 
        "Star TV", "STAR TV", "TV8", "TV8.5", "TV8 5", "NOW", "FOX", 
        "Kanal 7", "KANAL 7", "Beyaz TV", "Flash Haber", "Teve2", "teve2",
        "360", "24 TV", "TGRT Haber", "A2", "a2", 
        "ATV TR", "ATV HD", "ATV Turkiye", "ATV Türkiye", "atv"
    ],
    "⚽ İdman": [
        "TRT Spor", "TRT Spor Yildiz", "A Spor", "A SPOR", "S Sport", 
        "beIN Sports", "ASpor", "FB TV", "GS TV"
    ],
    "📰 Xəbər": [
        "TRT Haber", "Haberturk", "Haber Türk", "CNN Turk", "CNN Türk", 
        "NTV", "A Haber", "A HABER", "Ekotürk", "Bloomberg HT", 
        "Ülke TV", "SZC", "Sozcu TV", "Sözcü TV", "TV100", "Halk TV", "Tele1"
    ],
    "🧸 Uşaq & Sənədli": [
        "TRT Çocuk", "TRT Cocuk", "Minika Çocuk", "Minika Cocuk", "Minika GO", "Cartoon Network",
        "TRT Belgesel", "TRT Müzik", "TRT Muzik", "TRT Avaz", "TRT Kurdi",
        "TMB", "Kral POP", "Power TV", "Dream Turk", "Dream Türk", "Number1"
    ]
}

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

                matched_group = None
                for group_name, keywords in CHANNEL_GROUPS.items():
                    if any(kw.lower() in channel_name.lower() for kw in keywords):
                        matched_group = group_name
                        break

                if matched_group and channel_name not in added_channels:
                    clean_extinf = f'#EXTINF:-1 group-title="{matched_group}",{channel_name}\n'
                    final_playlist.append(f"{clean_extinf}{stream_url}\n")
                    added_channels.add(channel_name)
                    print(f"Əlavə edildi [{matched_group}]: {channel_name}")

        except Exception as e:
            print(f"Xəta baş verdi ({source_url}): {e}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.writelines(final_playlist)
    print("Yenilənmə tamamlandı! Çoxmənbəli və kateqoriyalı playlist yaradıldı.")

if __name__ == "__main__":
    main()
