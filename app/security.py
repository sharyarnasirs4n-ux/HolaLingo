import os
import requests

from fastapi import HTTPException, status
from dotenv import load_dotenv
from jose import jwt, jwk
from pwdlib import PasswordHash

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


load_dotenv()



password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )



JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")


JWT_ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return int(user_id)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )



def verify_google_token(token: str) -> dict:
    try:
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")

        print("GOOGLE CLIENT ID EXISTS:", bool(google_client_id))
        print(
            "GOOGLE CLIENT ID PREFIX:",
            google_client_id[:20] if google_client_id else None
        )

        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            google_client_id,
        )

        print("GOOGLE TOKEN VERIFIED")
        print("GOOGLE TOKEN AUDIENCE:", idinfo.get("aud"))

        return idinfo

    except ValueError as error:
        print("GOOGLE TOKEN VERIFICATION ERROR:", error)

        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token"
        )

APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"


def verify_apple_token(
    identity_token: str,
    expected_nonce: str,
) -> dict:

    try:
       
        apple_client_id = os.getenv("APPLE_CLIENT_ID")

        if not apple_client_id:
            raise RuntimeError(
                "APPLE_CLIENT_ID is not set"
            )


       
        response = requests.get(
            APPLE_KEYS_URL,
            timeout=10,
        )

        response.raise_for_status()

        apple_keys = response.json()["keys"]


       
        header = jwt.get_unverified_header(
            identity_token
        )

        kid = header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=401,
                detail="Apple token has no key ID",
            )


        
        key_data = next(
            (
                key
                for key in apple_keys
                if key["kid"] == kid
            ),
            None,
        )

        if not key_data:
            raise HTTPException(
                status_code=401,
                detail="Apple signing key not found",
            )


       
        public_key = jwk.construct(
            key_data
        )


       
        claims = jwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=apple_client_id,
            issuer="https://appleid.apple.com",
        )


       
        token_nonce = claims.get("nonce")

        if token_nonce != expected_nonce:
            raise HTTPException(
                status_code=401,
                detail="Invalid Apple nonce",
            )


       
        return claims


    except HTTPException:
        raise


    except Exception as error:

        print(
            "APPLE TOKEN VERIFICATION ERROR:",
            error,
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid Apple identity token",
        )