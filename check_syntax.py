import ast
import os

def check_syntax(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return None
    except SyntaxError as e:
        return f"{file_path}: {e}"
    except Exception as e:
        return f"{file_path}: {e}"

def main():
    app_dir = "app"
    for root, _, files in os.walk(app_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                error = check_syntax(file_path)
                if error:
                    print(error)

if __name__ == "__main__":
    main()
