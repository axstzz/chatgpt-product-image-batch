---
name: chatgpt-product-image-batch
description: Use when regenerating batches of e-commerce product images through the authenticated ChatGPT web interface from a folder containing collections, product images, three scene references, three prompts, and an output folder. Ask only for the root folder, process every product deterministically, download each result into the matching product output folder, and verify completeness and file integrity.
version: 1.0.0
author: Kebabier Labs
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [chatgpt, images, ecommerce, batch, browser-automation]
    related_skills: []
---

# Batch d’images produit via ChatGPT

## Vue d’ensemble

Ce skill transforme une arborescence préparée en lot d’images produit via l’interface web ChatGPT.

La seule variable demandée à l’utilisateur est le chemin absolu du dossier racine, par exemple :

```text
/Users/axel/Desktop/boutique/atelier aeris/image à refaire (chatgpt)
```

Il n’invente ni prompt, ni référence, ni produit. Il applique chaque couple `référence N + prompt N` au même produit, puis range le résultat dans `image générée/<Produit>/`.

## Quand l’utiliser

Utiliser ce skill lorsque le dossier racine contient une ou plusieurs collections, chacune avec :

```text
<racine>/
└── <collection>/
    ├── produit/
    ├── image de référence/
    ├── prompt/
    └── image générée/
```

Variantes de noms acceptées : pluriels, accents absents, casse différente, `image générées`.

Ne pas utiliser ce skill si :

- les prompts doivent encore être écrits ou validés ;
- les références ne sont pas finalisées ;
- l’utilisateur demande une génération via API plutôt que via ChatGPT web ;
- le dossier ne permet pas d’identifier sans ambiguïté trois références et trois prompts ordonnés.

## Prérequis

- **OpenCLI avec son extension navigateur active**, ou un outil équivalent de contrôle du navigateur local.
- Un onglet `https://chatgpt.com/` déjà ouvert sur le Mac et connecté au compte de l’utilisateur.
- Les téléchargements autorisés dans le navigateur.
- Le dossier racine accessible localement.
- Python 3 pour l’inventaire et les contrôles.

Ce workflow doit utiliser l’onglet ChatGPT réel du Mac. Ne pas remplacer cette voie par l’API Images, le backend Codex OAuth ou une génération serveur : la qualité et le comportement ne sont pas identiques.

Avant le premier produit, vérifier qu’OpenCLI voit bien l’onglet ChatGPT et peut ouvrir le sélecteur de fichiers. Si l’onglet n’est pas pilotable, s’arrêter au lieu de lancer une autre méthode.

Si ChatGPT demande une connexion, un CAPTCHA, une confirmation de sécurité ou un abonnement, s’arrêter et demander à l’utilisateur d’effectuer cette étape. Ne jamais demander son mot de passe.

## Contrat d’entrée

### Dossier `produit`

Il contient une image par produit, ou un sous-dossier par produit avec une image principale.

Formats acceptés : `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`.

Le nom de fichier ou du sous-dossier détermine le nom du produit. Exemple : `Anka.webp` devient `Anka`.

### Dossier `image de référence`

Il contient exactement trois images ordonnées par un numéro explicite : `1`, `2`, `3`, idéalement au début du nom.

Exemples valides :

```text
01-salon-jour.png
02-salon-soir.png
03-cuisine.png
```

### Dossier `prompt`

Il contient exactement trois fichiers texte ordonnés par un numéro explicite : `1`, `2`, `3`.

Formats acceptés : `.txt`, `.md`.

Chaque prompt doit correspondre à la référence du même numéro.

### Dossier `image générée`

Le skill crée si nécessaire un sous-dossier par produit :

```text
image générée/Anka/
```

Il ne supprime et n’écrase jamais une image existante. En cas de conflit, il ajoute un suffixe horodaté ou demande confirmation.

## Procédure

### 1. Obtenir le chemin racine

Si aucun chemin absolu n’est fourni, demander uniquement :

> Quel est le chemin absolu du dossier racine « image à refaire (chatgpt) » ?

Développer `~`, résoudre le chemin et vérifier qu’il existe.

Critère de fin : le dossier racine existe et est lisible.

### 2. Faire l’inventaire avant d’ouvrir ChatGPT

Exécuter :

```bash
python3 scripts/inventory.py "/chemin/vers/image à refaire (chatgpt)"
```

Le script produit un manifeste JSON et refuse les collections ambiguës.

Ne lancer aucune génération si une collection n’a pas :

- au moins un produit ;
- exactement trois références numérotées ;
- exactement trois prompts numérotés ;
- un dossier de sortie identifiable.

Critère de fin : le manifeste est valide et chaque ligne de travail contient un produit, une référence, un prompt et une destination.

### 3. Traiter une collection, puis un produit

Ordre déterministe : collections par ordre alphabétique, puis produits par ordre alphabétique, puis variantes `1 → 2 → 3`.

Pour chaque produit, créer si nécessaire :

```text
<collection>/image générée/<Produit>/
```

Critère de fin : la destination du produit existe avant toute génération.

### 4. Générer une image

Pour chaque variante `N` :

