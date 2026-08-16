// App.tsx — Composant racine de Gideonne
import { useEffect, useState } from "react";
import ChatWindow from "@/components/ChatWindow";
import Sidebar from "@/components/Sidebar";
import StatusBar from "@/components/StatusBar";
import SettingsPanel from "@/components/SettingsPanel";
import { useGideonneStore } from "@/stores/gideonne.store";

function App() {
  const [parametresOuverts, setParametresOuverts] = useState(false);
  const { initialiser } = useGideonneStore();
  useEffect(() => { initialiser(); }, [initialiser]);
  return (
    <div className="app-container">
      <Sidebar onOuvrirParametres={() => setParametresOuverts(true)} />
      <main className="main-content"><ChatWindow /></main>
      <StatusBar />
      {parametresOuverts && <SettingsPanel onFermer={() => setParametresOuverts(false)} />}
    </div>
  );
}
export default App;
