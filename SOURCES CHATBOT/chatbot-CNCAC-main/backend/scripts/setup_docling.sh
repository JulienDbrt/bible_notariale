#!/bin/bash
# Installation de Docling et ses dépendances pour le Protocole Opérationnel

echo "🚀 Installation de Docling pour le parsing universel de documents"
echo "=" * 60

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Environnement virtuel activé"
fi

# Installation de base de Docling
echo "📦 Installation de Docling..."
pip install --upgrade pip
pip install docling docling-core docling-parse

# Installation des dépendances pour formats spécifiques
echo "📦 Installation des parseurs additionnels..."
pip install python-docx  # Pour DOCX
pip install openpyxl     # Pour XLSX
pip install odfpy        # Pour OpenDocument (ODT, ODS, ODP)
pip install extract-msg  # Pour emails .msg
pip install python-pptx  # Pour PowerPoint

# Installation des dépendances OCR (optionnel mais recommandé)
echo "🔍 Installation des dépendances OCR..."
pip install easyocr      # OCR neural network based
# ou tesseract : pip install pytesseract

# Vérification de l'installation
echo ""
echo "✅ Vérification de l'installation..."
python -c "
try:
    from docling.document_converter import DocumentConverter
    print('✅ Docling installé avec succès')
    
    # Vérifier les formats supportés
    import docx
    print('✅ Support DOCX activé')
    
    import openpyxl
    print('✅ Support XLSX activé')
    
    import odf
    print('✅ Support OpenDocument activé')
    
    import extract_msg
    print('✅ Support emails MSG activé')
    
    print('')
    print('🎯 Formats supportés :')
    print('  - PDF (avec OCR)')
    print('  - Microsoft Office : DOCX, XLSX, PPTX')
    print('  - OpenDocument : ODT, ODS, ODP')
    print('  - Emails : EML, MSG')
    print('  - Web : HTML, XML')
    print('  - Text : TXT, MD, RTF, CSV')
    
except ImportError as e:
    print(f'❌ Erreur: {e}')
    print('Veuillez vérifier l\'installation')
"

echo ""
echo "🏁 Installation terminée !"
echo ""
echo "📝 Usage du protocole opérationnel :"
echo "  python protocole_operationnel.py           # Mode batch unique"
echo "  python protocole_operationnel.py --daemon  # Mode surveillance continue"
echo "  python protocole_operationnel.py --force   # Forcer le retraitement"