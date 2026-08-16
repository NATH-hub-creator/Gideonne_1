// tests/unit/memory_test.rs — Tests unitaires du module mémoire SQLite
#[cfg(test)]
mod tests {
    use rusqlite::Connection;

    fn creer_db_test() -> Connection {
        let conn = Connection::open_in_memory().expect("DB en mémoire impossible");
        conn.execute_batch("
            PRAGMA foreign_keys = ON;
            CREATE TABLE conversations (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                titre         TEXT    NOT NULL,
                cree_le       TEXT    NOT NULL DEFAULT (datetime('now')),
                mis_a_jour_le TEXT    NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role            TEXT    NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                contenu         TEXT    NOT NULL,
                cree_le         TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        ").expect("Tables impossibles à créer");
        conn
    }

    #[test]
    fn test_creer_conversation() {
        let conn = creer_db_test();
        conn.execute("INSERT INTO conversations (titre) VALUES (?1)", rusqlite::params!["Test"]).unwrap();
        let id: i64 = conn.query_row("SELECT id FROM conversations WHERE titre = 'Test'", [], |r| r.get(0)).unwrap();
        assert!(id > 0, "L'ID doit \u00eatre positif");
    }

    #[test]
    fn test_ajouter_message() {
        let conn = creer_db_test();
        conn.execute("INSERT INTO conversations (titre) VALUES ('Conv')", []).unwrap();
        let cid: i64 = conn.last_insert_rowid();
        conn.execute("INSERT INTO messages (conversation_id, role, contenu) VALUES (?1, 'user', 'Bonjour')", rusqlite::params![cid]).unwrap();
        conn.execute("INSERT INTO messages (conversation_id, role, contenu) VALUES (?1, 'assistant', 'Bonsoir')", rusqlite::params![cid]).unwrap();
        let nb: i64 = conn.query_row("SELECT COUNT(*) FROM messages WHERE conversation_id = ?1", rusqlite::params![cid], |r| r.get(0)).unwrap();
        assert_eq!(nb, 2, "Il doit y avoir 2 messages");
    }

    #[test]
    fn test_suppression_cascade() {
        let conn = creer_db_test();
        conn.execute("INSERT INTO conversations (titre) VALUES ('A supprimer')", []).unwrap();
        let cid: i64 = conn.last_insert_rowid();
        for i in 0..5 {
            conn.execute("INSERT INTO messages (conversation_id, role, contenu) VALUES (?1, 'user', ?2)",
                rusqlite::params![cid, format!("Msg {}", i)]).unwrap();
        }
        conn.execute("DELETE FROM conversations WHERE id = ?1", rusqlite::params![cid]).unwrap();
        let nb: i64 = conn.query_row("SELECT COUNT(*) FROM messages WHERE conversation_id = ?1",
            rusqlite::params![cid], |r| r.get(0)).unwrap();
        assert_eq!(nb, 0, "Suppression en cascade attendue");
    }

    #[test]
    fn test_role_invalide_rejete() {
        let conn = creer_db_test();
        conn.execute("INSERT INTO conversations (titre) VALUES ('Test r\u00f4le')", []).unwrap();
        let cid: i64 = conn.last_insert_rowid();
        let result = conn.execute(
            "INSERT INTO messages (conversation_id, role, contenu) VALUES (?1, 'invalide', 'test')",
            rusqlite::params![cid]);
        assert!(result.is_err(), "R\u00f4le invalide doit \u00eatre rejet\u00e9 par CHECK");
    }

    #[test]
    fn test_ordre_conversations() {
        let conn = creer_db_test();
        for titre in &["Premi\u00e8re", "Deuxi\u00e8me", "Troisi\u00e8me"] {
            conn.execute("INSERT INTO conversations (titre) VALUES (?1)", rusqlite::params![titre]).unwrap();
        }
        let mut stmt = conn.prepare("SELECT titre FROM conversations ORDER BY mis_a_jour_le DESC").unwrap();
        let titres: Vec<String> = stmt.query_map([], |r| r.get(0)).unwrap().filter_map(|r| r.ok()).collect();
        assert_eq!(titres.len(), 3);
        assert_eq!(titres[0], "Troisi\u00e8me", "La plus r\u00e9cente en premier");
    }
}
