class Node:
    pass

class ConstDeclaration(Node):
    def __init__(self, name, value_node):
        self.name = name
        self.value_node = value_node

class Struct(Node):
    def __init__(self, fields=None):
        self.fields = fields if fields is not None else {}

class Number(Node):
    def __init__(self, value):
        self.value = value

class ConstExpression(Node):
    def __init__(self, tokens):
        self.tokens = tokens

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class String(Node):
    def __init__(self, value):
        self.value = value