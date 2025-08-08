from functions.get_files_info import get_file_content

def test():
    print("Case 1: calculator/main.py")
    res = get_file_content("calculator", "main.py")
    print(res)  # print the contents so stdout includes "def main():"

    print("\nCase 2: calculator/pkg/calculator.py")
    res = get_file_content("calculator", "pkg/calculator.py")
    print(res)  # print the contents so stdout includes "def _apply_operator(self, operators, values)"

    print("\nCase 3: absolute /bin/cat — should error")
    res = get_file_content("calculator", "/bin/cat")
    print(res)  # should start with "Error:"

    print("\nCase 4: calculator/pkg/does_not_exist.py — should error")
    res = get_file_content("calculator", "pkg/does_not_exist.py")
    print(res)  # should start with "Error:"

if __name__ == "__main__":
    test()

