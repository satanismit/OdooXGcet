import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from models import User
from config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def generate_temporary_password(length: int = 12) -> str:
    """Generate a random temporary password."""
    characters = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


# JWT Token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decode a JWT token and return the login_id."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        login_id: str = payload.get("sub")
        return login_id
    except JWTError:
        return None


# Login ID Generation Logic
async def generate_login_id(
    company_name: str,
    first_name: str,
    last_name: str,
    joining_date: datetime
) -> str:
    """
    Generate a unique login ID based on the format:
    [CompanyCode][NameCode][Year][Serial]
    
    - CompanyCode: First 2 letters of company_name (Uppercase)
    - NameCode: First 2 letters of first_name + First 2 letters of last_name (Uppercase)
    - Year: 4-digit year of joining
    - Serial: 4-digit incremental number (0001, 0002, etc.)
    
    Example: Company "Ode", User "John Doe", Joined 2022
    Result: ODJODO20220001
    """
    # Extract and format components
    company_code = extract_code(company_name, 2)
    first_name_code = extract_code(first_name, 2)
    last_name_code = extract_code(last_name, 2)
    year = str(joining_date.year)
    
    # Build the prefix (without serial)
    prefix = f"{company_code}{first_name_code}{last_name_code}{year}"
    
    # Find the next serial number for this prefix and year
    serial = await get_next_serial_number(prefix, joining_date.year)
    
    # Construct the full login ID
    login_id = f"{prefix}{serial:04d}"
    
    return login_id


def extract_code(text: str, length: int) -> str:
    """
    Extract the first 'length' alphabetic characters from text.
    If text has fewer than 'length' characters, pad with 'X'.
    
    Args:
        text: The input string
        length: Number of characters to extract
    
    Returns:
        Uppercase string of exactly 'length' characters
    """
    # Remove spaces and non-alphabetic characters
    cleaned = ''.join(char for char in text if char.isalpha())
    
    # Take first 'length' characters or pad with 'X'
    if len(cleaned) >= length:
        code = cleaned[:length]
    else:
        code = cleaned + ('X' * (length - len(cleaned)))
    
    return code.upper()


async def get_next_serial_number(prefix: str, year: int) -> int:
    """
    Get the next serial number for a given prefix and year.
    
    Args:
        prefix: The login ID prefix (e.g., "ODJODO2022")
        year: The year of joining
    
    Returns:
        The next serial number (1, 2, 3, etc.)
    """
    # Query all users with login IDs starting with this prefix
    pattern = f"^{prefix}"
    
    # Find all users with this prefix
    users = await User.find(
        {"login_id": {"$regex": pattern}}
    ).to_list()
    
    if not users:
        return 1
    
    # Extract serial numbers from existing login IDs
    serial_numbers = []
    for user in users:
        # The serial number is the last 4 digits
        try:
            serial = int(user.login_id[-4:])
            serial_numbers.append(serial)
        except ValueError:
            continue
    
    # Return the next serial number
    if serial_numbers:
        return max(serial_numbers) + 1
    else:
        return 1
