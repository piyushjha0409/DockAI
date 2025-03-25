import os
import requests
from fastapi import HTTPException

# Configuration
RUST_SERVER_URL = os.getenv("RUST_SERVER_URL", "http://127.0.0.1:8080")
USE_SOLANA = os.getenv("USE_SOLANA", "false").lower() == "true"

# If using Solana, keep the existing code
# This is a simplified version for working with the Rust implementation
async def store_cid_local(cid: str):
    """
    Store a CID using the native Rust implementation
    
    Args:
        cid: The IPFS CID to store
        
    Returns:
        dict: Operation details
    """
    print(f"Storing CID locally: {cid}")
    
    try:
        # For simplicity, we're using a fixed account key
        account_key = "account1"
        signer_key = "signer1"
        
        # Call the Rust server
        response = requests.post(
            RUST_SERVER_URL, 
            data=f"STORE_CID {account_key} {signer_key} {cid}"
        )
        
        if response.status_code == 200:
            return {
                "account": account_key,
                "status": "success",
                "cid": cid
            }
        else:
            return {
                "account": account_key,
                "status": "failed",
                "error": response.text
            }
            
    except Exception as e:
        print(f"Failed to store CID: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store CID: {str(e)}")

# Choose the implementation based on configuration
async def store_cid_on_solana(cid: str):
    """
    Store a CID either on Solana or using the local Rust implementation
    
    Args:
        cid: The IPFS CID to store
        
    Returns:
        dict: Operation details
    """
    if USE_SOLANA:
        # Use the original Solana implementation
        # (Keep the existing Solana code here)
        pass
    else:
        # Use the local Rust implementation
        return await store_cid_local(cid)