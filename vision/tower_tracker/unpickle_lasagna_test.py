from lasagna_tracker import plot_data, load_data

import pickle
net = pickle.load(open('mlp.pickle', 'rb'))

X, y = load_data(["dataset/set_0"], 10, 20)
plot_data(net, X, y)
