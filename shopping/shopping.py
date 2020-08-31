import csv
import sys
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    ITALIC = '\033[3m'


def main():
    # Checks if format of entry is correct
    if len(sys.argv) != 2:
        sys.exit("Incorrect format!!! Enter as follows -> python3 shopping.py data")

    # Data is loaded from spreadsheet and is split into their respective train and test sets
    evidence, labels = load_data(sys.argv[1])
    trainX, testX, trainY, testY = train_test_split(evidence, labels, test_size=TEST_SIZE)

    # Model is trained to make predictions
    model = train_model(trainX, trainY)
    prediction = model.predict(testX)
    print(prediction)
    sensitivity, specificity = evaluate(testY, prediction)

    # Results are outputted
    print(color.CYAN + color.UNDERLINE + color.BOLD + "\nResults for user’s purchasing intent:\t" + color.END + "\n")
    print(color.BLUE + f"Correct:\t\033[1;33m{(testY == prediction).sum()}\n" + color.END)
    print(color.BLUE + f"Incorrect:\t\033[1;33m{(testY != prediction).sum()}\n" + color.END)
    print(color.BLUE + f"True Positive Rate:\t\033[1;33m{100 * sensitivity:.2f}%\n" + color.END)
    print(color.BLUE + f"True Negative Rate:\t\033[1;33m{100 * specificity:.2f}%\n" + color.END)


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).
    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
op        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)
    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # Two lists are initiated
    evidence = list()
    labels = list()

    abbreviations = dict(Jan=0, Feb=1, Mar=2, Apr=3, May=4, June=5, Jul=6, Aug=7, Sep=8, Oct=9, Nov=10, Dec=11)

    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence.append([
                int(row["Administrative"]),
                float(row["Administrative_Duration"]),
                int(row["Informational"]),
                float(row["Informational_Duration"]),
                int(row["ProductRelated"]),
                float(row["ProductRelated_Duration"]),
                float(row["BounceRates"]),
                float(row["ExitRates"]),
                float(row["PageValues"]),
                float(row["SpecialDay"]),
                abbreviations[row["Month"]],
                int(row["OperatingSystems"]),
                int(row["Browser"]),
                int(row["Region"]),
                int(row["TrafficType"]),
                1 if row["VisitorType"] == "Returning_Visitor" else 0,
                1 if row["Weekend"] == "TRUE" else 0,
            ])
            labels.append(1 if row["Revenue"] == "TRUE" else 0)

    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, prediction):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).
    Assume each label is either a 1 (positive) or 0 (negative).
    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.
    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivity = float(0)
    specificity = float(0)

    positiveTotal = float(0)
    negativeTotal = float(0)

    for label, prediction in zip(labels, prediction):

        if label == 1:
            positiveTotal += 1
            if label == prediction:
                sensitivity += 1

        if label == 0:
            negativeTotal += 1
            if label == prediction:
                specificity += 1

    # Conduction of normalization
    sensitivity /= positiveTotal
    specificity /= negativeTotal

    return sensitivity, specificity


if __name__ == "__main__":
    main()
