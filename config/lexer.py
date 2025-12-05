import re


class Token:
    def __init__(self, type, value, position=None):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.token_specs = [
            ('STRING', r'"([^"\\]|\\.)*"'),
            ('STRUCT', r'struct\b'),
            ('IDENTIFIER', r'[_A-Z][_a-zA-Z0-9]*'),  # Имена только с заглавных букв или _
            ('NUMBER', r'[+-]?\d+\.?\d*([eE][+-]?\d+)?'),  # ИСПРАВЛЕНО: числа могут быть без экспоненты
            ('COLON_EQUALS', r':='),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('COMMA', r','),
            ('EQUALS', r'='),
            ('SEMICOLON', r';'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MUL', r'\*'),
            ('DIV', r'/'),
            ('SKIP', r'[ \t\n]+'),
            ('MISMATCH', r'.'),
        ]
        self.regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specs)
        self.compiled_regex = re.compile(self.regex, re.DOTALL)

    def tokenize(self):
        while self.pos < len(self.text):
            # Обработка многострочных комментариев СТРОГО ПО ТЗ
            if self.text.startswith('<#', self.pos):
                end_pos = self.text.find('#>', self.pos + 2)
                if end_pos == -1:
                    raise SyntaxError(f"Unterminated comment starting at position {self.pos}")
                self.pos = end_pos + 2
                continue

            # Обработка выражений .[ ... ].
            if self.text.startswith('.[', self.pos):
                self._handle_expression()
                continue

            match = self.compiled_regex.match(self.text, self.pos)
            if not match:
                raise SyntaxError(f"Unexpected character at position {self.pos}: '{self.text[self.pos]}'")

            kind = match.lastgroup
            value = match.group()
            start_pos = match.start()

            if kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character: '{value}' at position {start_pos}")
            else:
                self.tokens.append(Token(kind, value, start_pos))

            self.pos = match.end()

        return self.tokens

    def _handle_expression(self):
        start_pos = self.pos
        content_start = self.pos + 2
        end_pos = self.text.find('].', content_start)

        if end_pos == -1:
            raise SyntaxError(f"Unterminated expression starting at position {start_pos}")

        content = self.text[content_start:end_pos]
        self.tokens.append(Token('START_EXPR', '.[', start_pos))
        self.tokens.append(Token('EXPR_CONTENT', content.strip(), content_start))
        self.tokens.append(Token('END_EXPR', '].', end_pos))
        self.pos = end_pos + 2