// Sidebar.tsx — Barre latérale de navigation
import { useTranslation } from "react-i18next";
import { useGideonneStore } from "@/stores/gideonne.store";
import { useMemory } from "@/hooks/useMemory";

interface PropsSidebar { onOuvrirParametres: () => void; }

function Sidebar({ onOuvrirParametres }: PropsSidebar) {
  const { t } = useTranslation();
  const { conversations, conversationActive, selectionnerConversation } = useGideonneStore();
  const { creerNouvelleConversation } = useMemory();
  return (
    <aside className="sidebar">
      <div className="sidebar-entete">
        <h1 className="sidebar-titre">Gideonne</h1>
        <button className="bouton-nouvelle-conv" onClick={creerNouvelleConversation}>+</button>
      </div>
      <nav className="conversations-liste">
        {conversations.length === 0
          ? <p className="conversations-vides">{t("sidebar.aucuneConversation")}</p>
          : conversations.map((conv) => (
              <button key={conv.id}
                className={`conversation-item ${conversationActive?.id === conv.id ? "conversation-item--active" : ""}`}
                onClick={() => selectionnerConversation(conv.id)}>
                <span className="conversation-titre">{conv.titre}</span>
                <span className="conversation-date">{new Date(conv.mis_a_jour_le).toLocaleDateString()}</span>
              </button>
            ))
        }
      </nav>
      <div className="sidebar-pied">
        <button className="bouton-parametres" onClick={onOuvrirParametres}>{t("sidebar.parametres")}</button>
      </div>
    </aside>
  );
}
export default Sidebar;
