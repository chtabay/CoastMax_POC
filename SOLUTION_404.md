# 🔧 SOLUTION ERREUR 404 - GitHub Pages

## ❌ Problème
Site GitHub Pages inaccessible avec erreur 404 malgré commit et repository public.

## ✅ Solutions étape par étape

### 1. Vérifier la configuration GitHub Pages

1. Aller dans **Settings** de votre repository
2. Scroll vers **Pages** (menu gauche)
3. Vérifier la configuration :

**Option A - Déploiement depuis /docs :**
```
Source: Deploy from a branch
Branch: main
Folder: / (root) ← CHANGER POUR /docs
```

**Option B - Déploiement depuis la racine :**
```
Source: Deploy from a branch  
Branch: main
Folder: / (root)
```

### 2. Si Option A (/docs) - Recommandé

✅ **Aucun changement nécessaire** - tous les fichiers sont dans `docs/`

### 3. Si Option B (racine) - Déplacer les fichiers

```bash
# Déplacer les fichiers vers la racine
mv docs/index.html ./
mv docs/coastmax_ariege.geojson ./
mv docs/summary.json ./
mv docs/top_segments.json ./
mv docs/_config.yml ./
```

### 4. Problèmes fréquents et solutions

#### 🔍 **Problème : Site toujours 404 après 10 minutes**

**Solution 1 - Forcer la reconstruction :**
```bash
git commit --allow-empty -m "Trigger GitHub Pages rebuild"
git push
```

**Solution 2 - Vérifier l'URL :**
- URL correcte : `https://USERNAME.github.io/REPOSITORY-NAME/`
- Si repository = `coastmax-ariege` → `https://USERNAME.github.io/coastmax-ariege/`

**Solution 3 - Actions GitHub :**
1. Aller dans **Actions** tab
2. Vérifier que le workflow **pages build and deployment** s'exécute
3. Si erreur, cliquer sur le workflow pour voir les détails

#### 🔍 **Problème : Repository public mais Pages désactivées**

1. **Settings** → **Pages**
2. Si "GitHub Pages is currently disabled", sélectionner la source
3. **Save** pour activer

#### 🔍 **Problème : Fichiers manquants**

Vérifier que ces fichiers existent dans `/docs/` ou `/` :
- ✅ `index.html` (page principale)
- ✅ `coastmax_ariege.geojson` (données)
- ✅ `summary.json` (statistiques)
- ✅ `top_segments.json` (top segments)

### 5. Test local avant déploiement

```bash
# Test local dans le dossier docs/
python -m http.server 8000 -d docs
# Ouvrir http://localhost:8000

# Ou depuis la racine si fichiers déplacés
python -m http.server 8000
# Ouvrir http://localhost:8000
```

### 6. URL alternatives si problème persiste

Si GitHub Pages ne fonctionne pas, alternatives :

**Netlify Drop :**
1. Aller sur [netlify.com/drop](https://netlify.com/drop)
2. Glisser-déposer le dossier `docs/`
3. URL instantanée générée

**Vercel :**
```bash
npx vercel --prod docs/
```

### 7. Checklist finale

- [ ] Repository public ✓
- [ ] Fichiers commitées dans `docs/` ou `/` ✓
- [ ] GitHub Pages activé avec bonne source ✓
- [ ] Attendre 5-10 minutes après activation
- [ ] Tester URL : `https://USERNAME.github.io/REPOSITORY-NAME/`
- [ ] Vérifier Actions GitHub pour erreurs

### 8. Configuration recommandée finale

Dans **GitHub Settings → Pages** :

```
Source: Deploy from a branch
Branch: main  
Folder: /docs ← IMPORTANT
```

**URL finale :** `https://USERNAME.github.io/REPOSITORY-NAME/`

---

## 🚀 Commandes rapides

```bash
# Regenerer tous les fichiers
python src/prepare_web_data.py

# Commit et push
git add docs/
git commit -m "Fix GitHub Pages - complete site files"
git push

# Puis attendre 5-10 minutes et tester l'URL
```
