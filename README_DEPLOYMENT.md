# 🚀 Déploiement du site CoastMax sur GitHub Pages

## 📋 Instructions de déploiement

### 1. Préparer le repository GitHub

```bash
# Initialiser le repository local
git init
git add .
git commit -m "Initial commit - CoastMax POC Ariège"

# Créer un repository sur GitHub et le lier
git remote add origin https://github.com/VOTRE_USERNAME/coastmax-ariege.git
git branch -M main
git push -u origin main
```

### 2. Activer GitHub Pages

1. Aller dans **Settings** de votre repository GitHub
2. Scroll vers **Pages** dans le menu de gauche  
3. Dans **Source**, sélectionner **Deploy from a branch**
4. Choisir **main** et **/ (root)** ou **/docs** selon votre configuration
5. Cliquer **Save**

### 3. Configuration finale

Éditer `docs/_config.yml` :
```yaml
url: "https://VOTRE_USERNAME.github.io/coastmax-ariege"
baseurl: "/coastmax-ariege"  # Si repository nommé coastmax-ariege
```

### 4. Accès au site

Votre site sera disponible à :
`https://VOTRE_USERNAME.github.io/coastmax-ariege`

## 🗂️ Structure des fichiers

```
docs/
├── index.html              # Page principale avec carte interactive
├── coastmax_ariege.geojson # Données géographiques des segments
├── summary.json            # Statistiques résumées  
├── top_segments.json       # Top segments (distance/vitesse)
└── _config.yml            # Configuration GitHub Pages
```

## 🎯 Fonctionnalités du site

- ✅ **Carte interactive** avec Leaflet.js
- ✅ **Visualisation** des 50 meilleurs segments de roue libre
- ✅ **Filtres** par distance ou vitesse
- ✅ **Statistics** temps réel (records, moyennes)
- ✅ **Popup détaillés** sur chaque segment
- ✅ **Responsive design** mobile/desktop
- ✅ **Centrage automatique** sur segments sélectionnés

## 📊 Données CoastMax Ariège

### Records absolus
- **Distance record** : 6409m en 14.2 min (39 km/h max)
- **Vitesse record** : 73.6 km/h sur 2451m (5.3 min)

### Zone couverte
- **Département** : Ariège, France  
- **Segments analysés** : 50 meilleurs
- **Distance moyenne** : 2685m
- **Réseau** : Routes cyclables OSM

## 🔧 Développement local

Pour tester localement :
```bash
# Serveur HTTP simple
python -m http.server 8000 -d docs

# Ou avec Node.js
npx serve docs
```

Puis ouvrir `http://localhost:8000`

## 📝 Prochaines étapes

1. **Étendre à d'autres régions** (Cantal, Pyrénées centrales)
2. **Algorithme d'enchaînement** des segments
3. **Export GPX** des parcours  
4. **Intégration DEM réel** (Copernicus 30m)
5. **API temps réel** pour nouvelles simulations
