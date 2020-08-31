import sys
from PIL import Image, ImageDraw, ImageFont
from termcolor import cprint

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            variable: self.crossword.words.copy()
            for variable in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [[None for _ in range(self.crossword.width)] for _ in range(self.crossword.height)]
        for var, word in assignment.items():
            dir = var.direction
            for n in range(len(word)):
                x = var.i + (n if dir == Variable.DOWN else 0)
                y = var.j + (n if dir == Variable.ACROSS else 0)
                letters[x][y] = word[n]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        cprint("Grid to be filled ", "red", end="")
        print()
        for x in range(self.crossword.height):
            for y in range(self.crossword.width):
                if self.crossword.structure[x][y]:
                    cprint("█ ", "white", end="")
                else:
                    cprint("█ ", "blue", end="")
            print()
        cprint("Filled Grid with words ", "red", end="")
        print()
        letters = self.letter_grid(assignment)
        for x in range(self.crossword.height):
            for y in range(self.crossword.width):
                if self.crossword.structure[x][y]:
                    print(letters[x][y] or " ", end=" ")
                else:
                    cprint("█ ", "blue", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        size = 100
        border = 2
        interior = size - 2 * border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * size,
             self.crossword.height * size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for x in range(self.crossword.height):
            for y in range(self.crossword.width):

                rect = [
                    (y * size + border,
                     x * size + border),
                    ((y + 1) * size - border,
                     (x + 1) * size - border)
                ]
                if self.crossword.structure[x][y]:
                    draw.rectangle(rect, fill="white")
                    if letters[x][y]:
                        w, h = draw.textsize(letters[x][y], font=font)
                        draw.text(
                            (rect[0][0] + ((interior - w) / 2),
                             rect[0][1] + ((interior - h) / 2) - 10),
                            letters[x][y], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        a, b = self.crossword.overlaps[x, y]

        for word1 in set(self.domains[x]):
            remove = True

            for word2 in self.domains[y]:
                if word1[a] == word2[b]:
                    remove = False

            if remove:
                self.domains[x].remove(word1)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = list()
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))

        while arcs:
            x, y = arcs.pop()

            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - self.domains[y]:
                    arcs.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return not bool(self.crossword.variables - set(assignment))

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = set()

        for var in assignment:

            # Different word to be used so added to a set that keeps track of used words
            if assignment[var] not in used_words:
                used_words.add(assignment[var])
            else:
                return False

            # Variables have to be correct length to fit in crossword
            if len(assignment[var]) != var.length:
                return False

            # No conflict between neighbours
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    x, y = self.crossword.overlaps[var, neighbor]
                    if assignment[var][x] != assignment[neighbor][y]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        x = dict()

        for val in self.domains[var]:
            x[val] = 0
            for neighbor in self.crossword.neighbors(var) - assignment:
                if val in self.domains[neighbor]:
                    x[val] += 1

        return sorted(x, key=x.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        sol = None

        for n in self.crossword.variables - set(assignment):
            if (
                    sol is None or len(self.domains[n]) < len(self.domains[sol]) or
                    len(self.crossword.neighbors(n)) > len(self.crossword.neighbors(sol))
            ):
                sol = n

        return sol

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for val in self.domains[var]:
            assignment[var] = val

            if self.consistent(assignment):
                res = self.backtrack(assignment)
                if res is not None:
                    return res

            assignment.pop(var)

        return None


def main():
    # Checks if the command has been entered correctly.
    if len(sys.argv) not in [3, 4]:
        sys.exit("Incorrect command!!! Must enter in following format -> python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] \
        if len(sys.argv) == 4 else None

    # Crossword is generated
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Result gets printed
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
