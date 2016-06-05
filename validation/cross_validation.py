# from time import time
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import fbeta_score
from sklearn.metrics import classification_report


def data_split(inputs, outputs, split_count):
    input_splits = [[] for _ in range(split_count)]
    output_splits = [[] for _ in range(split_count)]

    index = 0
    for input_, output_ in zip(inputs, outputs):
        if output_ == 1:
            for input_list, output_list in zip(input_splits, output_splits):
                input_list.append(input_)
                output_list.append(output_)
        else:
            input_splits[index].append(input_)
            output_splits[index].append(output_)
            index = (index + 1) % split_count

    return input_splits, output_splits


def get_best_classifier(classifiers, inputs, outputs, scorer):
    best_score = 0
    best_classifier = None
    for classifier in classifiers:
        score = scorer(classifier, inputs, outputs)
        if score > best_score or best_classifier is None:
            best_score = score
            best_classifier = classifier
        print("Fbeta score:", score)
    print()

    return best_classifier


def cross_validate(inputs, outputs, model_constructor, parameters, scorer, train_perc=0.7,
                   negative_splits=[16, 8, 4, 2, 1], folds=5, n_jobs=1, run_all_splits=False):
    test_size = 1.0 - train_perc
    train_in, test_in, train_out, test_out = train_test_split(inputs, outputs, test_size=test_size, stratify=outputs)

    classifiers = []
    for splits_count in negative_splits:
        print("Computing for part size: 1/" + str(splits_count) + "...")
        # split_classifiers = []

        splits_in, splits_out = data_split(train_in, train_out, splits_count)
        for split_in, split_out in zip(splits_in, splits_out):
            clf = GridSearchCV(model_constructor(), parameters, cv=folds, scoring=scorer, n_jobs=n_jobs, refit=True)
            clf.fit(split_in, split_out)
            classifiers.append(clf)

            print("\tBest score:", clf.best_score_)
            print("\tBest params:", clf.best_params_)
            if not run_all_splits:
                break

        # best_split_classifier = get_best_classifier(split_classifiers, train_in, train_out, scoring)
        # classifiers.append(best_split_classifier)
        # print("break2")
        # break

    best_classifier = get_best_classifier(classifiers, test_in, test_out, scorer)
    prediction_out = best_classifier.predict(test_in)
    print(classification_report(test_out, prediction_out))
    print(best_classifier.best_params_)
    return best_classifier
