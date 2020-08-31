from logic import *
"""

The commas in this project act as 'AND' conjunctions and is converted to conjunctive normal form
 
"""
AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
"""
uses the propositional conjunctions and is done in conjunctive normal form

"""

knowledge0 = And(
    # uses implications, or ; and ; not
    Implication(And(AKnight, AKnave), AKnight),
    Implication(Not(And(AKnight, AKnave)), AKnave),

    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    Not(And(Not(AKnight), Not(AKnave)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Implication(Not(And(AKnave, BKnave)), AKnave),
    Implication(And(AKnave, BKnave), AKnight),
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(Not(BKnight), Not(BKnave))),
    Not(And(Not(AKnight), Not(AKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(Not(AKnight), Not(AKnave))),
    Not(And(Not(BKnight), Not(BKnave))),
    Implication(And(AKnight, BKnight), AKnight),
    Implication(And(AKnave, BKnave), AKnight),
    Implication(And(AKnight, BKnave), AKnave),
    Implication(And(AKnave, BKnight), AKnave),
    Implication(And(AKnight, BKnight), BKnave),
    Implication(And(AKnave, BKnave), BKnave),
    Implication(And(AKnight, BKnave), BKnight),
    Implication(And(AKnave, BKnight), BKnight)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(CKnight, CKnave)),
    Not(And(Not(AKnight), Not(AKnave))),
    Not(And(Not(BKnight), Not(BKnave))),
    Not(And(Not(CKnight), Not(CKnave))),
    Implication(AKnight, CKnight),
    Implication(AKnave, CKnave),
    Implication(CKnave, BKnight),
    Implication(CKnight, BKnave),
    Biconditional(BKnight, Biconditional(AKnight, AKnave))
)
"""
Each of the symbols and propositional logic are on separate lines.

"""

def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()