// VoiceButton.tsx — Bouton de reconnaissance vocale
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useVoice } from "@/hooks/useVoice";

interface PropsVoiceButton { onTranscription: (texte: string) => void; }

function VoiceButton({ onTranscription }: PropsVoiceButton) {
  const { t } = useTranslation();
  const { demarrerEcoute, ecoute, disponible } = useVoice();
  const [erreur, setErreur] = useState<string | null>(null);

  const gererClic = async () => {
    if (ecoute || !disponible) return;
    setErreur(null);
    const res = await demarrerEcoute(5);
    if (res.succes && res.transcription) { onTranscription(res.transcription); }
    else { setErreur(res.message); setTimeout(() => setErreur(null), 3000); }
  };

  return (
    <div className="voice-button-zone">
      <button
        className={`voice-button ${ecoute?"voice-button--actif":""} ${!disponible?"voice-button--indisponible":""}`}
        onClick={gererClic} disabled={ecoute || !disponible}
        aria-label={ecoute?t("voix.ecoute"):disponible?t("voix.demarrer"):t("voix.indisponible")}
        title={!disponible?t("voix.indisponible"):undefined}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3Z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" x2="12" y1="19" y2="22"/>
        </svg>
      </button>
      {erreur && <div className="voice-erreur" role="alert">{erreur}</div>}
    </div>
  );
}
export default VoiceButton;
