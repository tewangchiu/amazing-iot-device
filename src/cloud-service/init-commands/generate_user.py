import random
import string


def generate_username():
    # You can customize the username generation logic as needed
    return 'dev_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(characters, k=length))
    return password

# Generate username and password
username = generate_username()
password = generate_password()

print(f"Username: {username}")
print(f"Password: {password}")
