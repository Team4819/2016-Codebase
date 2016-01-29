from lasagne import layers
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
import numpy as np
import os
from os.path import join
import cv2
from matplotlib import pyplot
from filter_test import find_goals

def build_cnn_net():
    return NeuralNet(
        layers=[
            ('input', layers.InputLayer),
            ('conv1', layers.Conv2DLayer),
            ('pool1', layers.MaxPool2DLayer),
            ('conv2', layers.Conv2DLayer),
            ('pool2', layers.MaxPool2DLayer),
            ('conv3', layers.Conv2DLayer),
            ('pool3', layers.MaxPool2DLayer),
            ('hidden4', layers.DenseLayer),
            ('hidden5', layers.DenseLayer),
            ('output', layers.DenseLayer),
            ],
        input_shape=(None, 3, 160, 120),
        conv1_num_filters=32, conv1_filter_size=(12, 12), pool1_pool_size=(2, 2),
        conv2_num_filters=64, conv2_filter_size=(6, 6), pool2_pool_size=(2, 2),
        conv3_num_filters=128, conv3_filter_size=(6, 6), pool3_pool_size=(2, 2),
        hidden4_num_units=500, hidden5_num_units=500,

        output_nonlinearity=None,
        output_num_units=2,

        update=nesterov_momentum,
        update_learning_rate=0.01,
        update_momentum=0.9,

        regression=True,
        max_epochs=1000,
        verbose=1
    )


def build_mlp_net():
    return NeuralNet(
        layers=[
            ('input', layers.InputLayer),
            ('hidden1', layers.DenseLayer),
            ('hidden2', layers.DenseLayer),
            ('output', layers.DenseLayer),
            ],
        input_shape=(None, 3, 160, 120),
        hidden1_num_units=100,
        hidden2_num_units=100,

        output_nonlinearity=None,
        output_num_units=2,

        update=nesterov_momentum,
        update_learning_rate=0.01,
        update_momentum=0.9,

        regression=True,
        max_epochs=200,
        verbose=1
    )


def load_data(path, max_count=-1):
    X = []
    y = []
    for file in os.listdir(path):
        if len(X) == max_count:
            break
        if file.endswith(".jpg"):
            fname = join(path, file)
            img = cv2.cvtColor(cv2.imread(fname), cv2.COLOR_BGR2RGB)
            gx, gy, _ = find_goals(img)[0]
            size = img.shape
            y.append(np.array([gx/size[0], gy/size[1]]))
            img = cv2.resize(img, (160, 120))
            X.append(img.transpose(2, 1, 0)/255)

    X = np.array(X)
    y = np.array(y)
    return X, y


def plot_data(net, X, y=None):
    y_pred = net.predict(X)

    fig = pyplot.figure(figsize=(6, 6))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)
    for i in range(8):
        ax = fig.add_subplot(4, 4, i + 1, xticks=[], yticks=[])
        img = X[i].transpose(2, 1, 0)
        ax.imshow(img)
        if y is not None:
            ax.scatter(y[i][0::2]*img.shape[0], y[i][1::2]*img.shape[1], marker='x', s=10)
        ax.scatter(y_pred[i][0::2]*img.shape[0], y_pred[i][1::2]*img.shape[1], marker='s', s=10)

    pyplot.show()


if __name__ == "__main__":
    net = build_cnn_net()
    X, y = load_data("training_data/filtered_pics/")
    net.fit(X, y)

    import pickle
    with open('cnn2.pickle', 'wb') as f:
        pickle.dump(net, f, -1)

    X, y = load_data("training_data/test_pics/")

    plot_data(net, X, y)