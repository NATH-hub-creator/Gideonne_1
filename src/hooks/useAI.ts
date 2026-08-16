// hooks/useAI.ts — Hook React pour l'inférence IA via Ollama
import { useState, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { useGideonneStore } from "@/stores/gideonne.store";

interface RequeteIA { message: string; modele: string; historique: Array<{ role: string; contenu: string }>; }
interface ReponseIA { contenu: string; modele: string; succes: boolean; erreur: string | null; }

export function useAI() {
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const { messages, modeleActif, ajouterMessageLocal } = useGideonneStore();

  const envoyerMessage = useCallback(async (texte: string) => {
    if (!texte.trim() || chargement) return;
    setChargement(true); setErreur(null);
    ajouterMessageLocal({ role: "user", contenu: texte, cree_le: new Date().toISOString() });
    try {
      const historique = messages.slice(-20).map((m) => ({ role: m.role, contenu: m.contenu }));
      const requete: RequeteIA = { message: texte, modele: modeleActif || "llama3", historique };
      const reponse = await invoke<ReponseIA>("envoyer_message", { requete });
      if (reponse.succes) {
        ajouterMessageLocal({ role: "assistant", contenu: reponse.contenu, cree_le: new Date().toISOString() });
      } else {
        setErreur(reponse.erreur ?? "Erreur inconnue");
        ajouterMessageLocal({ role: "assistant", contenu: `Erreur : ${reponse.erreur ?? "Impossible de joindre Ollama."}`, cree_le: new Date().toISOString() });
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErreur(msg);
      ajouterMessageLocal({ role: "assistant", contenu: `Erreur : ${msg}`, cree_le: new Date().toISOString() });
    } finally { setChargement(false); }
  }, [chargement, messages, modeleActif, ajouterMessageLocal]);

  return { envoyerMessage, chargement, erreur };
}
