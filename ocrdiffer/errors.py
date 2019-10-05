class Error(Exception):
    pass


class BaiduOCRError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class SogouOCRError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class AliOCRError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class OCREngineUnknownError(Error):
    pass
