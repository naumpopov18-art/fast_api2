from fastapi import HTTPException, status

def create_token(user_id: int) -> str:
    return str(user_id)

def decode_token(token: str) -> int:
    try:
        return int(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")