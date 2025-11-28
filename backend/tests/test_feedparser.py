"""
Mock feedparser module for testing purposes.
Provides minimal compatibility with feedparser API used in RSSRecipeScraper.
"""


class Munch(dict):
    """Mock Munch object - behaves like dict but with attribute access"""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


class _Munch:
    """Module for munch class"""
    Munch = Munch


munch = _Munch()


class Feed(Munch):
    """Mock Feed object"""
    def __init__(self, data=None):
        super().__init__(data or {})
        self["bozo"] = False
        self["bozo_exception"] = None


class Entry(Munch):
    """Mock Entry object"""
    def __init__(self, data=None):
        super().__init__(data or {})
        self["link"] = self.get("link", "")


class ParseResult:
    """Mock ParseResult object"""
    def __init__(self, feed_data=None, entries_data=None):
        self.feed = Feed(feed_data or {})
        self.entries = [Entry(e) for e in (entries_data or [])]
        self.bozo = False
        self.bozo_exception = None

    def __getitem__(self, key):
        if key == "feed":
            return self.feed
        elif key == "entries":
            return self.entries
        return None


def parse(url):
    """Mock parse function - returns empty ParseResult"""
    return ParseResult()
