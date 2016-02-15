from lasagne import layers
from lasagne.updates import nesterov_momentum
from nolearn.lasagne import NeuralNet
import numpy as np
import os
from os.path import join
import cv2
from matplotlib import pyplot
import csv

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
        input_shape=(None, 1, 160, 120),
        conv1_num_filters=16, conv1_filter_size=(4, 4), pool1_pool_size=(2, 2),
        conv2_num_filters=32, conv2_filter_size=(2, 2), pool2_pool_size=(2, 2),
        conv3_num_filters=64, conv3_filter_size=(2, 2), pool3_pool_size=(2, 2),
        hidden4_num_units=500, hidden5_num_units=100,

        output_nonlinearity=None,
        output_num_units=3,

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
        input_shape=(None, 90, 80),
        hidden1_num_units=500,
        hidden2_num_units=100,

        output_nonlinearity=None,
        output_num_units=3,

        update=nesterov_momentum,
        update_learning_rate=0.01,
        update_momentum=0.9,

        regression=True,
        max_epochs=1000,
        verbose=1
    )


def load_data(paths, max_count=-1, offset=0, mirror=True):
    X = []
    y = []
    for path in paths:
        csv_file = csv.DictReader(open(os.path.join(path, "posdata.csv")))
        offset_ticks = 0
        for row in csv_file:
            if offset > offset_ticks:
                offset_ticks += 1
                continue
            frame = row["frame"]
            depth_fname = "depth_{}.jpg".format(frame)
            if len(X) == max_count:
                break
            fname = join(path, depth_fname)
            img = cv2.resize(cv2.imread(fname), (160, 120)).transpose(2, 1, 0)[0:1]/255
            x_pos = (float(row["x"])+15)/30
            y_pos = (5-float(row["y"]))/20
            r_pos = (float(row["r"])+90)/180
            X.append(img)
            y.append((x_pos, y_pos, r_pos))
            if mirror:
                X.append(img[..., ::-1])
                y.append((1-x_pos, y_pos, 1-r_pos))


    X = np.array(X)
    y = np.array(y)
    print("X min {} max {}".format(X.min(), X.max()))
    print("y min {} max {}".format(y.min(), y.max()))
    return X, y


def plot_data(net, X, y=None):
    y_pred = net.predict(X)

    fig = pyplot.figure(figsize=(6, 6))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)
    for i in range(8):
        ax = fig.add_subplot(4, 4, i + 1, xticks=[], yticks=[])
        img = X[i].transpose(2, 1, 0)[:, :, 0]
        ax.imshow(img, 'gray')
        if y is not None:
            ax.scatter(y[i][0]*img.shape[0], y[i][1]*img.shape[1], marker='x', s=10)
        ax.scatter(y_pred[i][0]*img.shape[0], y_pred[i][1]*img.shape[1], marker='s', s=10)

    pyplot.show()


if __name__ == "__main__":
    net = build_cnn_net()
    X, y = load_data(["dataset/set_1", "dataset/set_2"])
    net.fit(X, y)

    import pickle
    with open('cnn.pickle', 'wb') as f:
        pickle.dump(net, f, -1)

    X, y = load_data(["dataset/set_2"], 20, 40)

    plot_data(net, X, y)
