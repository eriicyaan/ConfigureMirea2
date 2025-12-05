import unittest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.main import main as cli_main


class TestIntegration(unittest.TestCase):
    EXAMPLES_DIR = Path(__file__).parent / 'examples'

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def run_converter(self, input_path, output_path):
        with patch('sys.argv', ['config', '-i', str(input_path), '-o', str(output_path)]):
            cli_main()

    def test_character_config(self):
        input_file = self.EXAMPLES_DIR / 'character.conf'
        output_file = self.temp_dir / 'character.json'

        self.run_converter(input_file, output_file)

        with open(output_file, encoding='utf-8') as f:
            result = json.load(f)

        # Проверка основных полей
        self.assertEqual(result['Name'], "Элиандра")
        self.assertEqual(result['Class'], "Mage")
        self.assertEqual(result['Title'], "Хранительница Звёзд")
        self.assertEqual(result['Level'], 15.0)

        # Проверка вложенных структур
        self.assertEqual(result['Stats']['Intelligence'], 20.0)
        self.assertEqual(result['Stats']['Mana'], 200.0)  # 20 * 10

        # Проверка заклинаний
        heal = result['Spells']['Heal']
        self.assertEqual(heal['Name'], "Божественное исцеление")
        self.assertIn('150%', heal['Description'])
        self.assertEqual(heal['ManaCost'], 30.0)

        # Проверка диалога - в JSON \n преобразуется в реальный перенос
        self.assertIn("Сила — в знании", result['Dialogue'])
        self.assertIn('\n', result['Dialogue'])  # Реальный перенос строки

        os.unlink(output_file)

    def test_physics_config(self):
        input_file = self.EXAMPLES_DIR / 'physics.conf'
        output_file = self.temp_dir / 'physics.json'

        self.run_converter(input_file, output_file)

        with open(output_file, encoding='utf-8') as f:
            result = json.load(f)

        # Проверка констант
        self.assertEqual(result['Universe'], "Наблюдаемая Вселенная")
        constants = result['Constants']
        self.assertAlmostEqual(constants['GravitationalConstant'], 6.67430e-11, places=15)
        self.assertEqual(constants['SpeedOfLight'], 299792458.0)

        # Проверка вычислений
        math = result['Math']
        self.assertAlmostEqual(math['PiValue'], 3.1415926535, places=10)
        self.assertAlmostEqual(math['Sqrt2'], 1.4142135623730951, places=10)
        self.assertAlmostEqual(math['Euler'], 2.7182818284, places=10)

        # Проверка Unicode и реальных переносов
        self.assertIn("E = mc²", result['Citation'])
        self.assertIn('\n', result['Citation'])  # Реальный перенос строки
        self.assertIn('1905', result['Citation'])

        os.unlink(output_file)

    def test_server_config(self):
        input_file = self.EXAMPLES_DIR / 'server.conf'
        output_file = self.temp_dir / 'server.json'

        self.run_converter(input_file, output_file)

        with open(output_file, encoding='utf-8') as f:
            result = json.load(f)

        # Проверка вычислений
        self.assertEqual(result['Port'], 8080.0)  # 8000 + 80

        # Проверка хоста
        self.assertEqual(result['Host'], "0.0.0.0")
        self.assertEqual(result['Environment'], "production")

        # Проверка строк с экранированием
        messages = result['Messages']
        self.assertEqual(messages['Welcome'], "Добро пожаловать на сервер!")
        # В JSON экранирование обрабатывается правильно
        self.assertEqual(messages['Error'], "Ошибка: \\\"server down\\\"")

        # Проверка вложенных структур
        self.assertEqual(result['SSL']['CertPath'], "/etc/ssl/cert.pem")

        os.unlink(output_file)

    def tearDown(self):
        for file in self.temp_dir.glob('*'):
            try:
                file.unlink()
            except:
                pass
        try:
            self.temp_dir.rmdir()
        except:
            pass


if __name__ == '__main__':
    unittest.main(verbosity=2)