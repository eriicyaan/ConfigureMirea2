import sys
import json
import argparse
from pathlib import Path
from config.lexer import Lexer
from config.parser import Parser
from config.evaluator import Evaluator


def main():
    parser = argparse.ArgumentParser(description='Config language to JSON converter')
    parser.add_argument('-i', '--input', required=True, help='Input configuration file path')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file path')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        sys.stderr.write(f"Error: Input file '{args.input}' does not exist\n")
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except Exception as e:
        sys.stderr.write(f"Error reading input file: {str(e)}\n")
        sys.exit(1)

    try:
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        evaluator = Evaluator()
        json_data = evaluator.evaluate(ast)
    except SyntaxError as e:
        sys.stderr.write(f"Syntax error: {str(e)}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Processing error: {str(e)}\n")
        sys.exit(1)

    try:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully converted '{args.input}' to '{args.output}'")
    except Exception as e:
        sys.stderr.write(f"Error writing output file: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()