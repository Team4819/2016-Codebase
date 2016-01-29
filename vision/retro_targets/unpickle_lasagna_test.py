from lasagna_test1 import plot_data, load_data

import pickle
net = pickle.load(open('mlp.pickle', 'rb'))

X, y = load_data("training_data/test_pics", 20)
plot_data(net, X, y)
