// i18n/index.ts — Initialisation i18next pour Gideonne (6 langues)
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import fr from "./locales/fr.json";
import en from "./locales/en.json";
import es from "./locales/es.json";
import moore from "./locales/moore.json";
import gurunsi from "./locales/gurunsi.json";
import la from "./locales/la.json";

i18n.use(initReactI18next).init({
  resources: {
    fr: { translation: fr }, en: { translation: en }, es: { translation: es },
    mos: { translation: moore }, gur: { translation: gurunsi }, la: { translation: la },
  },
  lng: "fr", fallbackLng: "fr",
  interpolation: { escapeValue: false },
  debug: false,
});

export default i18n;
