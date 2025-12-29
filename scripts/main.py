print("\n  MARKET RISK PROJECT 2025-2026\n")
print("Which question do you want to run?\n")
print("[A] Non-parametric VaR")
print("[B] Expected Shortfall")
print("[C] Extreme Value Theory")
print("[D] Bouchaud Model")
print("[E] Haar Wavelets & Hurst")
print("[T] Run all questions")
print("[Q] Quit\n")

choice = input("Choice: ").upper()

if choice == 'Q':
    exit()

if choice == 'T':
    questions = ['A', 'B', 'C', 'D', 'E']
elif choice in ['A', 'B', 'C', 'D', 'E']:
    questions = [choice]
else:
    print("Invalid choice")
    exit()

done = set()
for q in questions:
    if q in ['A', 'B']:
        file = "question_a_b.py"
    else:
        file = f"question_{q.lower()}.py"

    if file not in done:
        exec(open(file).read())
        done.add(file)


