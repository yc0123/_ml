# https://www.kaggle.com/datasets/shantanugarg274/heart-prediction-dataset-quantum

import ml
from sklearn.ensemble import RandomForestClassifier

def learn_classifier(x_train, y_train):
    model = RandomForestClassifier(n_estimators=25)
    model.fit(x_train, y_train)
    return model

x_train,x_test,y_train,y_test=ml.load_csv("Heart Prediction Quantum Dataset.csv", "HeartDisease")

classifier=learn_classifier(x_train,y_train)

print('=========== train report ==========')
ml.report(classifier, x_train, y_train)

print('=========== test report ==========')
ml.report(classifier, x_test, y_test)