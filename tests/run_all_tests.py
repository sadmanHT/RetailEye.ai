import subprocess
import sys
import re

def run_tests():
    test_files = [
        "tests/test_imports.py",
        "tests/test_modules.py",
        "tests/test_api.py"
    ]
    
    all_passed = True
    total_passed = total_failed = total_skipped = 0
    
    # Run pytest on all files in order and generate html report
    print("Executing tests and generating HTML report...")
    cmd = ["pytest", "-v"] + test_files + ["--html=tests/test_report.html", "--self-contained-html"]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout
    
    # We will print the output so the user sees it
    print(out)
    
    # Parse the final line for summary
    # Example: "==== 10 passed, 2 failed in 0.50s ===="
    lines = out.strip().split('\n')
    summary_line = lines[-1] if lines else ""
    
    if "failed" in summary_line.lower() or "error" in summary_line.lower():
        all_passed = False
        
    print("-" * 50)
    if all_passed:
        # Green text
        print(f"\033[92mSUCCESS: {summary_line}\033[0m")
    else:
        # Red text
        print(f"\033[91mFAILED: {summary_line}\033[0m")
        
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    run_tests()
