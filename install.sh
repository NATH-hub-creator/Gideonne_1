#!/usr/bin/env bash
# =============================================================================
#  install.sh - Script d'installation automatique de Gideonne_1
#  Cree par Axel pour NAG NAT Industries - Koudougou, Burkina Faso
#  Usage : curl -sSL https://raw.githubusercontent.com/NATH-hub-creator/Gideonne_1/main/install.sh | bash
# =============================================================================

set -euo pipefail

# ===========================================================================
# VARIABLES GLOBALES
# ===========================================================================
REPO_OWNER="NATH-hub-creator"
REPO_NAME="Gideonne_1"
BRANCH="main"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/${BRANCH}.zip"
INSTALL_DIR="${HOME}/.gideonne"
VENV_DIR="${INSTALL_DIR}/venv"
APP_DIR="${INSTALL_DIR}/${REPO_NAME}-${BRANCH}"
LOG_FILE="${INSTALL_DIR}/install.log"
PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=8

# Codes de couleur ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ===========================================================================
# FONCTIONS D'AFFICHAGE
# ===========================================================================

afficher_banniere() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "  +---------------------------------------------------------+"
    echo "  |                                                         |"
    echo "  |   ███╗   ██╗ █████╗  ██████╗                           |"
    echo "  |   ████╗  ██║██╔══██╗██╔════╝                           |"
    echo "  |   ██╔██╗ ██║███████║██║  ███╗                          |"
    echo "  |   ██║╚██╗██║██╔══██║██║   ██║                          |"
    echo "  |   ██║ ╚████║██║  ██║╚██████╔╝  NAT Industries          |"
    echo "  |   ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝                          |"
    echo "  |                                                         |"
    echo "  |         Koudougou, Burkina Faso                         |"
    echo "  +---------------------------------------------------------+"
    echo -e "${RESET}"
    echo -e "${CYAN}  ---------------------------------------------------------${RESET}"
    echo -e "${BOLD}                 Installation de Gideonne_1${RESET}"
    echo -e "${CYAN}  ---------------------------------------------------------${RESET}"
    echo ""
}

info() {
    echo -e "  ${CYAN}[INFO]   ${RESET} $*"
}

ok() {
    echo -e "  ${GREEN}[  OK ]  ${RESET} $*"
}

avertissement() {
    echo -e "  ${YELLOW}[AVERT]  ${RESET} $*"
}

erreur() {
    echo -e "  ${RED}[ERREUR] ${RESET} $*" >&2
    echo "" >&2
    echo -e "  ${RED}Installation abandonnee.${RESET}" >&2
    echo -e "  Consultez le journal : ${LOG_FILE}" >&2
    echo "" >&2
    exit 1
}

etape() {
    echo ""
    echo -e "  ${BOLD}>> $*${RESET}"
    echo -e "  ${CYAN}----------------------------------------------------------${RESET}"
}

# ===========================================================================
# FONCTIONS UTILITAIRES
# ===========================================================================

commande_disponible() {
    command -v "$1" &>/dev/null
}

# Compare deux versions : retourne 0 si maj1.min1 >= maj2.min2
version_ok() {
    local maj="$1" min="$2"
    if [ "$maj" -gt "$PYTHON_MIN_MAJOR" ]; then
        return 0
    elif [ "$maj" -eq "$PYTHON_MIN_MAJOR" ] && [ "$min" -ge "$PYTHON_MIN_MINOR" ]; then
        return 0
    else
        return 1
    fi
}

# ===========================================================================
# ETAPE 1 - VERIFICATION DE PYTHON
# ===========================================================================

