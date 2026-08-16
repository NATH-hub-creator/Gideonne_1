// stores/gideonne.store.ts — Store global Zustand de Gideonne
import { create } from "zustand";
import { invoke } from "@tauri-apps/api/core";

export interface MessageStore {
  id: number;
  role: "user" | "assistant" | "system";
  contenu: string;
  cree_le: string;
}

export interface ConversationStore {
  id: number;
  titre: string;
  cree_le: string;
  mis_a_jour_le: string;
}

interface GideonneStore {
  conversations: ConversationStore[];
  conversationActive: ConversationStore | null;
  messages: MessageStore[];
  modeleActif: string;
  initialise: boolean;
  initialiser: () => Promise<void>;
  definirConversations: (convs: ConversationStore[]) => void;
  definirConversationActive: (conv: ConversationStore) => void;
  selectionnerConversation: (id: number) => Promise<void>;
  ajouterMessageLocal: (msg: Omit<MessageStore, "id">) => void;
  viderMessages: () => void;
  definirModele: (modele: string) => void;
}

let _idLocal = -1;

export const useGideonneStore = create<GideonneStore>((set, get) => ({
  conversations: [], conversationActive: null, messages: [],
  modeleActif: "llama3", initialise: false,

  initialiser: async () => {
    if (get().initialise) return;
    try {
      const convs = await invoke<ConversationStore[]>("lister_conversations");
      set({ conversations: convs, initialise: true });
    } catch { set({ initialise: true }); }
  },

  definirConversations: (convs) => set({ conversations: convs }),
  definirConversationActive: (conv) => set({ conversationActive: conv }),

  selectionnerConversation: async (id) => {
    const conv = get().conversations.find((c) => c.id === id);
    if (!conv) return;
    set({ conversationActive: conv, messages: [] });
    try {
      const msgs = await invoke<MessageStore[]>("charger_conversation", { conversationId: id });
      set({ messages: msgs });
    } catch (e) { console.error("Erreur chargement messages :", e); }
  },

  ajouterMessageLocal: (msg) =>
    set((state) => ({ messages: [...state.messages, { ...msg, id: _idLocal-- } as MessageStore] })),

  viderMessages: () => set({ messages: [] }),
  definirModele: (modele) => set({ modeleActif: modele }),
}));
