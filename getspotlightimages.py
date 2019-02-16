import os
from json import load, dump
from hashlib import md5
from shutil import copy, move
from datetime import datetime
from cv2 import imread, split, subtract, countNonZero

# load home path
PC_NAME = os.path.expanduser("~")

pathToImages = os.path.join("C:\\", "Users", PC_NAME, "AppData", "Local", "Packages", "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy", "LocalState", "Assets")
pathToJson =   os.path.join("C:\\", "Users", PC_NAME, "AppData", "Local", "BackgroundImageRetriever")
pathToTest =   os.path.join("C:\\", "Users", PC_NAME, "Pictures", "Test")
pathToMobile = os.path.join(pathToTest, "Mobile")

'''
	Function to decide if the incoming image from the Assets folder
	is an image that is already saved in the given folder.

	Parameters:
		isDesktopImage: boolean - tells whether we need to change to Mobile folder or stay in the Test folder
		renamedFile: string - name of the current file/image that we retrieved from the Assets folder
		incomingImage: bitmap - cv2 object to compare shapes and rgb values of given image
'''
def checkForDuplicatesUsingOpenCV(isDesktopImage, renamedFile, incomingImage):
	# see TODO/HACK below
	currentYear = str(datetime.now().year)

	try:
		# used to tell if we need to rename the image once decided
		# that it will be kept in either the Test or Mobile folder
		isDeleted = False

		# we need to change the directory if to the
		# Mobile folder if it is a mobile image
		if not isDesktopImage:
			os.chdir(pathToMobile)

		# list the files in the current directory
		imagesInTest = os.listdir(".")
		for image in imagesInTest:

			# skip directories
			if os.path.isdir(image):
				continue

			# read the current image in the test folder
			matchingImage = imread(image)

			''' TODO/HACK: Why "if currentYear + "-" not in image"?
					Basically I'm saving the image in the Test folder first and then checking for duplicates
					on the incoming image from the Assets folder and there will always be a duplicate because
					I'm going through every image in the Test folder which includes the image that I just saved
					from the Assets folder. Need to find a better way to do this but it will do for now.
			'''
			# if the incoming image from the Assets folder and the image in my
			# Test folder match then we have possible duplicate images
			if currentYear + "-" not in image and incomingImage.shape == matchingImage.shape:
				# get the difference in the images
				difference = subtract(incomingImage, matchingImage)

				# extract the r, g, b values from the difference
				r, g, b = split(difference)

				# if their are no pixels in the image, that means the images were exactly identical
				if countNonZero(r) == 0 and countNonZero(g) == 0 and countNonZero(b) == 0:
					isDeleted = True
					# removing image from Test folder
					os.remove(renamedFile)
					break

		# if it is not deleted
		if not isDeleted:
			# we need to remove the 2019- in the name of the image so that
			# when we check for duplicates, we always check for every image
			os.rename(renamedFile, renamedFile[5:])
		return
	except Exception as error:
		print("Exception in checkForDuplicates():", str(error))

'''
	Checks against the hashes stored in the image-hashes.json file
	to see if the hash exists and if so then remove the file from
	the Test folder and return True else leave it and return False

	Parameters:
		hashed_file: hash - file hash
		renamedFile: string - name of the current file/image that we retrieved from the Assets folder
'''
def checkForDuplicatesUsingHashMap(hashed_file, renamedFile):
	# read the json file with all our hashes
	with open("image-hashes.json", "r") as file:
		# store the hashes from the json file
		hashes = load(file)

		# if the hash exists then remove the image from
		# the folder and continue to the next one
		if hashed_file.hexdigest() in hashes.keys():
    		# go back to the Test folder
			os.chdir(pathToTest)

			# remove the image from the test folder
			os.remove(renamedFile)

			return True

	return False

