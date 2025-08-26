#!/usr/bin/env python3
"""
Déploiement de la version France sur GitHub Pages.
"""

import shutil
import os
from pathlib import Path


def deploy_france_version():
    """Déploie la version France en remplaçant la version Ariège."""
    print("🚀 Déploiement de la version France sur GitHub Pages...")
    
    # Copier les fichiers France vers la racine docs
    france_dir = Path("docs/france")
    docs_dir = Path("docs")
    
    if not france_dir.exists():
        print("❌ Dossier docs/france introuvable")
        return
    
    # Fichiers à copier
    files_to_copy = [
        "index.html",
        "france_structure.json", 
        "pyrenees_stats.json",
        "pyrenees_top.json"
    ]
    
    for file_name in files_to_copy:
        src = france_dir / file_name
        dst = docs_dir / file_name
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Copié: {file_name}")
        else:
            print(f"⚠️  Fichier manquant: {file_name}")
    
    # Créer un fichier de redirection pour l'ancienne version
    redirect_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoastMax - Redirection</title>
    <meta http-equiv="refresh" content="3;url=index.html">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f8f9fa;
        }
        .redirect-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        h1 { color: #667eea; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="redirect-box">
        <h1>🚴 CoastMax</h1>
        <p>Redirection vers la nouvelle version France...</p>
        <div class="spinner"></div>
        <p><small>Si la redirection ne fonctionne pas, <a href="index.html">cliquez ici</a></small></p>
    </div>
</body>
</html>"""
    
    with open(docs_dir / "redirect.html", 'w', encoding='utf-8') as f:
        f.write(redirect_html)
    
    print("✅ Fichier de redirection créé")
    print("\n🎯 Déploiement terminé !")
    print("   📁 Fichiers copiés vers docs/")
    print("   🔄 Redirection automatique configurée")
    print("\n📋 Prochaines étapes:")
    print("   1. git add docs/")
    print("   2. git commit -m 'Deploy France version'")
    print("   3. git push")
    print("   4. Attendre 5-10 minutes")
    print("   5. Tester: https://USERNAME.github.io/REPOSITORY/")


def main():
    """Point d'entrée principal."""
    deploy_france_version()


if __name__ == "__main__":
    main()
