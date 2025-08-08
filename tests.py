from functions.run_python import run_python_file

def test():
    print(run_python_file("calculator", "main.py"))
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print(run_python_file("calculator", "tests.py"))
    print(run_python_file("calculator", "../main.py"))      # should error (outside)
    print(run_python_file("calculator", "nonexistent.py"))  # should error (missing)

if __name__ == "__main__":
    test()


