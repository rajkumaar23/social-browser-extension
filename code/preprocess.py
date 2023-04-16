import csv, sys, pickle

dataset_filename = "NELL.08m.1115.esv.csv"
pickle_filename = "dataset.pickle"

# Preprocess the dataset
dataset = set()
csv.field_size_limit(sys.maxsize)
with open(dataset_filename, "r") as f:
    reader = csv.reader(f, delimiter=",")
    i = 1
    for row in reader:
        print("Count " + str(i))
        dataset.add(row[0].lower())
        i += 1

# Save the preprocessed dataset to a pickle file
with open(pickle_filename, "wb") as f:
    pickle.dump(dataset, f)
