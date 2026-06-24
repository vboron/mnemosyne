import subprocess


def run(command):
    subprocess.run(command, shell=True, check=False)


def main():
    while True:
        print()
        print("Mnemosyne")
        print("1. List discs")
        print("2. List albums")
        print("3. List memories")
        print("4. Revisit random memory")
        print("5. Preserve memory")
        print("6. Year in review")
        print("7. Exit")

        choice = input("> ").strip()

        if choice == "1":
            run("python3 mnemo.py list-discs")
        elif choice == "2":
            run("python3 mnemo.py list-albums")
        elif choice == "3":
            run("python3 mnemo.py list-memories")
        elif choice == "4":
            run("python3 mnemo.py revisit-random")
        elif choice == "5":
            run("python3 mnemo.py preserve")
        elif choice == "6":
            year = input("Year: ").strip()
            run(f"python3 mnemo.py year-in-review {year}")
        elif choice == "7":
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()