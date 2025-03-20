from tortoise.models import Model
from tortoise import fields

class UploadedFile(Model):
    id = fields.IntField(pk=True)
    filename = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=500)
    uploaded_at = fields.DatetimeField(auto_now_add=True)
