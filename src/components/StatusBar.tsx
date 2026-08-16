// StatusBar.tsx — Barre de statut en bas de l'application
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { invoke } from "@tauri-apps/api/core";
import { useGideonneStore } from "@/stores/gideonne.store";

function StatusBar() {
  const { t, i18n } = useTranslation();
  const { modeleActif } = useGideonneStore();
  const [ollamaActif, setOllamaActif] = useState<boolean | null>(null);
  useEffect(() => {
    const verifier = async () => { try { setOllamaActif(await invoke<boolean>("verifier_ollama")); } catch { setOllamaActif(false); } };
    verifier();
    const i = setInterval(verifier, 30_000);
    return () => clearInterval(i);
  }, []);
  return (
    <footer className="status-bar" role="status">
      <div className="status-item">
        <span className={`status-indicateur ${ollamaActif===null?"status-indicateur--inconnu":ollamaActif?"status-indicateur--actif":"status-indicateur--inactif"}`} />
        <span>{ollamaActif===null?t("status.verification"):ollamaActif?t("status.ollama.actif"):t("status.ollama.inactif")}</span>
      </div>
      <div className="status-item"><span>{t("status.modele")} : </span><strong>{modeleActif||t("status.aucunModele")}</strong></div>
      <div className="status-item"><span>{t("status.langue")} : </span><strong>{i18n.language.toUpperCase()}</strong></div>
      <div className="status-item status-item--droite"><span>Gideonne v0.1.0</span></div>
    </footer>
  );
}
export default StatusBar;
