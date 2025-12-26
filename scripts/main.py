import os
import sys

# Make sure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def main():
    print("\n" + "="*50)
    print("  MARKET RISK PROJECT 2025-2026")
    print("="*50 + "\n")

    print("Which question do you want to run?")
    print("  [A] Non-parametric VaR")
    print("  [B] Expected Shortfall")
    print("  [C] Extreme Value Theory")
    print("  [D] Bouchaud Model")
    print("  [E] Haar Wavelets & Hurst")
    print("  [T] Run all")
    print("  [Q] Quit\n")

    choice = input("Choice: ").strip().upper()

    if choice == 'Q':
        print("Goodbye!")
        return

    questions_to_run = []

    if choice == 'T':
        questions_to_run = ['A', 'B', 'C', 'D', 'E']
    elif choice in ['A', 'B', 'C', 'D', 'E']:
        questions_to_run = [choice]
    else:
        print("Invalid choice")
        return

    import math
    import csv

    for q in questions_to_run:
        print("\n" + "="*50)
        print(f"Question {q}")
        print("="*50)

        if q == 'A':
            exec(compile(open('question_a.py').read(), 'question_a.py', 'exec'), globals())
        elif q == 'B':
            exec(compile(open('question_b.py').read(), 'question_b.py', 'exec'), globals())
        elif q == 'C':
            exec(compile(open('question_c.py').read(), 'question_c.py', 'exec'), globals())
        elif q == 'D':
            exec(compile(open('question_d.py').read(), 'question_d.py', 'exec'), globals())
        elif q == 'E':
            exec(compile(open('question_e.py').read(), 'question_e.py', 'exec'), globals())

    print("\n" + "="*50)
    print("Done!")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
