

class Version():
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self):
        return f"{self.major},{self.minor},{self.patch}"


def version(major, minor, patch):
    def decorator(cls):
        cls.version = Version(major, minor, patch)
        cls.get_version = cls.__name__ + "_" + cls.version