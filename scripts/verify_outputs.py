#!/usr/bin/env python3
"""Vérifie que chaque produit inventorié possède trois sorties image lisibles.
Usage: python3 verify_outputs.py ROOT
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from inventory import build_manifest, norm

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}

def image_ok(path: Path) -> tuple[bool, str]:
    if not path.is_file() or path.stat().st_size < 1024:
        return False, "absent ou inférieur à 1 Ko"
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
        return True, "ok"
    except ImportError:
        return True, "ok (Pillow absent: intégrité décodée non contrôlée)"
    except Exception as exc:
        return False, f"image illisible: {exc}"

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: verify_outputs.py ROOT", file=sys.stderr)
        return 2
    manifest = build_manifest(Path(sys.argv[1]))
    if manifest["errors"]:
        print(json.dumps({"valid": False, "inventory_errors": manifest["errors"]}, ensure_ascii=False, indent=2))
        return 2
    results, valid = [], 0
    seen = set()
    for collection in manifest["collections"]:
        for job in collection["jobs"]:
            key = (collection["name"], job["product"], job["destination_dir"])
            if key in seen:
                continue
            seen.add(key)
            outdir = Path(job["destination_dir"])
            files = [p for p in outdir.iterdir() if p.is_file() and p.suffix.casefold() in IMAGE_EXTS] if outdir.is_dir() else []
            variants = {}
            for n in (1, 2, 3):
                matches = [p for p in files if f"-{n:02d}" in p.stem or p.stem.endswith(f"-{n}")]
                if len(matches) == 1:
                    ok, detail = image_ok(matches[0])
                    variants[str(n)] = {"path": str(matches[0]), "ok": ok, "detail": detail}
                    valid += int(ok)
                else:
                    variants[str(n)] = {"ok": False, "detail": f"{len(matches)} fichier(s) correspondant(s)"}
            results.append({"collection": collection["name"], "product": job["product"], "variants": variants})
    expected = len(results) * 3
    payload = {"collections": len(manifest["collections"]), "products": len(results), "expected": expected,
               "valid_images": valid, "complete": valid == expected, "results": results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["complete"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
