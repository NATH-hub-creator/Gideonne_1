// commands/security.rs — Chiffrement AES-256-GCM
use serde::{Deserialize, Serialize};
use tauri::command;
use aes_gcm::{aead::{Aead, AeadCore, KeyInit, OsRng}, Aes256Gcm, Key, Nonce};

#[derive(Debug, Serialize, Deserialize)]
pub struct DonneesChiffrees { pub succes: bool, pub message: String, pub donnees: Option<String> }

#[derive(Debug, Serialize, Deserialize)]
pub struct DonneesDechiffrees { pub succes: bool, pub message: String, pub donnees: Option<String> }

/// Chiffre des données avec AES-256-GCM
#[command]
pub async fn chiffrer_donnees(donnees: String, cle_hex: String) -> DonneesChiffrees {
    match chiffrer_interne(donnees.as_bytes(), &cle_hex) {
        Ok(c) => DonneesChiffrees { succes: true, message: "Chiffrement réussi.".to_string(), donnees: Some(c) },
        Err(e) => DonneesChiffrees { succes: false, message: format!("Erreur : {}", e), donnees: None },
    }
}

/// Déchiffre des données AES-256-GCM
#[command]
pub async fn dechiffrer_donnees(donnees_b64: String, cle_hex: String) -> DonneesDechiffrees {
    match dechiffrer_interne(&donnees_b64, &cle_hex) {
        Ok(c) => DonneesDechiffrees { succes: true, message: "Déchiffrement réussi.".to_string(), donnees: Some(c) },
        Err(e) => DonneesDechiffrees { succes: false, message: format!("Erreur : {}", e), donnees: None },
    }
}

fn chiffrer_interne(donnees: &[u8], cle_hex: &str) -> anyhow::Result<String> {
    let cle_bytes = hex::decode(cle_hex).map_err(|_| anyhow::anyhow!("Clé hex invalide"))?;
    let cle = Key::<Aes256Gcm>::from_slice(&cle_bytes);
    let algo = Aes256Gcm::new(cle);
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
    let ct = algo.encrypt(&nonce, donnees).map_err(|_| anyhow::anyhow!("Echec chiffrement"))?;
    let mut res = nonce.to_vec();
    res.extend_from_slice(&ct);
    Ok(b64_enc(&res))
}

fn dechiffrer_interne(b64: &str, cle_hex: &str) -> anyhow::Result<String> {
    let donnees = b64_dec(b64).map_err(|_| anyhow::anyhow!("Base64 invalide"))?;
    let cle_bytes = hex::decode(cle_hex).map_err(|_| anyhow::anyhow!("Clé hex invalide"))?;
    let cle = Key::<Aes256Gcm>::from_slice(&cle_bytes);
    let algo = Aes256Gcm::new(cle);
    if donnees.len() < 12 { return Err(anyhow::anyhow!("Données trop courtes")); }
    let (nb, ct) = donnees.split_at(12);
    let nonce = Nonce::from_slice(nb);
    let clair = algo.decrypt(nonce, ct).map_err(|_| anyhow::anyhow!("Echec déchiffrement"))?;
    String::from_utf8(clair).map_err(|e| anyhow::anyhow!("UTF-8 invalide : {}", e))
}

fn b64_enc(d: &[u8]) -> String {
    let a = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut r = Vec::new();
    for c in d.chunks(3) {
        let b0=c[0] as usize; let b1=if c.len()>1{c[1] as usize}else{0}; let b2=if c.len()>2{c[2] as usize}else{0};
        r.push(a[b0>>2]); r.push(a[((b0&3)<<4)|(b1>>4)]);
        if c.len()>1{r.push(a[((b1&15)<<2)|(b2>>6)])}else{r.push(b'=')};
        if c.len()>2{r.push(a[b2&63])}else{r.push(b'=')};
    }
    String::from_utf8(r).unwrap_or_default()
}

fn b64_dec(s: &str) -> Result<Vec<u8>,()> {
    let s: Vec<u8>=s.bytes().filter(|&b|b!=b'\n'&&b!=b'\r').collect();
    let mut out=Vec::new();
    let lk=|c:u8|->Result<u8,()>{match c{b'A'..=b'Z'=>Ok(c-b'A'),b'a'..=b'z'=>Ok(c-b'a'+26),b'0'..=b'9'=>Ok(c-b'0'+52),b'+'=>Ok(62),b'/'=>Ok(63),b'='=>Ok(0),_=>Err(())}};
    for c in s.chunks(4){if c.len()<4{break;}let(a,b,cc,d)=(lk(c[0])?,lk(c[1])?,lk(c[2])?,lk(c[3])?);
        out.push((a<<2)|(b>>4));if c[2]!=b'='{out.push((b<<4)|(cc>>2));}if c[3]!=b'='{out.push((cc<<6)|d);}}
    Ok(out)
}
