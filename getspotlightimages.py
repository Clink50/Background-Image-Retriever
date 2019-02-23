import os
import ctypes
import logging
from uuid import uuid4
from hashlib import md5
from json import load, dump
from shutil import copy, move
from datetime import datetime
from cv2 import imread, split, subtract, countNonZero

# load home path
PC_NAME = os.path.expanduser("~")

pathToImages = os.path.join("C:\\", "Users", PC_NAME, "AppData", "Local", "Packages", "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy", "LocalState", "Assets")
pathToData = os.path.join("C:\\", "Users", PC_NAME, "AppData", "Local", "BackgroundImageRetriever")
pathToTest = os.path.join("C:\\", "Users", PC_NAME, "Pictures", "Test")
pathToMobile = os.path.join(pathToTest, "Mobile")

environment = "dev"

'''
	Function to decide if the incoming image from the Assets folder
	is an image that is already saved in the given folder.

	Parameters:
		isDesktopImage: boolean - tells whether we need to change to Mobile folder or stay in the Test folder
		renamedFile: string - name of the current file/image that we retrieved from the Assets folder
		incomingImage: bitmap - cv2 object to compare shapes and rgb values of given image
'''
def CheckForDuplicatesUsingOpenCV(isDesktopImage, renamedFile, incomingImage):
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
	Initialize the project by creating the data folder in AppData if it 
	it doesn't exist and if the logging file doesn't exist also create it.
'''
def initializeProject(guid):
	try:
		# change the path to AppData 
		os.chdir(pathToData)

		# if there is not already a folder for storing the json in AppData then create it
		if not os.path.isdir(pathToData):
			# make the BackgroundImageRetriever folder in AppData
			os.mkdir(pathToData)
			
		logLevel = logging.ERROR if environment == "prod" else logging.DEBUG
		logging.basicConfig(filename="background-image.log", format="%(asctime)s - %(levelname)s - %(message)s", level=logLevel, datefmt="%d-%b-%y %H:%M:%S")

		# if the Test folder or Mobile folder does not already exist in the Pictures folder
		if not os.path.isdir(pathToTest) or not os.path.isdir(pathToMobile):
			logging.debug(f"{guid} - Test or Mobile folder not found. Creating...")
			# make the Test folder and the Mobile folder
			os.makedirs(pathToMobile, exist_ok=True)

		# if the hash file for the images doesn't not exist then create it
		if not os.path.isfile(os.path.join(pathToData, "image-hashes.json")):
			logging.debug(f"{guid} - Initial json file not found. Creating...")
			# get the hashes for all the images that is currently in the Test folder
			initializeImages(guid)

		# change directories to the original images
		os.chdir(pathToImages)
	except Exception as error:
		logging.exception(f"{guid} - Error occurred while initializing the project in initializeImages.")

'''
	This function will create the initial json file that stores all
	the hashes of the images that we already have in the Test folder.
'''
def initializeImages(guid):
	try:
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

		logging.debug(f"{guid} - Opening json file to store all image hashes...")

		# save the hashmap to a json file
		# w+ means to write to the file and
		# if it does not exist then create it
		with open("image-hashes.json", "w+") as file:
			# saving as json, passing the hashmap, the file
			# to save to and making the json file look pretty
			dump(hashMap, file, indent=4)

		logging.debug(f"{guid} - Hashes saved...")

	except Exception as error:
		logging.exception(f"{guid} - Error occurred while hashing images in initializeImages - {pathToFile}")

'''
	Checks against the hashes stored in the image-hashes.json file
	to see if the hash exists and if so then remove the file from
	the Test folder and return True else leave it and return False

	Parameters:
		hashed_file: hash - file hash
		renamedFile: string - name of the current file/image that we retrieved from the Assets folder
