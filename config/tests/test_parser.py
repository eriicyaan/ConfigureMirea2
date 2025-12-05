import unittest
from config.lexer import Lexer
from config.parser import Parser
from config.ast import *


class TestParser(unittest.TestCase):
    def test_const_declaration(self):
        # Добавляем корневую структуру для валидного синтаксиса
        input_text = 'MAX_THREADS := 10; struct {}'
        tokens = Lexer(input_text).tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        self.assertEqual(len(ast['consts']), 1)
        decl = ast['consts'][0]
        self.assertIsInstance(decl, ConstDeclaration)
        self.assertEqual(decl.name, 'MAX_THREADS')
        self.assertIsInstance(decl.value_node, Number)
        self.assertEqual(decl.value_node.value, 10.0)

    def test_nested_struct(self):
        # Исправляем true на число, так как в ТЗ нет boolean
        input_text = """
        struct {
            Server = struct {
                Port = 8080;
                SSL = struct {
                    Enabled = 1;
                };
            };
        }
        """
        tokens = Lexer(input_text).tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        root = ast['root']
        self.assertIsInstance(root, Struct)
        self.assertIn('Server', root.fields)

        server = root.fields['Server']
        self.assertIsInstance(server, Struct)
        self.assertIn('Port', server.fields)
        self.assertIn('SSL', server.fields)

        ssl = server.fields['SSL']
        self.assertIsInstance(ssl, Struct)
        self.assertIn('Enabled', ssl.fields)
        self.assertEqual(ssl.fields['Enabled'].value, 1.0)

    def test_const_expression_in_struct(self):
        input_text = """
        PI := 3.14;
        struct {
            CircleArea = .[ PI * 5 * 5 ].;
        }
        """
        tokens = Lexer(input_text).tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        expr = ast['root'].fields['CircleArea']
        self.assertIsInstance(expr, ConstExpression)
        self.assertEqual(expr.tokens, ['PI', '*', '5', '*', '5'])

    def test_real_world_examples(self):
        # Тест на реальный пример из character.conf
        input_text = """
        BaseInt := 20;
        struct {
            Stats = struct {
                Intelligence = BaseInt;
                Mana = .[BaseInt 10 *].;
            };
        }
        """
        tokens = Lexer(input_text).tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Проверяем константы
        self.assertEqual(len(ast['consts']), 1)
        self.assertEqual(ast['consts'][0].name, 'BaseInt')

        # Проверяем структуру
        root = ast['root']
        self.assertIn('Stats', root.fields)
        stats = root.fields['Stats']
        self.assertIn('Intelligence', stats.fields)
        self.assertIn('Mana', stats.fields)

        # Проверяем выражение
        mana_expr = stats.fields['Mana']
        self.assertIsInstance(mana_expr, ConstExpression)
        self.assertEqual(mana_expr.tokens, ['BaseInt', '10', '*'])

    def test_syntax_errors(self):
        # Невалидный синтаксис: отсутствует корневая структура
        with self.assertRaises(SyntaxError):
            Parser(Lexer('MAX := 10').tokenize()).parse()

        # Невалидный синтаксис: незакрытая структура
        with self.assertRaises(SyntaxError):
            Parser(Lexer('struct { field = 42').tokenize()).parse()


if __name__ == '__main__':
    unittest.main()