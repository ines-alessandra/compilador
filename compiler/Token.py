class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token(type='{self.type}', value='{self.value}', line={self.line})"
    
    def __str__(self):
        return f"Token(type='{self.type}', value='{self.value}', line={self.line})"