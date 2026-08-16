// hooks/useMemory.ts — Hook React pour la mémoire SQLite
import { useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import { useGideonneStore } from "@/stores/gideonne.store";

interface Conversation { id: number; titre: string; cree_le: string; mis_a_jour_le: string; }

export function useMemory() {
  const { definirConversations, definirConversationActive, viderMessages } = useGideonneStore();

  const chargerConversations = useCallback(async () => {
    try { definirConversations(await invoke<Conversation[]>("lister_conversations")); }
    catch (e) { console.error("Erreur chargement conversations :", e); }
  }, [definirConversations]);

  const creerNouvelleConversation = useCallback(async () => {
    try {
      const titre = `Conversation du ${new Date().toLocaleDateString("fr-FR")}`;
      await invoke<number>("creer_conversation", { params: { titre } });
      await chargerConversations();
      definirConversationActive({ id: 0, titre, cree_le: "", mis_a_jour_le: "" });
      viderMessages();
    } catch (e) { console.error("Erreur création conversation :", e); }
  }, [definirConversations, definirConversationActive, viderMessages, chargerConversations]);

  return { creerNouvelleConversation, chargerConversations };
}
