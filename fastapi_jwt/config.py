class Config:
    def __init__(self):
        self.config = {}

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value


config = Config()