1. Ouvrir **une nouvelle conversation temporaire ChatGPT**. Ne pas réutiliser la conversation de la variante précédente.
2. Cliquer sur l’ajout de fichiers.
3. Importer ensemble :
   - l’image réelle du produit ;
   - `image de référence N`.
4. Vérifier visuellement que les deux pièces jointes sont présentes.
5. Lire le fichier `prompt N` sans le modifier.
6. Coller le prompt intégralement.
7. Envoyer une seule fois.
8. Attendre la fin réelle de la génération. Tant que le bouton d’arrêt ou l’animation est visible, ne rien télécharger.
9. Si ChatGPT répond seulement par du texte, signale une erreur ou ne produit pas d’image, noter l’échec et réessayer une seule fois dans une nouvelle conversation.
10. Télécharger l’image originale avec le bouton de téléchargement de l’image, jamais par capture d’écran.

Pourquoi une nouvelle conversation par variante : les anciennes références restent dans le contexte et peuvent contaminer le décor suivant.

Critère de fin : un fichier image non vide a été téléchargé pour la variante courante.

### 5. Ranger et nommer

Déplacer le téléchargement vers :

```text
<collection>/image générée/<Produit>/<Produit>-01.png
<collection>/image générée/<Produit>/<Produit>-02.png
<collection>/image générée/<Produit>/<Produit>-03.png
```

Conserver l’extension réellement téléchargée si elle n’est pas PNG.

Écrire aussi un journal `generation-log.json` dans le dossier du produit avec :

- collection ;
- produit ;
- numéro de variante ;
- chemin du produit source ;
- chemin de la référence ;
- chemin du prompt ;
- chemin de sortie ;
- date ;
- statut `ok` ou `failed` ;
- message d’erreur éventuel.

Critère de fin : le résultat est dans le bon dossier et le journal correspond au fichier présent.

### 6. Vérifier avant de passer à la variante suivante

Contrôles mécaniques :

```bash
python3 scripts/verify_outputs.py "/chemin/vers/image à refaire (chatgpt)"
```

Contrôles visuels obligatoires :

- le luminaire visible correspond bien à l’image produit jointe ;
- le décor correspond à la référence `N` ;
- aucun autre luminaire n’a été ajouté ;
- pas de texte, logo ou filigrane inattendu ;
- pas de produit coupé ou déformé de manière manifeste.

En cas de doute sur la fidélité produit, classer la variante en `à_revoir` plutôt que de la déclarer terminée.

Critère de fin : fichier lisible, dimensions non nulles, bon produit, bon décor et aucun défaut bloquant visible.

### 7. Terminer le lot

Un produit est terminé uniquement lorsque ses trois sorties `01`, `02`, `03` sont présentes et valides.

Une collection est terminée uniquement lorsque tous ses produits sont terminés.

Rendre un bilan court :

```text
Collections : X
Produits : Y
Images attendues : Z
Images valides : Z
À revoir : 0
Échecs : 0
```

S’il reste une erreur, donner le chemin exact et la cause. Ne jamais annoncer « terminé » sur la seule base du nombre de clics.

## Reprise après interruption

Relancer l’inventaire, puis le vérificateur.

- Ignorer une variante uniquement si son fichier existe, s’ouvre correctement et figure en `ok` dans le journal.
- Reprendre au premier triplet incomplet.
- Ne pas régénérer silencieusement une image déjà valide.

## Erreurs et conduite à tenir

| Erreur | Action |
|---|---|
| Chemin racine inconnu | Demander seulement le chemin absolu |
| Deux dossiers candidats pour le même rôle | Montrer les chemins et demander lequel utiliser |
| Référence ou prompt sans numéro | Bloquer avant génération |
| Plus ou moins de 3 références/prompts | Bloquer la collection |
| Produit sans image lisible | Ignorer ce produit et le signaler |
| ChatGPT non connecté/CAPTCHA | Demander une intervention manuelle |
| Génération textuelle sans image | Une nouvelle conversation et un seul nouvel essai |
| Téléchargement introuvable | Vérifier le dossier Téléchargements, ne pas générer à nouveau immédiatement |
| Image produit infidèle | Marquer `à_revoir`, ne pas valider |
| Fichier de sortie existant | Ne pas écraser |

## Pièges à éviter

1. Importer seulement le décor et oublier l’image produit.
2. Inverser les numéros entre références et prompts.
3. Continuer dans la même conversation et contaminer la variante suivante.
4. Copier une version reformulée du prompt au lieu du fichier exact.
5. Faire une capture d’écran au lieu de télécharger l’original.
6. Se fier au nom affiché dans ChatGPT sans vérifier le chemin final.
7. Confondre « génération finie » avec « requête envoyée ».
8. Déclarer le lot terminé sans contrôle visuel produit par produit.

## Checklist finale

- [ ] Le chemin racine utilisé est consigné.
- [ ] Toutes les collections valides du manifeste ont été traitées.
- [ ] Chaque produit possède exactement trois sorties.
- [ ] Chaque sortie correspond au même numéro de référence et de prompt.
- [ ] Aucun fichier existant n’a été écrasé.
- [ ] Chaque image est lisible et non vide.
- [ ] Chaque produit est visuellement fidèle à sa source.
- [ ] Tous les journaux sont présents.
- [ ] Le total attendu égale le total valide, ou les exceptions sont listées avec leur chemin.
