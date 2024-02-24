import argparse

from src import spectrum

# Define the command-line interface
def parse_arguments():
	parser = argparse.ArgumentParser(description='Description of your CLI tool.')
	parser.add_argument('audio_file', type=str, help='File to analyse')
 
	parser.add_argument('-t', '--transparency', action='store_true', help='Make transparency')
	parser.add_argument('-i', '--invert', action='store_true', help='Make invert')
	parser.add_argument('-g', '--grain', action='store_true', help='Make grain')
	parser.add_argument('-e', '--enhance', action='store_true', help='Enhance')
	parser.add_argument('-n', '--axis', action='store_false', help='No axis')
 
	parser.add_argument('-s', '--onset', type=float, help='Onset position', default=0.0)
	parser.add_argument('-d', '--dur', type=float, help='Duration')
 
	parser.add_argument('-o', '--output_directory', type=str, help='Output directory')
	parser.add_argument('-c', '--color', type=str, help='Choose color')
	parser.add_argument('-f', '--format', type=str, help='Choose format', default='pdf')
	#parser.add_argument('-o', '--option', type=int, default=10, help='Description of an option')
	return parser.parse_args()

# Define the functionality of your CLI tool
def main():
	args = parse_arguments()

	# Execute functionality based on command-line arguments
	# Your code here
	spectrum.make(**vars(args))
 
# Entry point of the script
if __name__ == '__main__':
	main()

