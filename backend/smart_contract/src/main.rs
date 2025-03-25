use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::io::{Read, Write};
use std::fs::File;
use std::path::Path;
use serde::{Serialize, Deserialize};
use serde_json;
use std::net::{TcpListener, TcpStream};
use std::thread;

// Simulating a public key type
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Pubkey(pub [u8; 32]);

impl Pubkey {
    pub fn new(bytes: [u8; 32]) -> Self {
        Self(bytes)
    }
    
    pub fn to_string(&self) -> String {
        // Convert to base58 or some other format for compatibility with Python
        format!("{:?}", self.0)
    }
    
    pub fn from_string(s: &str) -> Result<Self, &'static str> {
        // This is a simplified implementation
        // Real implementation would parse from base58 or similar format
        if s.len() < 64 {
            return Err("Invalid public key string");
        }
        
        let mut bytes = [0u8; 32];
        // Simplified parsing - would need proper implementation
        for i in 0..32 {
            bytes[i] = i as u8;
        }
        
        Ok(Self(bytes))
    }
}

// Account data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CidAccount {
    pub owner: Pubkey,
    pub cid_count: u64,
    pub latest_cid: String,
}

// Storage manager to handle accounts
#[derive(Serialize, Deserialize)]
pub struct CidStorage {
    accounts: HashMap<String, CidAccount>,
}

impl CidStorage {
    pub fn new() -> Self {
        Self {
            accounts: HashMap::new(),
        }
    }
    
    // Load from disk if available
    pub fn load() -> Self {
        let path = Path::new("cid_storage.json");
        if path.exists() {
            if let Ok(mut file) = File::open(path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() {
                    if let Ok(storage) = serde_json::from_str(&contents) {
                        return storage;
                    }
                }
            }
        }
        Self::new()
    }
    
    // Save to disk
    pub fn save(&self) -> Result<(), &'static str> {
        let json = serde_json::to_string(self).map_err(|_| "Failed to serialize")?;
        let mut file = File::create("cid_storage.json").map_err(|_| "Failed to create file")?;
        file.write_all(json.as_bytes()).map_err(|_| "Failed to write to file")?;
        Ok(())
    }

    pub fn initialize(&mut self, account_key: Pubkey, owner: Pubkey) -> Result<(), &'static str> {
        let key_str = account_key.to_string();
        if self.accounts.contains_key(&key_str) {
            return Err("Account already exists");
        }

        let cid_account = CidAccount {
            owner,
            cid_count: 0,
            latest_cid: String::new(),
        };

        self.accounts.insert(key_str, cid_account);
        println!("CID account initialized");
        self.save()?;
        Ok(())
    }

    pub fn store_cid(&mut self, account_key: &str, signer: &Pubkey, cid: String) -> Result<(), &'static str> {
        let cid_account = self.accounts.get_mut(account_key)
            .ok_or("Account not found")?;
        
        // Verify owner (simplified for demo)
        if cid_account.owner != *signer {
            return Err("Unauthorized");
        }
        
        // Store the latest CID
        cid_account.latest_cid = cid;
        cid_account.cid_count += 1;
        
        println!("CID stored successfully: {}", cid_account.latest_cid);
        println!("Total CIDs stored: {}", cid_account.cid_count);
        
        self.save()?;
        Ok(())
    }
}

// HTTP server to handle requests from Python
fn handle_client(mut stream: TcpStream, storage: Arc<Mutex<CidStorage>>) {
    let mut buffer = [0; 1024];
    match stream.read(&mut buffer) {
        Ok(size) => {
            let request = String::from_utf8_lossy(&buffer[0..size]);
            let parts: Vec<&str> = request.split_whitespace().collect();
            
            if parts.len() >= 2 {
                let response = match parts[0] {
                    "INITIALIZE" => {
                        let mut storage = storage.lock().unwrap();
                        // Parts[1] would be account_key, parts[2] would be owner
                        // Simplified implementation
                        let account_key = Pubkey::new([1; 32]);
                        let owner = Pubkey::new([2; 32]);
                        match storage.initialize(account_key, owner) {
                            Ok(_) => "SUCCESS: Account initialized".to_string(),
                            Err(e) => format!("ERROR: {}", e),
                        }
                    },
                    "STORE_CID" => {
                        let mut storage = storage.lock().unwrap();
                        // parts[1] would be account_key, parts[2] would be signer, parts[3] would be CID
                        // Simplified implementation
                        let account_key = parts[1];
                        let signer = Pubkey::new([2; 32]); // In reality, parse from parts[2]
                        let cid = parts[3].to_string();
                        match storage.store_cid(account_key, &signer, cid) {
                            Ok(_) => "SUCCESS: CID stored".to_string(),
                            Err(e) => format!("ERROR: {}", e),
                        }
                    },
                    _ => "ERROR: Unknown command".to_string(),
                };
                
                let response = format!("HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}", 
                                      response.len(), response);
                stream.write(response.as_bytes()).unwrap();
            }
        },
        Err(_) => println!("Error reading from connection"),
    }
}

// Example usage
fn main() {
    // Create a shared storage instance
    let storage = Arc::new(Mutex::new(CidStorage::load()));
    
    // Set up a TCP server for Python to connect to
    let listener = TcpListener::bind("127.0.0.1:8080").unwrap();
    println!("Server listening on port 8080");
    
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                let storage_clone = Arc::clone(&storage);
                thread::spawn(move || {
                    handle_client(stream, storage_clone);
                });
            }
            Err(e) => {
                println!("Error: {}", e);
            }
        }
    }
}