'''
	Main function to start the process which goes to the Assets folder,
	copies the image over to the Test folder, renames the image, decide
	if image is for Mobile or Desktop and moves accordingly, checks for
	duplicates and either deletes the image or keeps the image.
'''
def main():
		
	# try:
	# if the Test folder or Mobile folder does not already exist in the Pictures folder
	if not os.path.isdir(pathToTest) or not os.path.isdir(pathToMobile):
		# make the Test folder and the Mobile folder
		os.makedirs(pathToMobile, exist_ok=True)

	# if the Test folder or Mobile folder does not already exist in the Pictures folder
	if not os.path.isdir(pathToJson):
		# make the BackgroundImageRetriever folder in AppData
		os.mkdir(pathToJson)

	# if the image hash json file does not already exist then
	# we need to create the initial file
	os.chdir(pathToJson)

	if not os.path.isfile("image-hashes.json"):
		print("Initial json file not found. Creating...")
		initialize_images()
		
	# change directories to the original images
	os.chdir(pathToImages)

	# read all the files in the directory
	files = os.listdir(".")
	for file in files:
		
		# get the size of the current file
		sizeOfFile = os.path.getsize(file)

		# if the size is less than 150KB then skip and continue to next image
		if(sizeOfFile < 150000):
			continue

		# copy the file over to my test folder
		copy(os.path.abspath(file), pathToTest)

		# change the directory to manipulate the copied file
		os.chdir(pathToTest)

		# set the filename to a unique name
		renamedFile = str(datetime.now().isoformat().replace(":", "-")) + ".jpg"

		# rename the file
		os.rename(file, renamedFile)

		# read the incoming image
		incomingImage = imread(renamedFile)

		# if the image is in a strange format and cannot be read by cv2
		# skip the image because it is not an image we care about
		if incomingImage is None:
			print("Bad Image because incomingImage is of NoneType. Skipping...")
			os.remove(renamedFile)
			os.chdir(pathToImages)
			continue

		# extract the 3 variables that come from shape
		height, width, channels = incomingImage.shape

		# create the initial hash
		hashed_file = md5()

		# open the image and read as binary
		with open(renamedFile, "rb") as image:
			# create the hash of the image
			buf = image.read()
			hashed_file.update(buf)

		# if image is desktop or for mobile
		if (height == 1920 and width == 1080 and channels == 3) or (height == 1080 and width == 1920 and channels == 3):
			# go to where the json file is stored on user computer
			os.chdir(pathToJson)

			# if this returns true then just change the directory
			# back to the original images folder
			if checkForDuplicatesUsingHashMap(hashed_file, renamedFile):
				os.chdir(pathToImages)
				continue

			# initialize the new dictionary to add to the json file
			# which will be the old contents + the new hash
			added_data = {}

			# read the hashes from the json file
			with open("image-hashes.json", "r") as file:
				# store the hashes in data
				data = load(file)

			# create the new key value pair with hashed data
			added_data[hashed_file.hexdigest()] = renamedFile

			# update the json file with the new data
			data.update(added_data)

			# open the json file to write the new json data to
			with open("image-hashes.json", "w") as file:
				# add the new data to the json file
				dump(data, file, indent=4)

			# go back to the Test folder
			os.chdir(pathToTest)

			# if the image is mobile
			if height == 1920 and width == 1080 and channels == 3:
				# put it in the mobile folder
				move(renamedFile, os.path.join(pathToMobile))

		# else we don't want the image, so remove it from the test folder
		else:
			print("Bad Image because it's not for desktop or mobile. Skipping...")
			os.remove(renamedFile)
			os.chdir(pathToImages)
			continue

		# else it is a desktop image so leave it in the Test folder
		# and change back to the directory with the original images
		os.chdir(pathToImages)

	# except Exception as error:
	# 	print("Exception occurred in main():", str(error))

	os.startfile(pathToTest)
	print("Done!")

'''
	This function will create the initial json file that stores all
	the hashes of the images that we already have in the Test folder.
'''
def initialize_images():
	# create our initial hashmap
	hashMap = {}

	# read all the files in the directory
	# Set the directory where you want to start from
	for dirName, subdirList, fileList in os.walk(pathToTest):
		# go through each file in the directory
		for file in fileList:
			# create an initial hash
			hashed_file = md5()

			# create the path to the image (could be in the Mobile folder)
			pathToFile = os.path.join(dirName, file)

			# open the image
			with open(pathToFile, "rb") as image:
				# create the hash based on the image contents
				buf = image.read()
				hashed_file.update(buf)

			# add it to the dictionary with the hash as the key and the file name as the value
			hashMap[hashed_file.hexdigest()] = file

	# save the hashmap to a json file
	# w+ means to write to the file and
	# if it does not exist then create it
	with open("image-hashes.json", "w+") as file:
		# saving as json, passing the hashmap, the file
		# to save to and making the json file look pretty
		dump(hashMap, file, indent=4)

'''
	Beginning of script
'''
if __name__ == "__main__":
	main()
