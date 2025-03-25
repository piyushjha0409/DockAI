import os
import base64
# import asyncio
from fastapi import HTTPException
from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import create_account, ID
from solders.keypair import Keypair
# import anchorpy
from anchorpy import Provider, Program, Wallet


# Solana Configuration from Environment Variables
SOLANA_RPC_ENDPOINT = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")
SOLANA_PROGRAM_ID = os.getenv("SOLANA_PROGRAM_ID", "YourProgramIDHere")
SOLANA_PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")
SOLANA_CID_ACCOUNT_KEY = os.getenv("SOLANA_CID_ACCOUNT_KEY")

# Initialize Solana client
solana_client = Client(SOLANA_RPC_ENDPOINT)

# Load wallet from private key if available, or create a new one
if SOLANA_PRIVATE_KEY:
    try:
        wallet = Keypair.from_bytes(base64.b64decode(SOLANA_PRIVATE_KEY))
    except Exception as e:
        print(f"Error loading wallet from private key: {str(e)}")
        wallet = Keypair()
else:
    wallet = Keypair()
    # Print wallet info for dev purposes
    print("⚠️ No private key found in environment. Using a randomly generated wallet.")
    print(f"Wallet public key: {wallet.public_key}")

# Load or initialize the persistent CID account
cid_account = None
if SOLANA_CID_ACCOUNT_KEY:
    try:
        cid_account_bytes = base64.b64decode(SOLANA_CID_ACCOUNT_KEY)
        cid_account = Keypair.from_bytes(cid_account_bytes)
        print(f"Using persistent CID account: {cid_account.public_key}")
    except Exception as e:
        print(f"Error loading CID account from key: {str(e)}")
        cid_account = None

# Program ID for the smart contract
program_id = Pubkey(SOLANA_PROGRAM_ID)


# Function to initialize the CID account if it doesn't exist yet
async def initialize_cid_account():
    global cid_account
    
    if cid_account is None:
        # Create a new keypair for the CID account
        cid_account = Keypair()
        print(f"Creating new CID account: {cid_account.public_key}")
        
        # Generate the account creation transaction
        txn = Transaction().add(
            create_account(
                from_pubkey=wallet.public_key,
                new_account_pubkey=cid_account.public_key,
                lamports=10000000,  # Adjust based on rent exemption calculation
                space=64,           # Adjust based on data size needs
                program_id=program_id
            )
        )
        
        # Send and confirm the transaction
        try:
            txn_signature = solana_client.send_transaction(txn, wallet, cid_account)
            print(f"Account creation transaction signature: {txn_signature}")
            
            # Confirm transaction success
            confirmation = solana_client.confirm_transaction(txn_signature)
            if not confirmation.value:
                raise Exception("Account creation failed to confirm")
                
            # Save the account key for future use
            print("CID Account created successfully. Export this value to reuse it:")
            print(f"SOLANA_CID_ACCOUNT_KEY={base64.b64encode(cid_account.secret_key).decode('utf-8')}")
            return str(txn_signature)
            
        except Exception as e:
            print(f"Error creating CID account: {str(e)}")
            raise e
    
    return "account_already_initialized"


async def store_cid_on_solana(cid: str):
    """
    Store a CID on the Solana blockchain using a persistent account
    
    Args:
        cid: The IPFS CID to store on Solana
        
    Returns:
        dict: Transaction details with signatures
    """
    print(f"Storing CID on Solana: {cid}")
    
    try:
        # Ensure the CID account is initialized
        init_signature = await initialize_cid_account()
        
        # Now interact with the smart contract using AnchorPy
        provider = Provider(solana_client, Wallet(wallet))
        
        # Determine the IDL file path - adjust as needed
        idl_path = os.getenv("SOLANA_PROGRAM_IDL", "YourProgramIDL.json")
        
        try:
            program = await Program.fetch(idl_path, provider)
            
            # Call the store_cid instruction
            tx = await program.rpc["store_cid"](cid, ctx={
                "accounts": {
                    "cid_account": cid_account.public_key,
                    "user": wallet.public_key,
                    "system_program": ID,
                },
                "signers": [wallet, cid_account] if init_signature != "account_already_initialized" else [wallet]
            })
            
            print(f"Stored CID on-chain. Transaction: {tx}")
            
            return {
                "account": str(cid_account.public_key),
                "create_signature": init_signature,
                "store_signature": str(tx)
            }
            
        except Exception as anchor_err:
            print(f"Anchor program error: {str(anchor_err)}")
            # If the program call fails, we still return the account info
            return {
                "account": str(cid_account.public_key),
                "create_signature": init_signature,
                "store_signature": "failed",
                "error": str(anchor_err)
            }
            
    except Exception as e:
        print(f"Solana transaction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store CID on Solana: {str(e)}")


