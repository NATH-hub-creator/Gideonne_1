# ==============================================================================
#  _   _    _    ____    _   _    _  _____     ___           _           _
# | \ | |  / \  / ___|  | \ | |  / \|_   _|  |_ _|_ __   __| |_   _ ___| |_ _ __ (_) ___  ___
# |  \| | / _ \| |  _   |  \| | / _ \ | |     | || '_ \ / _` | | | / __| __| '__| |/ _ \/ __|
# | |\  |/ ___ \ |_| |  | |\  |/ ___ \| |     | || | | | (_| | |_| \__ \ |_| |  | |  __/\__ \
# |_| \_/_/   \_\____|  |_| \_/_/   \_\_|    |___|_| |_|\__,_|\__,_|___/\__|_|  |_|\___||___/
#
#  Script d'installation automatique - Gideonne_1
#  Editeur  : NAG NAT Industries | Koudougou, Burkina Faso
#  Auteur   : Dr Nathanael (alias Zero Day)
#  Version  : 1.0.0
#  Cible    : Windows 10 / Windows 11 (PowerShell 5.1+)
# ==============================================================================
#
#  UTILISATION :
#      irm https://raw.githubusercontent.com/NATH-hub-creator/Gideonne_1/main/install.ps1 | iex
#
# ==============================================================================

#Requires -Version 5.1

# ------------------------------------------------------------------------------
# 0. CONFIGURATION GENERALE
# ------------------------------------------------------------------------------

$ErrorActionPreference = "Stop"
$ProgressPreference    = "SilentlyContinue"   # Accelere les telechargements

# Coordonnees du depot GitHub
$GITHUB_OWNER = "NATH-hub-creator"
$GITHUB_REPO  = "Gideonne_1"
$GITHUB_REF   = "main"
$ARCHIVE_URL  = "https://github.com/$GITHUB_OWNER/$GITHUB_REPO/archive/refs/heads/$GITHUB_REF.zip"

# Dossier d'installation (dans le profil utilisateur)
$INSTALL_DIR  = Join-Path $env:USERPROFILE "Gideonne_1"

# Version minimale de Python requise
$PYTHON_MIN_MAJOR = 3
$PYTHON_MIN_MINOR = 8

# ------------------------------------------------------------------------------
# 1. FONCTIONS UTILITAIRES
# ------------------------------------------------------------------------------

function Write-Banniere {
    <#
    .SYNOPSIS
        Affiche la banniere NAG NAT Industries en couleur.
    #>
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║          NAG NAT Industries - Gideonne_1 Installer          ║" -ForegroundColor Cyan
    Write-Host "  ║              Koudougou, Burkina Faso  *  v1.0.0             ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Etape {
    <#
    .SYNOPSIS
        Affiche un message d'etape numerotee.
    .PARAMETER Numero
        Numero de l'etape (ex : "1/6").
    .PARAMETER Message
        Description de l'etape.
    #>
    param(
        [string]$Numero,
        [string]$Message
    )
    Write-Host ""
    Write-Host "  [$Numero] $Message" -ForegroundColor Yellow
    Write-Host "  " + ("-" * 60) -ForegroundColor DarkGray
}

