import secrets

def generate_random_otp(length: int = 6) -> str:
    if length <= 0:
        raise ValueError("OTP length must be greater than 0")

    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))
