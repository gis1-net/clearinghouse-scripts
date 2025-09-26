import sys
import time

def main():
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <state> <county>")
        return 1  # Return a failure exit code
    
    state = sys.argv[1]
    county = sys.argv[2]
    
    print(f"This is state: {state}")
    print(f"This is county: {county}")
    
    time.sleep(2)  # Wait for 5 seconds
    
    return 0  # Return a success exit code


if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"Exit Code: {exit_code}")  # Print the exit code
        sys.exit(exit_code)  # Exit with the appropriate code
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Explicit failure exit code
