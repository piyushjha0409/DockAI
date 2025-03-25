use anchor_lang::prelude::*;

declare_id!("Fcxy6et97fRDwCUgFbQjYZKqL55BVCnPD8Ct49LvsVzk");

#[program]
pub mod cid_storage {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let cid_account = &mut ctx.accounts.cid_account;
        cid_account.owner = ctx.accounts.user.key();
        cid_account.cid_count = 0;
        cid_account.latest_cid = String::new();
        msg!("CID account initialized");
        Ok(())
    }

    pub fn store_cid(ctx: Context<StoreCid>, cid: String) -> Result<()> {
        let cid_account = &mut ctx.accounts.cid_account;
        
        // Store the latest CID
        cid_account.latest_cid = cid;
        cid_account.cid_count += 1;
        
        msg!("CID stored successfully: {}", cid_account.latest_cid);
        msg!("Total CIDs stored: {}", cid_account.cid_count);
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = user, space = 8 + 32 + 8 + 64)]
    pub cid_account: Account<'info, CidAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct StoreCid<'info> {
    #[account(mut)]
    pub cid_account: Account<'info, CidAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct CidAccount {
    pub owner: Pubkey,
    pub cid_count: u64,
    pub latest_cid: String,
}