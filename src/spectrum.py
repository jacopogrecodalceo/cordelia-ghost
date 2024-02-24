from wand.image import Image, Color
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import librosa
import random
import subprocess

from .func import *
CUSTOM_CMAPs = [
	'RdPu',
	'PuRd',
	'BuPu',
	'PuBu',
	]

width = 16*256
height = 9*256

""" def plot_spectrogram(channel, args):
	y, n_fft, hop_length = args
	D = librosa.stft(y[channel], n_fft=n_fft, hop_length=hop_length)
	S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
	return S_db """

def format_frequency(freq):
	freq = int(freq)
	if freq > 1000:
		return f"{freq / 1000:.1f}kHz"
	else:
		return f"{freq}Hz"

def format_time(duration, onset):
	return np.arange(onset, onset + duration, duration/11)

def format_mmss(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def process_plot_spectrum(input, output, onset, dur, color, axis, format):

	y, sr = librosa.load(input, mono=False, sr=None, offset=onset, duration=dur)
	duration = librosa.get_duration(y=y, sr=sr)

	channels = y.shape[0]

	n_fft = 4096
	hop_length = n_fft // 32

	#result is 3149 × 1773
	#width = width + width - 3149
	#height = height + height - 1773
	#dpi = width / (height / 25.4)
	dpi = 300

	spectrograms = []
	for channel in range(channels):
		#y, n_fft, hop_length = args
		D = librosa.stft(y[channel], n_fft=n_fft, hop_length=hop_length)
		S_db = librosa.amplitude_to_db(np.abs(D), top_db=120, ref=np.max)
		#args = (y, n_fft, hop_length)
		#spectrograms = list(executor.map(lambda channel: plot_spectrogram(channel, args), range(channels)))
		#y_harm, y_perc = librosa.effects.hpss(y[channel])
		spectrograms.append(S_db)

	fig, ax = plt.subplots(nrows=channels, dpi=dpi, figsize=(width // dpi, height // dpi))
	plt.subplots_adjust(hspace=0)

	linewidth = .25
	# Generate logarithmically spaced array of frequencies
	num_freqs = 11  # Number of frequency points
	min_freq = 20  # Minimum frequency in Hz
	max_freq = sr / 2  # Maximum frequency (Nyquist frequency)
	log_freqs = np.logspace(np.log10(min_freq), np.log10(max_freq), num=num_freqs)[:-1]

	times = format_time(duration, onset)
	#print([format_mmss(t) for t in times])
	for channel, S_db in enumerate(spectrograms):
		#print(S_db)
		# Generate film grain noise with the same shape as the spectrogram
		film_grain_noise = np.random.normal(loc=0, scale=5, size=S_db.shape)
		clipped_noise = np.clip(film_grain_noise, -10, 10)  # Adjust the range as needed

		# Add the noise to the spectrogram
		noisy_spectrogram = S_db + clipped_noise
		# Define the parameters for gamma correction

		librosa.display.specshow(noisy_spectrogram,
						x_axis='time',
						y_axis='log',
						ax=ax[channel],
						n_fft=n_fft,
						hop_length=hop_length,
						sr=sr,
						cmap=plt.get_cmap(color)
						)

		if axis:
  
			ax[channel].tick_params(labelsize=7, labelfontfamily='Andale Mono', width=linewidth)

			#ax[channel].grid(True, which='major', axis='x', linewidth=linewidth, color='black')  # Add gridlines
			ax[channel].set_xticks(times-onset)
			ax[channel].set_xticklabels([format_mmss(t) for t in times])  # Set y-axis tick labels

			if channel == 0:
				ax[channel].xaxis.set_ticks_position('top')
			else:
				ax[channel].set_xticks([])
				ax[channel].set_xticklabels([])  # Set y-axis tick labels

			ax[channel].set_xlabel('')
			ax[channel].set_ylabel(f'ch{channel+1}')
			#librosa.display.waveshow(y_harm, sr=sr, ax=ax[channel], color='b')
			#librosa.display.waveshow(y_perc, sr=sr, ax=ax[channel], color='w')
			# Customize the tick labels to add 's' for seconds

			ax[channel].set_yticks(log_freqs)  # Set y-axis ticks as logarithmically spaced frequencies
			ax[channel].set_yticklabels([format_frequency(freq) for freq in log_freqs], fontsize=3.5)  # Set y-axis tick labels

			#ax[channel].set_ylim([0, sr / 2])  # Adjust the y-axis limit to the Nyquist frequency
			ax[channel].xaxis.set_minor_locator(plt.NullLocator())
			ax[channel].yaxis.set_minor_locator(plt.NullLocator())

			# Remove outside borders
			ax[channel].spines['top'].set_visible(False)
			ax[channel].spines['right'].set_visible(False)
			ax[channel].spines['left'].set_visible(False)

			#line_x_adjust = 1/2048  # Adjust the horizontal position of the line
			ax[channel].spines['bottom'].set_capstyle('butt')
			#plt.axhline(y=log_freqs[-1]*(channel+1), color='black', linewidth=linewidth, xmin=line_x_adjust, xmax=1-line_x_adjust)  # Adjust the y-coordinate as needed
			ax[channel].spines['bottom'].set_visible(True if channel < channels-1 else False)
		else:
			ax[channel].set_axis_off()


	fig.savefig(output, dpi=dpi, bbox_inches='tight', pad_inches=1/8, format=format)
	plt.close(fig)
	#return output

def make(audio_file, transparency=False, invert=False, grain=False, enhance=False, onset=0.0, dur=None, output_directory=None, color=None, axis=True, format='pdf'):
	same_directory, basename, _ = get_info(audio_file)
	print("Audio File:", audio_file)
	print("Transparency:", transparency)
	print("Invert:", invert)
	print("Grain:", grain)
	print("Enhance:", enhance)
	print("Onset:", onset)
	print("Duration:", dur)
	print("Output Directory:", output_directory)
	print("Color:", color)
	print("Axis:", axis)
	print("Format:", format)
	
	if not color:
		custom_cmap = random.choice(CUSTOM_CMAPs)
	else:
		custom_cmap = color
  
	output = os.path.join(output_directory if output_directory else same_directory, f'{basename}-{int(onset)}-{custom_cmap}.{format}')
	process_plot_spectrum(audio_file, output, onset, dur, custom_cmap, axis, format)

	if enhance:
		with Image(filename=output, resolution=300, format=format) as img:
			# Apply image enhancement techniques here
			img.sharpen(radius=1, sigma=.95)
			img.level(black=0.125, white=.925, gamma=1.0)
			img.blur(radius=1, sigma=.95)

			# Save the enhanced image
			img.save(filename=output)

	if invert:
		with Image(filename=output, resolution=300, format=format) as img:
			img.alpha_channel = False
			img.negate()
			img.save(filename=output)

	if grain:
		command = f'/Users/j/Documents/zsh/filmgrain "{output}" "{output}" -b .25 -A 75'
		subprocess.run(command, shell=True)

	if transparency:
		with Image(filename=output, resolution=300, format=format) as img:
			fuzz = .105
			img.transparent_color(Color('white'), 0, fuzz=int(np.iinfo(np.uint16).max * fuzz))
			img.trim()
			img.save(filename=output)



