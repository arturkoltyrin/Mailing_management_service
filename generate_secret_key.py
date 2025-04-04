import random
import string

def generate_secret_key(length=50):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

secret_key = generate_secret_key()
print(secret_key)