import bisect
import collections
import re
import os
import random
import sys
import numpy
from termcolor import cprint

cprint("PAGERANK ALGORITHM", 'yellow')
DAMPING = 0.85
SAMPLES = 10000
EPSILON = 0.001

def main():
    if len(sys.argv) != 2:
        sys.exit("Incorrect corpus entry or format. Should enter it as: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    cprint(f"PageRank results from Sampling (n = {SAMPLES})","blue")
    for page in sorted(ranks):
        cprint(f"  {page}: {ranks[page]:.4f}","red")
    ranks = iterate_pagerank(corpus, DAMPING)
    cprint(f"PageRank results from Iteration","blue")
    for page in sorted(ranks):
        cprint(f"  {page}: {ranks[page]:.4f}","green")


def crawl(current_directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for name in os.listdir(current_directory):
        if not name.endswith(".html"):
            continue
        with open(os.path.join(current_directory, name)) as f:
            content = f.read()
            all_links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", content)
            pages[name] = set(all_links) - {name}

    # Only include links to other pages in the corpus
    for name in pages:
        pages[name] = set(
            link for link in pages[name]
            if link in pages
        )

    return pages

def normalize(output):
    summation_values = sum(output.values())
    return {x:(y/summation_values) for (x,y) in output.items()}

def transition_model(corpus, page, factors):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    With probability `factors`, choose a link at random
    linked to by `page`. With probability `1 - factors`, choose
    a link at random chosen from all pages in the corpus.
    """
    all_pages = list(corpus.keys())
    dlink = corpus[page]
    if (dlink == {}):
        return dict(zip(all_pages, numpy.ones(len(all_pages), dtype=numpy.float)/len(all_pages)))
    dweights = factors * numpy.ones(len(dlink), dtype=numpy.float)/len(dlink)
    output = dict(zip(dlink,dweights))
    others = set(all_pages) - set(dlink)
    for page in others:
        output[page] = 0.0
    addition = (1-factors)/len(all_pages)
    output = {x:y+addition for (x,y) in output.items()}
    return normalize(output)


def cdf(weights):
    bank = sum(weights)
    list_results = []
    cumulativesum = 0
    for n in weights:
        cumulativesum += n
        list_results.append(cumulativesum / bank)
    return list_results

def choose(population, weights):
    cdf_of_values = cdf(weights)
    y = random.random()
    index = bisect.bisect(cdf_of_values, y)
    return population[index]

def sample_pagerank(corpus, factors, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys = list(corpus.keys())
    page = random.choice(keys)
    counts = collections.defaultdict(int)
    for z in range(n):
        model = transition_model(corpus, page, factors)
        page = choose(list(model.keys()), list(model.values()))
        counts[page] += 1
    return {x:float(a)/n for (x,a) in counts.items()}

def is_converged(previous_pr, next_pr):
    return all([(abs(next_pr[x] - y) <= EPSILON) for (x,y) in sorted(previous_pr.items())])

def iterate_pagerank(corpus, factors):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys = list(corpus.keys())
    previous_pagerank = dict(zip(keys, numpy.ones(len(keys), dtype=numpy.float)/len(keys)))
    reversal = {k: set() for k in keys}
    random = (1-factors)/len(keys)
    for x,y in corpus.items():
        for page in y:
            reversal[page].add(x)
    while True:
        next_pagerank = {}
        for x,v in previous_pagerank.items():
            current = 0.0
            for page in reversal[x]:
                current += previous_pagerank[page]/len(corpus[page])
            next_pagerank[x] = random + factors * current
        next_pagerank = normalize(next_pagerank)
        if (is_converged(previous_pagerank, next_pagerank)):
            break
        previous_pagerank = next_pagerank
    return previous_pagerank


if __name__ == "__main__":
    main()