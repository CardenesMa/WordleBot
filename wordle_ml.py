#! This is an unfinished file. Categotical data is not working out here

#ML package
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import CategoricalNB
import pandas as pd
# choosing the model : https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html
# First attempt: Linear SVC
#Docs: https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html#sklearn.naive_bayes.GaussianNB


# first, load up the data
data = pd.read_csv("wordle_data.csv")

train, test = train_test_split(data, test_size = 0.1, random_state=42)

x_train = train.drop(['Correct Word'], axis = 1, inplace= False)
y_train = train.drop(['Word 1', 'Word 2', 'Word 3', 'Word 4', 'Word 5', 'Word 6'], axis = 1, inplace= False)


# predict a word

# show the confidence of that word 
