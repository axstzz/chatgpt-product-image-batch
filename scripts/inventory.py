#!/usr/bin/env python3
"""Inventorie un lot ChatGPT produit + 3 références + 3 prompts.
Usage: python3 inventory.py ROOT [--write PATH]
Zéro dépendance externe, lecture seule sauf si --write est fourni.
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
PROMPT_EXTS = {".txt", ".md"}
ALIASES = {
    "products": {"produit", "produits", "product", "products"},
    "references": {"image de reference", "images de reference", "reference", "references"},
    "prompts": {"prompt", "prompts"},
    "outputs": {"image generee", "images generees", "image generees", "images generee", "image generated", "generated images"},
}

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[_\-]+", " ", value.casefold())
    return re.sub(r"\s+", " ", value).strip()

def natural_number(path: Path) -> int | None:
    # Accepte 1/2/3 et les préfixes usuels 01/02/03, sans confondre 10/21/32.
    nums = re.findall(r"(?<!\d)0?([1-3])(?!\d)", path.stem)
    return int(nums[-1]) if len(nums) == 1 else None

def role_dirs(collection: Path) -> tuple[dict[str, Path], list[str]]:
    found: dict[str, list[Path]] = {k: [] for k in ALIASES}
    for child in collection.iterdir():
        if child.is_dir():
            n = norm(child.name)
            for role, aliases in ALIASES.items():
                if n in aliases:
                    found[role].append(child)
    errors, roles = [], {}
    for role, paths in found.items():
        if len(paths) != 1:
            errors.append(f"{collection}: dossier {role}: {len(paths)} candidat(s) ({', '.join(map(str, paths)) or 'aucun'})")
        else:
            roles[role] = paths[0]
    return roles, errors

def ordered_three(folder: Path, exts: set[str], label: str) -> tuple[list[Path], list[str]]:
    files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.casefold() in exts)
    by_num: dict[int, list[Path]] = {1: [], 2: [], 3: []}
    errors = []
    for p in files:
        n = natural_number(p)
        if n is None:
            errors.append(f"{p}: numéro 1, 2 ou 3 absent ou ambigu")
        else:
            by_num[n].append(p)
    for n, paths in by_num.items():
        if len(paths) != 1:
            errors.append(f"{folder}: {label} {n}: {len(paths)} fichier(s)")
    return ([by_num[n][0] for n in (1, 2, 3)] if not errors else []), errors

def products(folder: Path) -> tuple[list[dict], list[str]]:
    items, errors = [], []
    for p in sorted(folder.iterdir(), key=lambda x: norm(x.name)):
        if p.is_file() and p.suffix.casefold() in IMAGE_EXTS:
            items.append({"name": p.stem, "source": str(p.resolve())})
        elif p.is_dir():
            imgs = sorted(x for x in p.rglob("*") if x.is_file() and x.suffix.casefold() in IMAGE_EXTS)
            if len(imgs) == 1:
                items.append({"name": p.name, "source": str(imgs[0].resolve())})
            elif len(imgs) == 0:
                errors.append(f"{p}: aucune image produit")
            else:
                errors.append(f"{p}: {len(imgs)} images produit, impossible de choisir automatiquement")
    names = [norm(x["name"]) for x in items]
    if len(names) != len(set(names)):
        errors.append(f"{folder}: noms de produits en doublon après normalisation")
    if not items:
        errors.append(f"{folder}: aucun produit")
    return items, errors

def build_manifest(root: Path) -> dict:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Dossier racine introuvable: {root}")
    manifest = {"root": str(root), "collections": [], "errors": []}
    for collection in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda x: norm(x.name)):
        roles, errors = role_dirs(collection)
        # Ignore les dossiers techniques qui ne ressemblent pas à une collection.
        if len(roles) == 0 and len(errors) == len(ALIASES):
            continue
        entry = {"name": collection.name, "path": str(collection.resolve()), "jobs": []}
        if errors:
            manifest["errors"].extend(errors)
            manifest["collections"].append(entry)
            continue
        prods, pe = products(roles["products"])
        refs, re_ = ordered_three(roles["references"], IMAGE_EXTS, "référence")
        prompts, pre = ordered_three(roles["prompts"], PROMPT_EXTS, "prompt")
        manifest["errors"].extend(pe + re_ + pre)
        if not (pe or re_ or pre):
            for prod in prods:
                destination = roles["outputs"] / prod["name"]
                for i in range(3):
                    entry["jobs"].append({
                        "product": prod["name"], "product_image": prod["source"],
                        "variant": i + 1, "reference": str(refs[i].resolve()),
                        "prompt": str(prompts[i].resolve()),
                        "destination_dir": str(destination.resolve()),
                    })
        manifest["collections"].append(entry)
    if not manifest["collections"]:
        manifest["errors"].append(f"{root}: aucune collection reconnue")
    manifest["summary"] = {
        "collections": len(manifest["collections"]),
        "jobs": sum(len(c["jobs"]) for c in manifest["collections"]),
        "products": sum(len({j["product"] for j in c["jobs"]}) for c in manifest["collections"]),
        "valid": not manifest["errors"],
    }
    return manifest

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--write", type=Path)
    args = ap.parse_args()
    try:
        manifest = build_manifest(args.root)
    except Exception as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    text = json.dumps(manifest, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text + "\n", encoding="utf-8")
    return 0 if manifest["summary"]["valid"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
