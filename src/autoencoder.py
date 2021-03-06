
import itertools

import numpy as np
import main as m

import matplotlib.pyplot as plt

from keras.layers import Input, Dense
from keras.models import Model
from keras.optimizers import SGD

no_of_hidden_nodes = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
error_rate = [0, 0.05, 0.1, 0.15, 0.2]
learning_rate = 0.1
no_epochs = 2000
batch_size = 8

def get_autoenc_model(n):
	input_img = Input(shape=(17,))
	encoded = Dense(n, activation='sigmoid')(input_img)
	decoded = Dense(17, activation='sigmoid')(encoded)
	autoencoder = Model(input_img, decoded)
	sgd = SGD(lr=learning_rate)
	autoencoder.compile(optimizer=sgd, loss='binary_crossentropy')

	return autoencoder

def get_noisy_data(X, noise_lvl):
	l = len(X[0])
	lvl = int(round(noise_lvl * l))
	mask = [0] * lvl + [1] * (l - lvl)

	X_noisy = X.copy()

	for i in range(len(X)):
		np.random.shuffle(mask)
		X_noisy[i] = X_noisy[i] * mask

	return X_noisy

def train(X, X_noisy, autoencoder, verbosity = 2):
	autoencoder.fit(
		X_noisy, X,
		epochs=no_epochs,
		batch_size=batch_size,
		verbose = verbosity,
		validation_data = (X_noisy, X)
		)

def train_one(X, Y, n, e):
	X_noisy = get_noisy_data(X, e)
	autoencoder = get_autoenc_model(n)

	train(X, X_noisy, autoencoder, 0)
	X_regen = autoencoder.predict(X)

	return m.get_score(X_regen, Y)

def plot_result(res, baseline):
	colors = ['red', 'pink', 'green', 'yellow', 'black']

	plt.plot(no_of_hidden_nodes, [baseline] * len(res[0]), color='blue', label='baseline', linestyle='-')

	for err,color, rate in zip(res, colors, error_rate):
		plt.plot(no_of_hidden_nodes, err, color=color, label=str(rate*100)+'%', linestyle='-')

	plt.legend(loc = 'upper right')
	plt.xlabel('No of hidden nodes')

	plt.ylabel('Adjusted Rand Index')
	plt.savefig('result.svg')

def get_training_results():
	X, Y = m.get_dataset(m.dataset1_filepath)
	baseline = m.get_score(X, Y)
	# print train_one(X, Y, 16, 0.1)
	res = np.empty((len(error_rate), len(no_of_hidden_nodes)), dtype=float)

	for i in range(len(error_rate)):
		for j in range(len(no_of_hidden_nodes)):
			print "Training for %d hidden nodes %f corruption level" % (no_of_hidden_nodes[j], error_rate[i])
			ari = train_one(X, Y, no_of_hidden_nodes[j], error_rate[i])
			res[i][j] = ari

	plot_result(res, baseline)

if __name__ == '__main__':
	get_training_results()
