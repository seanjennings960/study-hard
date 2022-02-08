import  sys

def main():
    """Add two numbers."""
    a, b = [int(i) for i in input().split(' ')]
    print(a + b)


if __name__ == '__main__':
    main()
