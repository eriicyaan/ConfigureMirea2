from config.ast import ConstDeclaration, String, Struct, Number, ConstExpression, Identifier


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def _advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _expect(self, token_type):
        if self.current_token is None or self.current_token.type != token_type:
            token_value = self.current_token.value if self.current_token else "EOF"
            position = self.current_token.position if self.current_token else -1
            raise SyntaxError(f"Expected {token_type}, got '{token_value}' at position {position}")
        token = self.current_token
        self._advance()
        return token

    def parse(self):
        consts = []

        # Парсим объявления констант
        while self.current_token and self.current_token.type == 'IDENTIFIER':
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == 'COLON_EQUALS':
                consts.append(self._parse_const_declaration())
            else:
                break

        # Корневая структура ОБЯЗАТЕЛЬНО должна быть struct {...} (по ТЗ)
        if not self.current_token or self.current_token.type != 'STRUCT':
            raise SyntaxError("Expected root struct at the end of configuration. Format: struct { ... }")

        root_struct = self._parse_struct()

        # После корневой структуры не должно быть ничего
        if self.current_token:
            raise SyntaxError(f"Unexpected content after root struct: {self.current_token.type}")

        return {'consts': consts, 'root': root_struct}

    def _parse_const_declaration(self):
        name_token = self._expect('IDENTIFIER')
        self._expect('COLON_EQUALS')
        value_node = self._parse_value()
        self._expect('SEMICOLON')
        return ConstDeclaration(name_token.value, value_node)

    def _parse_struct(self):
        self._expect('STRUCT')
        self._expect('LBRACE')

        fields = {}
        while self.current_token and self.current_token.type != 'RBRACE':
            name_token = self._expect('IDENTIFIER')  # Имена полей тоже должны начинаться с заглавной буквы
            self._expect('EQUALS')
            value_node = self._parse_value()
            fields[name_token.value] = value_node

            if self.current_token and self.current_token.type == 'COMMA':
                self._advance()

        self._expect('RBRACE')
        return Struct(fields)

    def _parse_value(self):
        if self.current_token.type == 'NUMBER':
            value = float(self.current_token.value)
            self._advance()
            return Number(value)
        elif self.current_token.type == 'STRUCT':
            return self._parse_struct()
        elif self.current_token.type == 'START_EXPR':
            return self._parse_const_expression()
        elif self.current_token.type == 'STRING':
            raw_value = self.current_token.value[1:-1]  # Удаляем кавычки
            value = raw_value.replace('\\"', '"').replace('\\\\', '\\')
            self._advance()
            return String(value)
        elif self.current_token.type == 'IDENTIFIER':
            # Это может быть ссылка на константу
            name = self.current_token.value
            self._advance()
            return Identifier(name)
        else:
            position = self.current_token.position if self.current_token else -1
            raise SyntaxError(f"Unexpected token in value: {self.current_token.type} at position {position}")

    def _parse_const_expression(self):
        self._expect('START_EXPR')
        content_token = self._expect('EXPR_CONTENT')
        self._expect('END_EXPR')

        tokens = []
        current = ''
        for char in content_token.value:
            if char in ' +-*/()':
                if current:
                    tokens.append(current)
                    current = ''
                if char != ' ':
                    tokens.append(char)
            else:
                current += char
        if current:
            tokens.append(current)
        return ConstExpression(tokens)