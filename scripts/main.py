print("\n" + "="*50)
print("  MARKET RISK PROJECT 2025-2026")
print("="*50 + "\n")

print("Which question do you want to run?")
print("  [A] Non-parametric VaR")
print("  [B] Expected Shortfall")
print("  [C] Extreme Value Theory")
print("  [D] Bouchaud Model")
print("  [E] Haar Wavelets & Hurst")
print("  [T] Run all questions")
print("  [Q] Quit\n")

choice = input("Choice: ").strip().upper()

if choice == 'Q':
    print("Goodbye!")
    exit()

questions_to_run = []

if choice == 'T':
    questions_to_run = ['A', 'B', 'C', 'D', 'E']
elif choice in ['A', 'B', 'C', 'D', 'E']:
    questions_to_run = [choice]
else:
    print("Invalid choice")
    exit()

for q in questions_to_run:
    if q in ['A', 'B']:
        filename = "question_a_b.py"
    else:
        filename = f"question_{q.lower()}.py"
    exec(open(filename).read())


