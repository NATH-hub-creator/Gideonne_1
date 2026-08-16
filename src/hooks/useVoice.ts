// hooks/useVoice.ts — Hook React pour la reconnaissance vocale (STT)
import { useState, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";

interface ResultatSTT { succes: boolean; transcription: string | null; langue_detectee: string | null; message: string; }

export function useVoice() {
  const [ecoute, setEcoute] = useState(false);
  const disponible = false; // TODO: passer à true en v0.2.0 (Whisper STT)

  const demarrerEcoute = useCallback(async (dureeSecondes: number): Promise<ResultatSTT> => {
    if (ecoute || !disponible) return { succes: false, transcription: null, langue_detectee: null, message: "Module voix non disponible (v0.2.0)." };
    setEcoute(true);
    try { return await invoke<ResultatSTT>("demarrer_ecoute", { dureeSecondes, langue: null }); }
    catch (e) { return { succes: false, transcription: null, langue_detectee: null, message: e instanceof Error ? e.message : String(e) }; }
    finally { setEcoute(false); }
  }, [ecoute, disponible]);

  return { demarrerEcoute, ecoute, disponible };
}
