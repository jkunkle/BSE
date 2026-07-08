
class Error:

    def __init__(self, etype, message=''):

        self._etype = etype
        self._message = message

    def __repr__(self):

        return f'{type(self._etype).__name__} : {self._etype} -- {self._message}'