'''
def checkForDuplicatesUsingHashMap(hashed_file, renamedFile, guid):
	try:
		logging.info(f"{guid} - Opening json file to check for duplicates.");

		# read the json file with all our hashes
		with open("image-hashes.json", "r") as file:
			# store the hashes from the json file
			hashes = load(file)

			# if the hash exists then remove the image from
			# the folder and continue to the next one
			if hashed_file.hexdigest() in hashes.keys():
				# go back to the Test folder
				os.chdir(pathToTest)

				logging.info(f"{guid} - Duplicate image found. Deleting - {renamedFile}")
				# remove the image from the test folder
				os.remove(renamedFile)

				return True

		return False

	except Exception as error:
		logging.exception(f"{guid} - Error occurred while checking for duplicates in checkForDuplicatesUsingHashMap.")

'''
	Main function to start the process which goes to the Assets folder,
	copies the image over to the Test folder, renames the image, decide
	if image is for Mobile or Desktop and moves accordingly, checks for
	duplicates and either deletes the image or keeps the image.
'''
def main():
	guid = str(uuid4())
	try:
		initializeProject(guid)
		
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

			logging.info(f"{guid} - Using CV2 to read image...")
			# read the incoming image
			incomingImage = imread(renamedFile)

			# if the image is in a strange format and cannot be read by cv2
			# skip the image because it is not an image we care about
			if incomingImage is None:
				logging.warning(f"{guid} - Bad Image because incomingImage is of NoneType. Skipping...")
				os.remove(renamedFile)
				os.chdir(pathToImages)
				continue

			# extract the 3 variables that come from shape
			height, width, channels = incomingImage.shape

			# create the initial hash
			hashed_file = md5()

			logging.info(f"{guid} - Opening image to create the hash - {renamedFile}");

			# open the image and read as binary
			with open(renamedFile, "rb") as image:
				# create the hash of the image
				buf = image.read()
				hashed_file.update(buf)

			logging.info(f"{guid} - Image hash created...")

			# if image is desktop or for mobile
			if (height == 1920 and width == 1080 and channels == 3) or (height == 1080 and width == 1920 and channels == 3):
				# go to where the json file is stored on user computer
				os.chdir(pathToData)

				# if this returns true then just change the directory
				# back to the original images folder
				if checkForDuplicatesUsingHashMap(hashed_file, renamedFile, guid):
					logging.info(f"{guid} - Duplicate was found. Moving to next image...")
					os.chdir(pathToImages)
					continue

				# initialize the new dictionary to add to the json file
				# which will be the old contents + the new hash
				added_data = {}

				logging.info(f"{guid} - Opening json file to load hashes.")

				# read the hashes from the json file
				with open("image-hashes.json", "r") as file:
					# store the hashes in data
					data = load(file)

				logging.info(f"{guid} - Hash stored in data object - {renamedFile}")

				# create the new key value pair with hashed data
				added_data[hashed_file.hexdigest()] = renamedFile

				logging.info(f"{guid} - Adding image hash to data object.")
				# update the json file with the new data
				data.update(added_data)

				logging.info(f"{guid} - Data object updated. Writing new data to json file...")

				# open the json file to write the new json data to
				with open("image-hashes.json", "w") as file:
					# add the new data to the json file
					dump(data, file, indent=4)

				logging.info(f"{guid} - Data with new image hash stored in json file.")

				# go back to the Test folder
				os.chdir(pathToTest)

				# if the image is mobile
				if height == 1920 and width == 1080 and channels == 3:
					logging.info(f"{guid} - Image is for Mobile. Moving to Mobile folder...")
					# put it in the mobile folder
					move(renamedFile, os.path.join(pathToMobile))

			# else we don't want the image, so remove it from the test folder
			else:
				logging.warning(f"{guid} - Bad Image path - {os.getcwd()}")
				logging.warning(f"{guid} - Bad Image image name - {renamedFile}")
				logging.warning(f"{guid} - Bad Image because it's not for desktop or mobile. Removing image...")
				os.remove(renamedFile)
				os.chdir(pathToImages)
				continue

			# else it is a desktop image so leave it in the Test folder
			# and change back to the directory with the original images
			os.chdir(pathToImages)

	except Exception as error:
		logging.exception(f"{guid} - Error occurred in main.")
		answer = ctypes.windll.user32.MessageBoxW(0, f"Error occurred while retrieving images! Please check at \n {pathToData}/background-image.log to see the issue. \n\nIf the issue cannot be resolved, please log an issue at here: https://github.com/clink73/Background-Image-Retriever/issues/new", "Error", 1)
		exit()

	os.startfile(pathToTest)
	logging.info(f"{guid} - Background Image Retriever complete.")

'''
	Beginning of script
'''
if __name__ == "__main__":
	main()
