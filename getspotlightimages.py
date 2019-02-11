import os
from shutil import copy, move
from datetime import datetime
from cv2 import imread, split, subtract, countNonZero
import logging

# set up logging to a file
logging.basicConfig(filename="background-image.log", filemode="a", level=logging.DEBUG)

# load home path
PC_NAME = os.environ['HOME']

pathToImages = os.path.join("C:\\", "Users", PC_NAME, "AppData", "Local", "Packages", "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy", "LocalState", "Assets")
pathToMobile = os.path.join(pathToTest, "Mobile")

currentYear = str(datetime.now().year)

'''
    Function to decide if the incoming image from the Assets folder
    is an image that is already saved in the given folder.

    Parameters: 
        isDesktopImage: boolean - tells whether we need to change to Mobile folder or stay in the Test folder
        renamedFile: string - name of the currect file/image that we retrieved from the Assets folder
        incomingImage: bitmap - cv2 object to compare shapes and rgb values of given image
'''
def checkForDuplicates(isDesktopImage, renamedFile, incomingImage):
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
        logging.exception("Exception in checkForDuplicates():", str(error))
        
'''
    Main function to start the process which goes to the Assets folder,
    copies the image over to the Test folder, renames the image, decide
    if image is for Mobile or Desktop and moves accordingly, checks for
    duplicates and either deletes the image or keeps the image.
'''
def main():
    try: 
        # if the Test folder or Mobile folder does not already exist in the Pictures folder
        if not os.path.isdir(pathToTest) or not os.path.isdir(pathToMobile):
            # make the Test folder and the Mobile folder
            os.makedirs(pathToMobile, exist_ok=True)

        # change directories to the original images
        os.chdir(pathToImages)

        # read all the files in the directory
        files = os.listdir(".")
        for file in files: 

            # get the size of the current file
            sizeOfFile = os.path.getsize(file)

            # if the size is less than 150KB then skip and continue to next image
            if(sizeOfFile < 150000):
                logging.debug("File not large enough. Skipping...")
                continue

            # copy the file over to my test folder
            copy(os.path.abspath(file), pathToTest)

            # change the directory to manipulate the copied file
            os.chdir(pathToTest)

            # set the filename to a unique name
            renamedFile = str(datetime.now().isoformat().replace(":", "-")) + ".jpg"

            # rename the file
            os.rename(file, renamedFile)

            logging.debug("Reading image using imread with:", str(renamedFile))

            # read the incoming image 
            incomingImage = imread(renamedFile)

            # if the image is in a strange format and cannot be read by cv2
            # skip the image because it is not an image we care about
            if incomingImage is None: 
                logging.debug("Bad Image because incomingImage is of NoneType. Skipping...")
                os.remove(renamedFile)
                os.chdir(pathToImages)
                continue

            # extract the 3 variables that come from shape
            height, width, channels = incomingImage.shape
            
            logging.debug("Image shape:", height, width, channels)

            # if the image is mobile
            if height == 1920 and width == 1080 and channels == 3:
                logging.debug("Image is for Mobile:", str(renamedFile))
                # put it in the mobile folder
                move(renamedFile, os.path.join(pathToMobile))
                checkForDuplicates(False, renamedFile, incomingImage) 
            # else if the image is for the desktop
            elif height == 1080 and width == 1920 and channels == 3:
                logging.debug("Image is for Desktop:", renamedFile)
                checkForDuplicates(True, renamedFile, incomingImage)
            # else we don't want the image, so remove it from the test folder
            else:
                os.remove(renamedFile)
                os.chdir(pathToImages)
                continue

            # else it is a desktop image so leave it in the Test folder
            # and change back to the directory with the original images
            os.chdir(pathToImages)

    except Exception as error:
        logging.exception("Exception occurred in main():", str(error))

'''
    Beginning of script
'''
if __name__ == "__main__":
    main()