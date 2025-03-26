use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    pubkey::Pubkey,
    program_error::ProgramError,
};
use std::collections::HashMap;
use serde::{Serialize, Deserialize};
use serde_json;

// Declare the program's entry point
entrypoint!(process_instruction);

// Define the program's ID 
solana_program::declare_id!("3oYm2ArhEFxH42uBZpsEqBzqfrWH4xquop4oNStTJ6M6");

// Account structure to store CID data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CidAccount {
    pub owner: Pubkey,
    pub cid_count: u64,
    pub latest_cid: String,
}

// Storage manager
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

    pub fn initialize(&mut self, account_key: Pubkey, owner: Pubkey) -> Result<(), ProgramError> {
        let key_str = account_key.to_string();
        if self.accounts.contains_key(&key_str) {
            return Err(ProgramError::AccountAlreadyInitialized);
        }

        let cid_account = CidAccount {
            owner,
            cid_count: 0,
            latest_cid: String::new(),
        };

        self.accounts.insert(key_str, cid_account);
        msg!("CID account initialized");
        Ok(())
    }

    pub fn store_cid(&mut self, account_key: &str, signer: &Pubkey, cid: String) -> Result<(), ProgramError> {
        let cid_account = self.accounts.get_mut(account_key)
            .ok_or(ProgramError::UninitializedAccount)?;

        if cid_account.owner != *signer {
            return Err(ProgramError::InvalidAccountData);
        }

        cid_account.latest_cid = cid;
        cid_account.cid_count += 1;

        msg!("CID stored successfully: {}", cid_account.latest_cid);
        Ok(())
    }
}

// Solana Smart Contract Entry Function
pub fn process_instruction(
    _program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_info = next_account_info(accounts_iter)?;

    msg!("Received instruction: {:?}", instruction_data);

    Ok(())
}
