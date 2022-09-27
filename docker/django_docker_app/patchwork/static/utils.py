from django.core.files.base import ContentFile

class TextFile(ContentFile):
    content_type = 'txt'


class UndefinedArg():
    pass