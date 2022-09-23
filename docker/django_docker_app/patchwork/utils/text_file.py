from django.core.files import File

class TextFile(File):
    content_type = 'txt'