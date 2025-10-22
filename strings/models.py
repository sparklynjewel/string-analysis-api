from django.db import models

# Create your models here.
class AnalyzedString(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    value = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64)
    character_frequency_map = models.JSONField()

    def __str__(self):
        return self.value
