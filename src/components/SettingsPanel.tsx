// SettingsPanel.tsx — Panneau de paramètres (modal)
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { invoke } from "@tauri-apps/api/core";
import { useGideonneStore } from "@/stores/gideonne.store";

interface PropsSettings { onFermer: () => void; }

function SettingsPanel({ onFermer }: PropsSettings) {
  const { t, i18n } = useTranslation();
  const { modeleActif, definirModele } = useGideonneStore();
  const [modeles, setModeles] = useState<string[]>([]);
  const [modeleChoisi, setModeleChoisi] = useState(modeleActif);
  const [langueChoisie, setLangueChoisie] = useState(i18n.language);

  useEffect(() => { invoke<string[]>("lister_modeles").then(setModeles).catch(() => setModeles([])); }, []);

  const langues = [
    { code: "fr", label: "Français" }, { code: "en", label: "English" },
    { code: "es", label: "Español" }, { code: "mos", label: "Mooré" },
    { code: "gur", label: "Gurunsi" }, { code: "la", label: "Latina" },
  ];

  const sauvegarder = () => { definirModele(modeleChoisi); i18n.changeLanguage(langueChoisie); onFermer(); };

  return (
    <div className="modal-fond" role="dialog" aria-modal="true" onClick={(e) => { if (e.target === e.currentTarget) onFermer(); }}>
      <div className="modal-contenu">
        <div className="modal-entete">
          <h2>{t("parametres.titre")}</h2>
          <button className="bouton-fermer" onClick={onFermer}>&times;</button>
        </div>
        <div className="modal-corps">
          <div className="champ-formulaire">
            <label htmlFor="select-modele">{t("parametres.modeleIA")}</label>
            <select id="select-modele" value={modeleChoisi} onChange={(e) => setModeleChoisi(e.target.value)}>
              {modeles.length === 0
                ? <option value="">{t("parametres.aucunModele")}</option>
                : modeles.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="champ-formulaire">
            <label htmlFor="select-langue">{t("parametres.langue")}</label>
            <select id="select-langue" value={langueChoisie} onChange={(e) => setLangueChoisie(e.target.value)}>
              {langues.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
            </select>
          </div>
        </div>
        <div className="modal-pied">
          <button className="bouton-secondaire" onClick={onFermer}>{t("commun.annuler")}</button>
          <button className="bouton-principal" onClick={sauvegarder}>{t("commun.sauvegarder")}</button>
        </div>
      </div>
    </div>
  );
}
export default SettingsPanel;