verifier_python() {
    etape "Verification de Python ${PYTHON_MIN_MAJOR}.${PYTHON_MIN_MINOR}+"

    PYTHON_CMD=""

    for cmd in python3 python; do
        if commande_disponible "$cmd"; then
            local maj min ver
            maj=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null) || continue
            min=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null) || continue
            ver="${maj}.${min}"

            if version_ok "$maj" "$min"; then
                PYTHON_CMD="$cmd"
                ok "Python ${ver} detecte (${cmd})"
                break
            else
                avertissement "Python ${ver} trouve mais version minimale requise : ${PYTHON_MIN_MAJOR}.${PYTHON_MIN_MINOR}"
            fi
        fi
    done

    if [ -z "${PYTHON_CMD}" ]; then
        erreur "Python ${PYTHON_MIN_MAJOR}.${PYTHON_MIN_MINOR}+ est requis mais introuvable.
         Installez Python :
           Ubuntu/Debian : sudo apt install python3
           macOS (Homebrew) : brew install python3
           Site officiel  : https://www.python.org/downloads/"
    fi

    # Verifie pip
    if ! "${PYTHON_CMD}" -m pip --version >> "${LOG_FILE}" 2>&1; then
        erreur "pip est introuvable pour ${PYTHON_CMD}.
         Essayez : ${PYTHON_CMD} -m ensurepip --upgrade"
    fi

    ok "pip est disponible."
}

# ===========================================================================
# ETAPE 2 - TELECHARGEMENT DU CODE SOURCE
# ===========================================================================

telecharger_code() {
    etape "Telechargement du code source de Gideonne_1"

    mkdir -p "${INSTALL_DIR}"

    local zip_path="${INSTALL_DIR}/gideonne_source.zip"

    if commande_disponible curl; then
        info "Telechargement via curl..."
        if ! curl -sSL --fail "${REPO_URL}" -o "${zip_path}" 2>>"${LOG_FILE}"; then
            erreur "Impossible de telecharger depuis GitHub.
         Verifiez votre connexion internet.
         URL : ${REPO_URL}"
        fi
    elif commande_disponible wget; then
        info "Telechargement via wget..."
        if ! wget -q "${REPO_URL}" -O "${zip_path}" 2>>"${LOG_FILE}"; then
            erreur "Impossible de telecharger depuis GitHub.
         Verifiez votre connexion internet.
         URL : ${REPO_URL}"
        fi
    else
        erreur "Ni curl ni wget ne sont installes.
         Ubuntu/Debian : sudo apt install curl
         macOS (Homebrew) : brew install curl"
    fi

    ok "Archive telechargee."

    if ! commande_disponible unzip; then
        erreur "La commande unzip est requise mais introuvable.
         Ubuntu/Debian : sudo apt install unzip
         macOS          : unzip est inclus par defaut"
    fi

    # Supprime le dossier precedent si present
    if [ -d "${APP_DIR}" ]; then
        avertissement "Installation precedente detectee -- remplacement en cours..."
        rm -rf "${APP_DIR}"
    fi

    if ! unzip -q "${zip_path}" -d "${INSTALL_DIR}" 2>>"${LOG_FILE}"; then
        erreur "Impossible de decompresser l'archive. Fichier corrompu ?"
    fi

    rm -f "${zip_path}"
    ok "Code source extrait dans : ${APP_DIR}"
}

# ===========================================================================
# ETAPE 3 - CREATION DE L'ENVIRONNEMENT VIRTUEL
# ===========================================================================

creer_environnement_virtuel() {
    etape "Creation de l'environnement virtuel Python"

    if [ -d "${VENV_DIR}" ]; then
        avertissement "Environnement virtuel existant detecte -- recreation..."
        rm -rf "${VENV_DIR}"
    fi

    if ! "${PYTHON_CMD}" -m venv "${VENV_DIR}" >> "${LOG_FILE}" 2>&1; then
        erreur "Echec de la creation de l'environnement virtuel.
         Sous Ubuntu/Debian, installez :
           sudo apt install python3-venv"
    fi

    ok "Environnement virtuel cree : ${VENV_DIR}"
}

# ===========================================================================
# ETAPE 4 - INSTALLATION DES DEPENDANCES
# ===========================================================================

