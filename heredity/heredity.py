import csv
import itertools
import sys

PROBS = {

    # Provided unconditional probabilities
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probabaility of trait with 2 genes
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait with 1 gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait with no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Probability if there is a chance of mutation
    "mutation": 0.01
}


def main():
    if len(sys.argv) != 2:
        sys.exit("Incorrect Format! Must add it in the following way ->  python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Track of genes and probabilities
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Goes over traits
    names = set(people)
    for have_trait in powerset(names):

        # Violation check
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Goes over people who might have genes
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Probabilty update
                probs = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, probs)

    # Probabilities must sum to 1!!!
    normalize(probabilities)

    # Results are displayed here
    for person in people:
        print(f"{person}:")
        for area in probabilities[person]:
            print(f"  {area.capitalize()}:")
            for value in probabilities[person][area]:
                probs = probabilities[person][area][value]
                print(f"    {value}: {probs:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    # Read CSV file
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else False if row["trait"] == "0" else None)
            }
    return data


def powerset(setx):
    """
    Return a list of all possible subsets of set s.
    """
    setx = list(setx)
    return [
        set(setx) for setx in
        itertools.chain.from_iterable(itertools.combinations(setx, x) for x in range(len(setx) + 1))
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Calculation of probability from statistics and data set provided
    no_gene = set()
    probability = 1

    # If they have no genes
    for person in people:
        if person not in one_gene and person not in two_genes:
            no_gene.add(person)
    for person in no_gene:
        if people[person]["mother"] == None:
            chance = PROBS["gene"][0]
        else:
            chance = 1
            mother = people[person]["mother"]
            father = people[person]["father"]
            one_minus = 1 - PROBS["mutation"]
            mutation = PROBS["mutation"]
            if mother in no_gene and father in no_gene:
                chance *= one_minus ** 2
            elif mother in no_gene and father in one_gene:
                chance *= one_minus * 0.5
            elif mother in no_gene and father in two_genes:
                chance *= one_minus * mutation
            elif mother in one_gene and father in no_gene:
                chance *= 0.5 * one_minus
            elif mother in one_gene and father in one_gene:
                chance *= 0.5 ** 2
            elif mother in one_gene and father in two_genes:
                chance *= 0.5 * mutation
            elif mother in two_genes and father in no_gene:
                chance *= mutation * one_minus
            elif mother in two_genes and father in one_gene:
                chance *= mutation * 0.5
            elif mother in two_genes and father in two_genes:
                chance *= mutation ** 2
        if person in have_trait:
            chance *= PROBS["trait"][0][True]
        else:
            chance *= PROBS["trait"][0][False]

        probability *= chance
    # If they have one gene
    for person in one_gene:
        if people[person]["mother"] == None:
            chance = PROBS["gene"][1]
        else:
            chance = 1
            mother = people[person]["mother"]
            father = people[person]["father"]
            one_minus = 1 - PROBS["mutation"]
            mutation = PROBS["mutation"]
            if mother in no_gene and father in no_gene:
                chance *= 2 * (mutation * one_minus)
            elif mother in no_gene and father in one_gene:
                chance *= 0.5
            elif mother in no_gene and father in two_genes:
                chance *= mutation ** 2 + one_minus ** 2
            elif mother in one_gene and father in no_gene:
                chance *= 0.5
            elif mother in one_gene and father in one_gene:
                chance *= 0.5
            elif mother in one_gene and father in two_genes:
                chance *= 0.5
            elif mother in two_genes and father in no_gene:
                chance *= mutation ** 2 + one_minus ** 2
            elif mother in two_genes and father in one_gene:
                chance *= 0.5
            elif mother in two_genes and father in two_genes:
                chance *= 2 * (mutation * one_minus)
        if person in have_trait:
            chance *= PROBS["trait"][1][True]
        else:
            chance *= PROBS["trait"][1][False]
        probability *= chance

    # If they have two genes
    for person in two_genes:
        if people[person]["mother"] == None:
            chance = PROBS["gene"][2]
        else:
            chance = 1
            mother = people[person]["mother"]
            father = people[person]["father"]
            one_minus = 1 - PROBS["mutation"]
            mutation = PROBS["mutation"]
            if mother in no_gene and father in no_gene:
                chance *= mutation ** 2
            elif mother in no_gene and father in one_gene:
                chance *= mutation * 0.5
            elif mother in no_gene and father in two_genes:
                chance *= one_minus * mutation
            elif mother in one_gene and father in no_gene:
                chance *= 0.5 * mutation
            elif mother in one_gene and father in one_gene:
                chance *= 0.5 ** 2
            elif mother in one_gene and father in two_genes:
                chance *= 0.5 * one_minus
            elif mother in two_genes and father in no_gene:
                chance *= mutation * one_minus
            elif mother in two_genes and father in one_gene:
                chance *= one_minus * 0.5
            elif mother in two_genes and father in two_genes:
                chance *= one_minus ** 2

        # If they have traits predefined
        if person in have_trait:
            chance *= PROBS["trait"][2][True]
        else:
            chance *= PROBS["trait"][2][False]
        probability *= chance

    return probability


def update(probabilities, one_gene, two_genes, have_trait, probs):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for n in probabilities:
        if n not in one_gene and n not in two_genes:
            gene = 0
        elif n in one_gene:
            gene = 1
        else:
            gene = 2
        probabilities[n]["gene"][gene] += probs
        if n in have_trait:
            probabilities[n]["trait"][True] += probs
        else:
            probabilities[n]["trait"][False] += probs


def normalize(probabilities):
    # Checks if it sums to 1
    for n in probabilities:
        gene = sum(probabilities[n]["gene"].values())
        for genex in probabilities[n]["gene"]:
            probabilities[n]["gene"][genex] /= gene
        trait = sum(probabilities[n]["trait"].values())
        for traitx in probabilities[n]["trait"]:
            probabilities[n]["trait"][traitx] /= trait


if __name__ == "__main__":
    main()