# ChatGPT Product Image Batch

Skill portable pour générer des séries d’images produit avec l’interface web ChatGPT.

Pour chaque collection et chaque produit, il associe :

1. l’image réelle du produit ;
2. l’image de référence 1 + le prompt 1 ;
3. l’image de référence 2 + le prompt 2 ;
4. l’image de référence 3 + le prompt 3 ;
5. trois téléchargements rangés dans `image générée/<Produit>/`.

## Structure attendue

```text
image à refaire (chatgpt)/
└── Suspensions/
    ├── produit/
    │   ├── Anka.webp
    │   └── Oma.webp
    ├── image de référence/
    │   ├── 01-reference.png
    │   ├── 02-reference.png
    │   └── 03-reference.png
    ├── prompt/
    │   ├── 01-prompt.txt
    │   ├── 02-prompt.txt
    │   └── 03-prompt.txt
    └── image générée/
```

Les accents, la casse et certains pluriels sont tolérés.

## Installation Hermes Agent

```bash
git clone https://github.com/axstzz/chatgpt-product-image-batch.git
mkdir -p ~/.hermes/skills/ecommerce
cp -R chatgpt-product-image-batch ~/.hermes/skills/ecommerce/
```

Relancer la session Hermes.

## Installation Claude Code

```bash
git clone https://github.com/axstzz/chatgpt-product-image-batch.git
mkdir -p ~/.claude/skills
cp -R chatgpt-product-image-batch ~/.claude/skills/
```

Relancer Claude Code.

## Utilisation

```text
Utilise le skill chatgpt-product-image-batch.
Mon dossier racine est : /chemin/absolu/vers/image à refaire (chatgpt)
```

Si le chemin n’est pas fourni, le skill demande uniquement cette information.

## Sécurité

- Aucun mot de passe, cookie ou token dans le dépôt.
- L’utilisateur doit déjà être connecté à ChatGPT dans son navigateur.
- Aucun fichier existant n’est écrasé.
- Une conversation ChatGPT neuve est utilisée pour chaque variante.
- Le téléchargement original est utilisé, jamais une capture d’écran.

## Vérification locale

```bash
python3 scripts/inventory.py "/chemin/vers/image à refaire (chatgpt)"
python3 scripts/verify_outputs.py "/chemin/vers/image à refaire (chatgpt)"
```

Pillow est facultatif. S’il est installé, le vérificateur décode réellement chaque image.
