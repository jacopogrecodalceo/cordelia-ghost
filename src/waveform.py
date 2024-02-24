from wand.image import Image, Color
import numpy as np
#import matplotlib
#matplotlib.use('TkAgg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import librosa
import random

from .func import *

CUSTOM_CMAPs = [
	'RdPu',
	'PuRd',
	'BuPu',
	'PuBu',
	]

""" def plot_spectrogram(channel, args):
	y, n_fft, hop_length = args
	D = librosa.stft(y[channel], n_fft=n_fft, hop_length=hop_length)
	S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
	return S_db """

def make(input, transparency=False, invert=False):

	directory, basename, _ = get_info(input)
	output = os.path.join(directory, f'{basename}.png')

	y, sr = librosa.load(input, mono=False, sr=None)
	channels = y.shape[0]

	n_fft = 8192
	hop_length = n_fft // 16
	width = 16*256
	height = 9*256

	#result is 3149 × 1773
	#width = width + width - 3149
	#height = height + height - 1773
	dpi = width / (height / 25.4)
	#dpi = 300

	custom_cmap = random.choice(CUSTOM_CMAPs)

	spectrograms = []
	for channel in range(channels):
		#y, n_fft, hop_length = args
		D = librosa.stft(y[channel], n_fft=n_fft, hop_length=hop_length)
		S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
		#args = (y, n_fft, hop_length)
		#spectrograms = list(executor.map(lambda channel: plot_spectrogram(channel, args), range(channels)))
		y_harm, y_perc = librosa.effects.hpss(y[channel])
		spectrograms.append((S_db, y_harm, y_perc))

	fig, ax = plt.subplots(nrows=channels, dpi=dpi, figsize=(width // dpi, height // dpi), sharex=True)
	plt.subplots_adjust(hspace=(5 // dpi))

	for channel, (S_db, y_harm, y_perc) in enumerate(spectrograms):
		#print(S_db)
		librosa.display.specshow(S_db,
						x_axis='time',
						y_axis='log',
						ax=ax[channel],
						n_fft=n_fft,
						hop_length=hop_length,
						sr=sr,
						#cmap=plt.get_cmap(custom_cmap)
						)

		librosa.display.waveshow(y_harm, sr=sr, ax=ax[channel], color='b')
		librosa.display.waveshow(y_perc, sr=sr, ax=ax[channel], color='w')

		ax[channel].set_axis_off()

	fig.savefig(output, dpi=dpi, bbox_inches='tight', pad_inches=0)
	plt.close(fig)


	if invert:
		with Image(filename=output) as img:
			img.negate()
			img.save(filename=output)

	if transparency:
		with Image(filename=output) as img:
			fuzz = 0.15
			img.transparent_color(Color(has_more_black_than_white(output)), 0, fuzz=int(np.iinfo(np.uint16).max * fuzz))
			img.save(filename=output)
