// i18n/languages.rs — Traductions backend pour 6 langues
// Français, Anglais, Espagnol, Mooré, Gurunsi, Latin

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum Langue { Francais, Anglais, Espagnol, Moore, Gurunsi, Latin }

impl Langue {
    pub fn depuis_code(code: &str) -> Self {
        match code { "en"=>Self::Anglais, "es"=>Self::Espagnol, "mos"|"moore"=>Self::Moore, "gur"|"gurunsi"=>Self::Gurunsi, "la"|"lat"=>Self::Latin, _=>Self::Francais }
    }
    pub fn code(&self) -> &'static str {
        match self { Self::Francais=>"fr", Self::Anglais=>"en", Self::Espagnol=>"es", Self::Moore=>"mos", Self::Gurunsi=>"gur", Self::Latin=>"la" }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum CleTraduction { Demarrage, Arret, ErreurOllama, ErreurBase, PluginCharge, ConfigChargee }

pub fn obtenir_traduction(cle: &CleTraduction, langue: &Langue) -> &'static str {
    match (cle, langue) {
        (CleTraduction::Demarrage, Langue::Francais) => "Gideonne démarre...",
        (CleTraduction::Demarrage, Langue::Anglais) => "Gideonne is starting...",
        (CleTraduction::Demarrage, Langue::Espagnol) => "Gideonne iniciando...",
        (CleTraduction::Demarrage, Langue::Moore) => "Gideonne yika...",
        (CleTraduction::Demarrage, Langue::Gurunsi) => "Gideonne sengua...",
        (CleTraduction::Demarrage, Langue::Latin) => "Gideonne incipit...",
        (CleTraduction::Arret, Langue::Francais) => "Gideonne s'arrête.",
        (CleTraduction::Arret, _) => "Gideonne is stopping.",
        (CleTraduction::ErreurOllama, Langue::Francais) => "Impossible de joindre Ollama.",
        (CleTraduction::ErreurOllama, _) => "Cannot reach Ollama.",
        (CleTraduction::ErreurBase, Langue::Francais) => "Erreur de base de données.",
        (CleTraduction::ErreurBase, _) => "Database error.",
        (CleTraduction::PluginCharge, Langue::Francais) => "Plugin chargé.",
        (CleTraduction::PluginCharge, _) => "Plugin loaded.",
        (CleTraduction::ConfigChargee, Langue::Francais) => "Configuration chargée.",
        (CleTraduction::ConfigChargee, _) => "Configuration loaded.",
    }
}
