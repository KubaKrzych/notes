from django.db import models
from django.contrib.auth.models import User
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import os
from cryptography.hazmat.primitives import hashes


class Note(models.Model):
    ENCRYPTION_CHOICES = (
        ("N", "Not encrypted"),
        ("E", "Encrypted"),
    )
    SHARING_CHOICES = (
        ("P", "Public"),
        ("S", "Shared"),
        ("N", "Private"),
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    encryption_key = models.CharField(max_length=255, blank=True, null=True)
    encryption_status = models.CharField(
        max_length=1, choices=ENCRYPTION_CHOICES, default="N"
    )
    sharing_status = models.CharField(
        max_length=1, choices=SHARING_CHOICES, default="N"
    )
    salt = models.CharField(max_length=44, blank=True, null=True)

    def get_key(self, raw_key, salt):
        salt = base64.urlsafe_b64decode(salt.encode())

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(raw_key.encode()))
        return key

    def encrypt_content(self, raw_key):
        salt = os.urandom(16)
        self.salt = base64.urlsafe_b64encode(salt).decode()
        key = self.get_key(raw_key, self.salt)
        f = Fernet(key)
        self.content = f.encrypt(self.content.encode()).decode()

    def decrypt_content(self, raw_key):
        try:
            key = self.get_key(raw_key, self.salt)
            f = Fernet(key)
            return f.decrypt(self.content.encode()).decode()
        except InvalidToken:
            return "Decryption failed! Invalid key."


class SharedNote(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(
        User, related_name="shared_notes", on_delete=models.CASCADE
    )
