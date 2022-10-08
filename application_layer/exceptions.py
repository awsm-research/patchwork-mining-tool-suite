class InvalidFileException(Exception):
    def __init__(self, message="Invalid file type. Only json or jsonlines files are supported.", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message


class InvalidItemTypeException(Exception):
    def __init__(self, message="Invalid item type. Supported item types include: accounts, projects, series, patches, comments.", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message

class PostRequestException(Exception):
    def __init__(self, response, *args, **kwargs):
        super().__init__(response, *args, **kwargs)
        self.response = response

    def __str__(self):
        return self.response.text