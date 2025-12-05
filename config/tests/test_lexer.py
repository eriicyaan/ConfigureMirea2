import unittest
from config.lexer import Lexer, Token


class TestLexer(unittest.TestCase):
    def test_basic_tokens(self):
        input_text = 'struct { Port = 8080; }'
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        # Проверяем только типы и значения, игнорируя позиции
        token_data = [(t.type, t.value) for t in tokens]
        expected = [
            ('STRUCT', 'struct'),
            ('LBRACE', '{'),
            ('IDENTIFIER', 'Port'),
            ('EQUALS', '='),
            ('NUMBER', '8080'),
            ('SEMICOLON', ';'),
            ('RBRACE', '}')
        ]
        self.assertEqual(token_data, expected)

    def test_multiline_comments(self):
        input_text = """
        <#
        This is a comment
        with multiple lines
        #>
        MaxConnections := 100;
        """
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        token_data = [(t.type, t.value) for t in tokens]
        expected = [
            ('IDENTIFIER', 'MaxConnections'),
            ('COLON_EQUALS', ':='),
            ('NUMBER', '100'),
            ('SEMICOLON', ';')
        ]
        self.assertEqual(token_data, expected)

    def test_const_expression(self):
        input_text = '.[ PI * 2 + 10 ].'
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, 'START_EXPR')
        self.assertEqual(tokens[1].type, 'EXPR_CONTENT')
        self.assertEqual(tokens[1].value, 'PI * 2 + 10')
        self.assertEqual(tokens[2].type, 'END_EXPR')

    def test_strings(self):
        input_text = 'Message = "Hello \\"World\\"";'
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        self.assertEqual(tokens[2].type, 'STRING')
        # В лексере экранирование уже обработано
        self.assertEqual(tokens[2].value, 'Hello "World"')

    def test_numbers(self):
        input_text = 'Value1 = 42; Value2 = 3.14e-2;'
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        number_tokens = [t for t in tokens if t.type == 'NUMBER']
        self.assertEqual(number_tokens[0].value, '42')
        self.assertEqual(number_tokens[1].value, '3.14e-2')

    def test_errors(self):
        with self.assertRaises(SyntaxError):
            Lexer('<# unterminated comment').tokenize()

        with self.assertRaises(SyntaxError):
            Lexer('.[ unterminated expression').tokenize()

        with self.assertRaises(SyntaxError):
            Lexer('@').tokenize()


if __name__ == '__main__':
    unittest.main()