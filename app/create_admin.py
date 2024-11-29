
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def test_hashing():
    password = "1q2w3e4r"
    hashed = pwd_context.hash(password)
    print(f"Hashed password: {hashed}")
    if pwd_context.verify(password, hashed):
        print("Password hashing and verification successful.")
    else:
        print("Password verification failed.")

if __name__ == "__main__":
    test_hashing()