function Write-OK {
    <#
    .SYNOPSIS
        Affiche un message de succes.
    #>
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Info {
    <#
    .SYNOPSIS
        Affiche un message informatif neutre.
    #>
    param([string]$Message)
    Write-Host "  [..] $Message" -ForegroundColor Gray
}

function Write-Attention {
    <#
    .SYNOPSIS
        Affiche un avertissement non bloquant.
    #>
    param([string]$Message)
    Write-Host "  [!]  $Message" -ForegroundColor DarkYellow
}

function Stop-AvecErreur {
    <#
    .SYNOPSIS
        Affiche un message d'erreur critique et arrete le script.
    .PARAMETER Message
        Explication de l'erreur.
    .PARAMETER Conseil
        Action corrective proposee a l'utilisateur.
    #>
    param(
        [string]$Message,
        [string]$Conseil = ""
    )
    Write-Host ""
    Write-Host "  [ERREUR] $Message" -ForegroundColor Red
    if ($Conseil) {
        Write-Host "  [AIDE]   $Conseil" -ForegroundColor DarkYellow
    }
    Write-Host ""
    Write-Host "  Installation interrompue. Corrigez l'erreur ci-dessus et relancez le script." -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ------------------------------------------------------------------------------
# 2. VERIFICATION DE PYTHON
# ------------------------------------------------------------------------------

function Test-Python {
    <#
    .SYNOPSIS
        Verifie que Python 3.8 ou superieur est disponible sur le systeme.
    .OUTPUTS
        Le chemin absolu de l'executable Python valide.
    #>
    Write-Etape "1/6" "Verification de Python"

    # Candidats a tester dans l'ordre de preference
    $candidats = @("python", "python3", "py")

    foreach ($cmd in $candidats) {
        try {
            # Execution silencieuse pour obtenir la version
            $sortie = & $cmd --version 2>&1
            if ($sortie -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]

                if ($major -gt $PYTHON_MIN_MAJOR -or
                    ($major -eq $PYTHON_MIN_MAJOR -and $minor -ge $PYTHON_MIN_MINOR)) {
                    Write-OK "Python $major.$minor detecte ($cmd)"
                    return $cmd
                }
                else {
                    Write-Attention "Python $major.$minor trouve via '$cmd' - version insuffisante (minimum : 3.$PYTHON_MIN_MINOR)"
                }
            }
        }
        catch {
            # Commande introuvable, on passe au candidat suivant
        }
    }

    # Aucun Python valide trouve
    Stop-AvecErreur `
        "Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR ou superieur est requis mais n'a pas ete trouve." `
        "Telechargez Python sur https://www.python.org/downloads/ (cochez 'Add Python to PATH')."
}

# ------------------------------------------------------------------------------
# 3. TELECHARGEMENT ET EXTRACTION DU CODE SOURCE
# ------------------------------------------------------------------------------

function Get-CodeSource {
    <#
    .SYNOPSIS
        Telecharge l'archive ZIP du depot depuis GitHub et l'extrait localement.
    #>
    Write-Etape "2/6" "Telechargement du code source depuis GitHub"

    # Dossier temporaire pour l'archive
    $tmpDir      = Join-Path $env:TEMP "gideonne_install_$([System.Guid]::NewGuid().ToString('N').Substring(0,8))"
    $archivePath = Join-Path $tmpDir "Gideonne_1.zip"

    # Creation du dossier temporaire
    New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

    Write-Info "URL : $ARCHIVE_URL"
    Write-Info "Destination temporaire : $archivePath"

    try {
        Invoke-WebRequest -Uri $ARCHIVE_URL -OutFile $archivePath -UseBasicParsing
    }
    catch {
        Stop-AvecErreur `
            "Le telechargement a echoue : $($_.Exception.Message)" `
            "Verifiez votre connexion internet et reessayez."
    }

    Write-OK "Archive telechargee avec succes."

    # Extraction de l'archive
    Write-Info "Extraction en cours..."

    try {
        Expand-Archive -LiteralPath $archivePath -DestinationPath $tmpDir -Force
    }
    catch {
        Stop-AvecErreur `
            "L'extraction de l'archive a echoue : $($_.Exception.Message)" `
            "Verifiez que vous avez les droits d'ecriture dans le dossier temporaire."
    }

    # Le dossier extrait s'appelle toujours "<repo>-<ref>" (ex : Gideonne_1-main)
    $dossierExtrait = Join-Path $tmpDir "${GITHUB_REPO}-${GITHUB_REF}"

    if (-not (Test-Path $dossierExtrait)) {
        # Fallback : on cherche le premier sous-dossier disponible
        $sousDossiers = Get-ChildItem -Path $tmpDir -Directory
        if ($sousDossiers.Count -eq 0) {
            Stop-AvecErreur "L'extraction n'a produit aucun dossier." "L'archive est peut-etre corrompue."
        }
        $dossierExtrait = $sousDossiers[0].FullName
    }

    # Copie vers le dossier d'installation definitif
    Write-Info "Installation vers : $INSTALL_DIR"

    if (Test-Path $INSTALL_DIR) {
        Write-Attention "Le dossier '$INSTALL_DIR' existe deja. Il sera remplace."
        Remove-Item -LiteralPath $INSTALL_DIR -Recurse -Force
    }

    Copy-Item -Path $dossierExtrait -Destination $INSTALL_DIR -Recurse -Force
    Write-OK "Code source installe dans : $INSTALL_DIR"

    # Nettoyage des fichiers temporaires
    Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue

    return $INSTALL_DIR
}

# ------------------------------------------------------------------------------
# 4. CREATION DE L'ENVIRONNEMENT VIRTUEL PYTHON
# ------------------------------------------------------------------------------

function New-EnvVirtuel {
    <#
    .SYNOPSIS
        Cree un environnement virtuel Python dans le dossier d'installation.
    .PARAMETER PythonCmd
        Commande Python a utiliser (ex : "python", "python3").
    .PARAMETER DossierInstall
        Chemin absolu du dossier d'installation de Gideonne.
    .OUTPUTS
        Le chemin absolu du pip dans l'environnement virtuel.
    #>
    param(
        [string]$PythonCmd,
        [string]$DossierInstall
    )

    Write-Etape "3/6" "Creation de l'environnement virtuel Python"

    $envPath = Join-Path $DossierInstall ".venv"
    Write-Info "Emplacement du venv : $envPath"

    try {
        & $PythonCmd -m venv $envPath
    }
    catch {
        Stop-AvecErreur `
            "La creation de l'environnement virtuel a echoue : $($_.Exception.Message)" `
            "Assurez-vous que le module 'venv' est disponible (il est inclus par defaut avec Python 3.3+)."
    }

    Write-OK "Environnement virtuel cree."

    # Retourne le chemin du pip dans le venv
    $pipPath = Join-Path $envPath "Scripts\pip.exe"
    if (-not (Test-Path $pipPath)) {
        Stop-AvecErreur `
            "pip introuvable dans l'environnement virtuel ($pipPath)." `
            "L'environnement virtuel est peut-etre corrompu. Supprimez le dossier .venv et relancez."
    }

    return $pipPath
}

# ------------------------------------------------------------------------------
# 5. INSTALLATION DES DEPENDANCES
# ------------------------------------------------------------------------------

function Install-Dependances {
    <#
    .SYNOPSIS
        Installe toutes les dependances listees dans requirements.txt via pip.
    .PARAMETER PipCmd
        Chemin absolu vers le pip de l'environnement virtuel.
    .PARAMETER DossierInstall
        Chemin absolu du dossier d'installation de Gideonne.
    #>
    param(
        [string]$PipCmd,
        [string]$DossierInstall
    )

    Write-Etape "4/6" "Installation des dependances Python"

    $requirementsPath = Join-Path $DossierInstall "requirements.txt"

    if (-not (Test-Path $requirementsPath)) {
        Stop-AvecErreur `
            "Fichier requirements.txt introuvable dans : $DossierInstall" `
            "Verifiez que le telechargement du code source s'est bien passe."
    }

    Write-Info "Mise a jour de pip..."
    try {
        & $PipCmd install --upgrade pip --quiet
    }
    catch {
        Write-Attention "La mise a jour de pip a echoue (non bloquant) : $($_.Exception.Message)"
    }

    Write-Info "Installation des paquets depuis requirements.txt..."
    try {
        & $PipCmd install -r $requirementsPath
    }
    catch {
        Stop-AvecErreur `
            "L'installation des dependances a echoue : $($_.Exception.Message)" `
            "Verifiez votre connexion internet et les droits d'acces au dossier d'installation."
    }

    Write-OK "Toutes les dependances sont installees."
}

# ------------------------------------------------------------------------------
# 6. CONFIGURATION DE L'ENVIRONNEMENT (.env)
# ------------------------------------------------------------------------------

function Set-FichierEnv {
    <#
    .SYNOPSIS
        Cree un fichier .env a partir de .env.example si aucun .env n'existe.
    .PARAMETER DossierInstall
        Chemin absolu du dossier d'installation de Gideonne.
    #>
    param([string]$DossierInstall)

    Write-Etape "5/6" "Configuration de l'environnement (.env)"

    $envFile    = Join-Path $DossierInstall ".env"
    $envExample = Join-Path $DossierInstall ".env.example"

    if (Test-Path $envFile) {
        Write-OK "Fichier .env existant conserve (aucune modification)."
        return
    }

    if (Test-Path $envExample) {
        Copy-Item -Path $envExample -Destination $envFile
        Write-OK "Fichier .env cree a partir de .env.example."
        Write-Attention "IMPORTANT : Ouvrez le fichier .env et renseignez votre cle API OpenAI (OPENAI_API_KEY)."
        Write-Info "Emplacement : $envFile"
    }
    else {
        # Aucun fichier exemple - on cree un .env minimal avec des commentaires
        Write-Attention ".env.example introuvable. Creation d'un fichier .env minimal."
        $contenuMinimal = @"
# Gideonne_1 - Configuration minimale generee par install.ps1
# Completez les valeurs ci-dessous avant de lancer Gideonne.

# Cle API OpenAI (obligatoire)
OPENAI_API_KEY=sk-VOTRE_CLE_ICI

# Modele a utiliser
GIDEONNE_MODEL=gpt-4o-mini

# URL de base de l'API (laisser vide pour OpenAI)
OPENAI_BASE_URL=https://api.openai.com/v1

# Parametres du modele
GIDEONNE_MAX_TOKENS=2048
GIDEONNE_TEMPERATURE=0.7

# Taille de la memoire conversationnelle (en nombre de tours)
GIDEONNE_MEMORY_SIZE=20

# Niveau de log : DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
"@
        Set-Content -Path $envFile -Value $contenuMinimal -Encoding UTF8
        Write-Attention "IMPORTANT : Editez $envFile et renseignez votre cle OpenAI avant de lancer Gideonne."
    }
}

# ------------------------------------------------------------------------------
# 7. LANCEMENT DE GIDEONNE
# ------------------------------------------------------------------------------

function Start-Gideonne {
    <#
    .SYNOPSIS
        Lance Gideonne avec l'environnement virtuel configure.
    .PARAMETER DossierInstall
        Chemin absolu du dossier d'installation de Gideonne.
    #>
    param([string]$DossierInstall)

    Write-Etape "6/6" "Lancement de Gideonne"

    $pythonVenv = Join-Path $DossierInstall ".venv\Scripts\python.exe"
    $mainPy     = Join-Path $DossierInstall "main.py"

    if (-not (Test-Path $pythonVenv)) {
        Stop-AvecErreur `
            "Python de l'environnement virtuel introuvable : $pythonVenv" `
            "Relancez le script d'installation pour reconstruire l'environnement."
    }

    if (-not (Test-Path $mainPy)) {
        Stop-AvecErreur `
            "Point d'entree introuvable : $mainPy" `
            "Verifiez que le code source a ete correctement telecharge."
    }

    Write-OK "Demarrage de Gideonne..."
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║   Gideonne est pret. Tapez 'exit' pour quitter.             ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    # Changement de repertoire pour que les chemins relatifs fonctionnent
    Push-Location $DossierInstall
    try {
        & $pythonVenv $mainPy
    }
    catch {
        Pop-Location
        Stop-AvecErreur `
            "Gideonne a rencontre une erreur au demarrage : $($_.Exception.Message)" `
            "Verifiez que votre cle API est correctement renseignee dans le fichier .env."
    }
    Pop-Location
}

# ==============================================================================
# POINT D'ENTREE PRINCIPAL
# ==============================================================================

try {
    # Affichage de la banniere NAG NAT Industries
    Write-Banniere

    Write-Host "  Ce script va installer et configurer Gideonne_1 sur votre machine." -ForegroundColor White
    Write-Host "  Dossier d'installation : $INSTALL_DIR" -ForegroundColor White
    Write-Host ""

    # Etape 1 - Verification de Python
    $pythonCmd = Test-Python

    # Etape 2 - Telechargement et extraction du code source
    $dossierInstall = Get-CodeSource

    # Etape 3 - Creation de l'environnement virtuel
    $pipCmd = New-EnvVirtuel -PythonCmd $pythonCmd -DossierInstall $dossierInstall

    # Etape 4 - Installation des dependances
    Install-Dependances -PipCmd $pipCmd -DossierInstall $dossierInstall

    # Etape 5 - Configuration du fichier .env
    Set-FichierEnv -DossierInstall $dossierInstall

    # Resume de l'installation
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║              Installation terminee avec succes !            ║" -ForegroundColor Green
    Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Gideonne est installe dans : $dossierInstall" -ForegroundColor White
    Write-Host ""
    Write-Host "  Pour relancer Gideonne ulterieurement :" -ForegroundColor White
    Write-Host "    cd `"$dossierInstall`"" -ForegroundColor DarkCyan
    Write-Host "    .\.venv\Scripts\python.exe main.py" -ForegroundColor DarkCyan
    Write-Host ""

    # Etape 6 - Lancement automatique
    Start-Gideonne -DossierInstall $dossierInstall
}
catch {
    # Filet de securite global - capture toute exception non geree
    Write-Host ""
    Write-Host "  [ERREUR INATTENDUE] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Ligne : $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor DarkRed
    Write-Host ""
    Write-Host "  Signalez cette erreur a NAG NAT Industries avec le message ci-dessus." -ForegroundColor DarkYellow
    Write-Host ""
    exit 1
}
