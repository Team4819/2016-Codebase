import numpy as np
import scipy.ndimage
import theano.tensor as T
from opendeep import config_root_logger
from opendeep.models import Prototype, Conv2D, Dense, Softmax
from opendeep.models.utils import Noise, Pool2D
from opendeep.optimization.loss import Neg_LL
from opendeep.optimization import AdaDelta
from opendeep.monitor import Monitor
from opendeep.data.stream import ModifyStream
from opendeep.data import ImageDataset, MNIST

from . import filter_test

config_root_logger()

lenet = Prototype()

images = T.tensor4('xs')
images_shape = (None, 1, 640, 480)

lenet.add(Conv2D(inputs=(images_shape, images), n_filters=20, filter_size=(5, 5), border_mode="full", activation="relu"))
lenet.add(Pool2D, size=(2, 2))
lenet.add(Noise, noise="dropout", noise_level=0.5)

lenet.add(Conv2D, n_filters=20, filter_size=(5, 5), border_mode="full", activation="relu")
lenet.add(Pool2D, size=(2, 2))
lenet.add(Noise, noise="dropout", noise_level=0.5)

dense_input = lenet.models[-1].get_outputs().flatten(2)
dense_in_shape = lenet.models[-1].output_size[:1] + (np.prod(lenet.models[-1].output_size[1:]), )

lenet.add(Dense(inputs=(dense_in_shape, dense_input), outputs=500, activation="relu"))
lenet.add(Noise, noise="dropout", noise_level=0.5)

lenet.add(Softmax, outputs=10, out_as_probs=False)

labels = T.lvector('ys')

loss = Neg_LL(inputs=lenet.models[-1].p_y_given_x, targets=labels, one_hot=False)

accuracy = Monitor(name="Accuracy", expression=1-(T.mean(T.neq(lenet.models[-1].y_pred, labels))),
                   valid=True, test=True)


def greyscale_image(img):
    arr = np.average(img, 0)
    return arr


def target_preprocess(img):
    return filter_test.find_goal(img)

data = ImageDataset("training_data/cd_retro_pics", targets_preprocess=target_preprocess, inputs_preprocess=greyscale_image)

print("Building optimizer")
optimizer = AdaDelta(model=lenet, loss=loss, dataset=data, epochs=10)
optimizer.train(monitor_channels=accuracy)

print("Predicting...")
predictions = lenet.run(data.test_inputs)

print("Accuracy: ", float(sum(predictions == data.test_targets)) / len(data.test_targets))
