import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Initialisation of height, width mine numbers
        self.height = height
        self.width = width
        self.mines = set()

        # Firstly, player had found no mines
        self.mines_found = set()

        # There is an empty field with no mines created
        self.board = []
        for x in range(self.height):
            row = []
            for y in range(self.width):
                row.append(False)
            self.board.append(row)

        # Using randrange mines are added randomly on the borad
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                # print((i, j))
                self.mines.add((i, j))
                self.board[i][j] = True

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for x in range(self.height):
            print("--" * self.width + "-")
            for y in range(self.width):
                if self.board[x][y]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")
    # Text base is created to locate each and every mine
    def is_mine(self, cell):
        x, y = cell
        return self.board[x][y]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Nearby mines count is tracked
        counter = 0

        # All cells are looped over
        for x in range(cell[0] - 1, cell[0] + 2):
            for y in range(cell[1] - 1, cell[1] + 2):

                # The cell gets ignored
                if (x, y) == cell:
                    continue

                # The counter is updated if mine is found
                if 0 <= x < self.height and 0 <= y < self.width:
                    if self.board[x][y]:
                        counter += 1

        return counter

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count): # Initialisation using a constructor method
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safes = set()

    def __eq__(self, other): # Methods are defined here
        return self.cells == other.cells and self.count == other.count

    def __hash__(self):
        return hash((tuple(self.cells), self.count))

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.safes.add(cell)
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Initial width and height are initialised
        self.height = height
        self.width = width

        # Track of cells clicked on are tracked
        self.moves_made = set()

        # Safe cells or mines are kept track of
        self.mines = set()
        self.safes = set()

        # Sentences of truth are stored in this set
        self.knowledge = set()

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        self.moves_made.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        self.moves_made.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.safes.add(cell)
        self.moves_made.add(cell)
        cells = []
        for x in range(cell[0] - 1, cell[0] + 2):
            for y in range(cell[1] - 1, cell[1] + 2):
                if 0 <= x < self.height and 0 <= y < self.width:
                    new_instance = (x, y)
                    if (new_instance != cell):
                        cells.append(new_instance)
        self.knowledge.add(Sentence(cells, count))
        # adds the safe cell to the data structure
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
        """ 
        infer from one sentence count equalling the length of that 
        sentences count that all of the cells are mines and then apply 
        that knowledge to all sentences
        """
        for sentence in self.knowledge:
            if (sentence.count == len(sentence.cells)):
                for cell in sentence.cells:
                    self.mines.add(cell)

        for mine in self.mines:
            for sentence in self.knowledge:
                sentence.mark_mine(mine)
        """
        infer from one sentence count being zero but there being cells
        that all those cells are safe and then propigate that knowledge
        to current sentence and that particular cell knowledge to the
        rest of the sentences
        """
        for sentence in self.knowledge:
            if (sentence.count == 0 and len(sentence.cells) != 0):
                for cell in sentence.cells:
                    self.safes.add(cell)

        for safe_cell in self.safes:
            for sentence in self.knowledge:
                sentence.mark_safe(safe_cell)

        """
        Add the difference between two complete subsets to knowledge
        """
        sentences = []
        for first in self.knowledge:
            for second in self.knowledge:
                if (first != second and first.cells.issubset(second.cells)):
                    count_new = second.count - first.count
                    new_set = second.cells.difference(first.cells)
                    sentences.append(Sentence(new_set, count_new))
        [self.knowledge.add(sentence) for sentence in sentences]

        for sentence in self.knowledge:
             print(sentence.cells, sentence.count)
        print(f"safes: {self.safes}")
        print(f"moves_made: {self.moves_made}")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        difference = self.safes.difference(self.moves_made)
        return None if not difference else random.choice(tuple(difference))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        move_availability = set()
        moves = self.moves_made.union(self.mines)
        for x in range(self.height):
            for y in range(self.width):
                sets = (x, y)
                if (sets not in moves):
                    move_availability.add(sets)

        return None if move_availability == set() else random.choice(tuple(move_availability))