installer_dependances() {
    etape "Installation des dependances"

    local pip_cmd="${VENV_DIR}/bin/pip"
    local requirements="${APP_DIR}/requirements.txt"

    info "Mise a jour de pip..."
    if ! "${pip_cmd}" install --upgrade pip >> "${LOG_FILE}" 2>&1; then
        avertissement "Impossible de mettre a jour pip -- installation sur version actuelle."
    fi

    if [ -f "${requirements}" ]; then
        info "Fichier requirements.txt trouve -- installation des paquets..."
        if ! "${pip_cmd}" install -r "${requirements}" >> "${LOG_FILE}" 2>&1; then
            erreur "L'installation des dependances a echoue.
         Consultez le journal : ${LOG_FILE}"
        fi
        ok "Dependances installees avec succes."
    else
        avertissement "Aucun requirements.txt trouve -- etape ignoree."
    fi
}

# ===========================================================================
# ETAPE 5 - CONFIGURATION DU FICHIER .env
# ===========================================================================

configurer_env() {
    etape "Configuration de l'environnement (.env)"

    local env_file="${APP_DIR}/.env"
    local env_example="${APP_DIR}/.env.example"

    if [ -f "${env_file}" ]; then
        ok "Fichier .env deja present -- aucune modification effectuee."
        return 0
    fi

    if [ -f "${env_example}" ]; then
        cp "${env_example}" "${env_file}"
        ok "Fichier .env cree a partir de .env.example."
        avertissement "Editez ${env_file} avec vos parametres avant de lancer Gideonne."
    else
        avertissement "Aucun .env.example trouve. Creation d'un .env vide."
        touch "${env_file}"
        avertissement "Configurez manuellement ${env_file} avant le lancement."
    fi
}

# ===========================================================================
# ETAPE 6 - LANCEMENT DE GIDEONNE
# ===========================================================================

afficher_resume() {
    echo ""
    echo -e "  ${CYAN}==========================================================${RESET}"
    echo -e "  ${GREEN}${BOLD}  Installation terminee avec succes !${RESET}"
    echo -e "  ${CYAN}==========================================================${RESET}"
    echo ""
    echo -e "  ${BOLD}Recapitulatif :${RESET}"
    echo -e "    Repertoire : ${APP_DIR}"
    echo -e "    Venv       : ${VENV_DIR}"
    echo -e "    Journal    : ${LOG_FILE}"
    echo ""
    echo -e "  ${BOLD}Pour relancer Gideonne ulterieurement :${RESET}"
    echo ""
    echo -e "    cd ${APP_DIR}"
    echo -e "    source ${VENV_DIR}/bin/activate"
    echo -e "    python main.py"
    echo ""
    echo -e "  ${CYAN}  NAG NAT Industries - Koudougou, Burkina Faso${RESET}"
    echo -e "  ${CYAN}  https://github.com/${REPO_OWNER}/${REPO_NAME}${RESET}"
    echo ""
}

lancer_gideonne() {
    etape "Lancement de Gideonne_1"

    local python_venv="${VENV_DIR}/bin/python"
    local entree=""

    # Recherche du point d'entree dans l'ordre de priorite
    for candidat in main.py app.py gideonne.py run.py; do
        if [ -f "${APP_DIR}/${candidat}" ]; then
            entree="${candidat}"
            break
        fi
    done

    if [ -z "${entree}" ]; then
        avertissement "Aucun point d'entree detecte automatiquement (main.py, app.py, etc.)."
        echo ""
        echo -e "  ${BOLD}Pour lancer Gideonne manuellement :${RESET}"
        echo ""
        echo -e "    cd ${APP_DIR}"
        echo -e "    source ${VENV_DIR}/bin/activate"
        echo -e "    python <votre_fichier_principal>.py"
        echo ""
        afficher_resume
        return 0
    fi

    ok "Point d'entree detecte : ${entree}"
    info "Demarrage de Gideonne_1..."
    echo ""
    echo -e "  ${CYAN}==========================================================${RESET}"
    echo ""

    cd "${APP_DIR}"
    exec "${python_venv}" "${entree}"
}

# ===========================================================================
# POINT D'ENTREE PRINCIPAL
# ===========================================================================

main() {
    # Initialisation du journal
    mkdir -p "${INSTALL_DIR}"
    echo "=== Journal d'installation Gideonne_1 - $(date) ===" > "${LOG_FILE}"

    afficher_banniere

    verifier_python
    telecharger_code
    creer_environnement_virtuel
    installer_dependances
    configurer_env
    lancer_gideonne
}

main "$@"
