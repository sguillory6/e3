from HTMLParser import HTMLParser


class MetaAttributeParser(HTMLParser):
    def __init__(self, meta_name):
        HTMLParser.__init__(self)
        self._meta_name = meta_name
        self.recording = 0
        self.meta_content = ""
        self._found = False

    def handle_starttag(self, tag, attributes):
        if tag != 'meta':
            return

        for name, value in attributes:
            if self._found:
                self._found = False
                self.meta_content = value
                return

            if name == 'name' and value == self._meta_name:
                self._found = True
                continue