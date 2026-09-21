# AGENTS.md — instruments-check

## But du projet
App **« Mes instruments »** pour 2 enfants sur **iPad mini 4** (Safari ancien, max iPadOS 15.x).
Chaque enfant a un panneau mission (Edwin → 🎹 Piano, Ambre → 🎻 Violon) sur **2 colonnes**.
Bouton **Fait** → étoile débloquée **immédiatement**. Bouton **🎁 Cadeau Bonus** (popup de
confirmation) → débloque le panneau carte du dessous : une **carte aléatoire du jour**, image seule.
Déployé sur **GitHub Pages** (repo `gfahrni/instruments-check`).

## Stack
- HTML/CSS/JS statique uniquement, sans build, sans dépendance, sans framework.
- Déploiement : push sur `main` → GitHub Pages.

## Structure
- `index.html` : layout 2 colonnes + logique (JS simple, tout inline).
- `instruments-v1.css` : thème versionné. **Renommer à chaque changement visuel**
  (ex: `instruments-v2.css`) pour forcer le cache Safari.
- `cartes.json` : `{ edwin: {...cartes}, ambre: {...cartes} }` — généré depuis
  `cartes-collections.md` (voir plus bas). Chaque carte = `{id, num, nom, type, img}`.
- `cartes/mario/<n>.jpg`, `cartes/mario/le<n>.jpg`, `cartes/disney/<n>.jpg` : images locales
  (offline). 431 images = 261 Panini Super Mario + 170 Topps Disney Princess.
- `telecharger-cartes.py` : télécharge les images manquantes listées dans `cartes.json`.
- `cartes-collections.md` : liste source des cartes (Mario, Disney, filles, listes Edwin/Ambre).

## Données / sets
- **Edwin (mario)** = collection Panini Super Mario **sans** les personnages filles → 209 cartes.
- **Ambre (peach)** = Disney Princess (170) + personnages filles Super Mario (52) → 222 cartes.
- Images hotlinkées depuis laststicker.com une seule fois puis **stockées dans le repo**.

## Contraintes iPad mini 4 (importantes)
- Compatible Safari iOS 15 : JS ES5 (pas de modules ES, optional chaining, etc.).
- Garder les meta iOS : `viewport-fit=cover`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`.
- Tactile first : grosses zones de toucher, pas de hover-only.
- Tester en conditions réelles : ajout à l'écran d'accueil + mode plein écran.

## Conventions de travail
- Modifier `index.html` directement, garder le fichier petit et lisible.
- **Reset quotidien** : `resetIfNewDay()` / `clearAll()` (`index.html`) efface tout (mission, étoile,
  cadeau) à chaque nouveau jour (clé `instruments-v1-day`). Recharge aussi au retour d'app (visibilitychange/pageshow).
- **Carte du jour** : déterministe `hash(date|enfant) % nbCartes` → même carte toute la journée,
  change le lendemain. Pas de stockage de la carte nécessaire.
- État sous préfixe `instruments-v1-` (`fait-<enfant>`, `bonus-<enfant>`, `day`).
- Un test = un commit clair (ex: `test: layout 2 colonnes iOS 15`).
- Ne pas ajouter de tooling/build sans demande explicite.
- Langue UI : français.
