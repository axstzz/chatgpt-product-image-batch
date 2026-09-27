# Installation rapide

Copier le dossier `chatgpt-product-image-batch` dans le répertoire de skills de l’agent.

## Hermes Agent

```bash
mkdir -p ~/.hermes/skills/ecommerce
cp -R chatgpt-product-image-batch ~/.hermes/skills/ecommerce/
```

Relancer ensuite la session Hermes afin que la liste des skills soit rechargée.

## Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R chatgpt-product-image-batch ~/.claude/skills/
```

Relancer Claude Code.

## Utilisation

Dire à l’agent :

```text
Utilise le skill chatgpt-product-image-batch.
Le dossier racine est : /chemin/absolu/vers/image à refaire (chatgpt)
```

Si aucun chemin n’est fourni, le skill le demande avant l’inventaire.

## Dépendances

- Python 3
- Un navigateur contrôlable par l’agent
- Une session ChatGPT déjà connectée
- Pillow facultatif, uniquement pour approfondir le contrôle d’intégrité des images

Aucune clé API OpenAI n’est nécessaire. Aucun identifiant ChatGPT ne doit être mis dans le dépôt.
