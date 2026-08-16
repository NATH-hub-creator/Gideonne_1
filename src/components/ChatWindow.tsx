// ChatWindow.tsx — Fenêtre de conversation principale
import { useRef, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useGideonneStore } from "@/stores/gideonne.store";
import { useAI } from "@/hooks/useAI";
import VoiceButton from "./VoiceButton";

function ChatWindow() {
  const { t } = useTranslation();
  const { messages } = useGideonneStore();
  const { envoyerMessage, chargement } = useAI();
  const [saisie, setSaisie] = useState("");
  const finListeRef = useRef<HTMLDivElement>(null);

  useEffect(() => { finListeRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const gererEnvoi = async () => {
    const texte = saisie.trim();
    if (!texte || chargement) return;
    setSaisie("");
    await envoyerMessage(texte);
  };

  const gererTouche = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); gererEnvoi(); }
  };

  return (
    <div className="chat-window">
      <div className="messages-liste" role="log" aria-live="polite">
        {messages.length === 0 ? (
          <div className="message-accueil">
            <h2>{t("accueil.titre")}</h2>
            <p>{t("accueil.description")}</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`message message--${msg.role}`}>
              <div className="message-role">{msg.role === "user" ? t("role.utilisateur") : t("role.assistant")}</div>
              <div className="message-contenu">{msg.contenu}</div>
              <div className="message-heure">{new Date(msg.cree_le).toLocaleTimeString()}</div>
            </div>
          ))
        )}
        {chargement && (
          <div className="message message--assistant message--chargement">
            <div className="message-role">{t("role.assistant")}</div>
            <div className="points-suspension"><span/><span/><span/></div>
          </div>
        )}
        <div ref={finListeRef} />
      </div>
      <div className="saisie-zone">
        <VoiceButton onTranscription={(txt) => setSaisie((p) => p + " " + txt)} />
        <textarea className="saisie-texte" value={saisie} onChange={(e) => setSaisie(e.target.value)}
          onKeyDown={gererTouche} placeholder={t("saisie.placeholder")} rows={1} disabled={chargement} />
        <button className="bouton-envoyer" onClick={gererEnvoi} disabled={!saisie.trim() || chargement}>
          {t("saisie.envoyer")}
        </button>
      </div>
    </div>
  );
}
export default ChatWindow;
