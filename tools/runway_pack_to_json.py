# tools/runway_pack_to_json.py
import os, re, json
from pathlib import Path

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def natkey(s: str):
    # Doğal sıralama: 1,2,10
    import re as _re
    return [_int(x) if x.isdigit() else x.lower() for x in _re.split(r'(\d+)', s)]

def _int(x): 
    try: return int(x)
    except: return x

def build_index(root: Path, base_url: str):
    out = {"collections": []}
    runway_root = root / "runway"
    if not runway_root.exists():
        return out

    for brand_dir in sorted([p for p in runway_root.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        brand = brand_dir.name
        for season_dir in sorted([p for p in brand_dir.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
            season = season_dir.name

            images = [p for p in season_dir.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXT]
            images.sort(key=lambda p: natkey(p.name))
            if not images:
                continue

            editorial = ""
            ed = season_dir / "editorial.txt"
            if ed.exists():
                editorial = ed.read_text(encoding="utf-8").strip()

            looks = []
            for i, p in enumerate(images, start=1):
                rel = p.relative_to(root).as_posix()  # runway/Dior/SS25/look_xxx.jpg
                looks.append({
                    "id": f"{brand.lower().replace(' ','-')}-{season.lower()}-{i}",
                    "imageUrl": f"{base_url}/{rel}",
                    "index": i,
                    "tags": []
                })

            out["collections"].append({
                "id": f"{brand.lower().replace(' ','-')}-{season.lower()}",
                "brand": brand,
                "season": season,
                "title": f"{brand} {season}",
                "editorial": editorial,
                "looks": looks
            })
    return out

def main():
    # GitHub Actions içinde base_url'i env'den alacağız (GH_PAGES_BASE).
    base = os.getenv("GH_PAGES_BASE", "").rstrip("/")
    if not base:
        raise SystemExit("GH_PAGES_BASE boş. Workflow içinde export edilmesi gerekir.")

    root = Path(".").resolve()
    data = build_index(root, base)
    (root / "index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✓ index.json yazıldı (koleksiyon: {len(data['collections'])})")

if __name__ == "__main__":
    main()
