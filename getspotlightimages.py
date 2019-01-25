import os
import shutil
import datetime

pathToImages = os.path.join("C:\\", "Users", "<USERNAME>", "AppData", "Local", "Packages", 
                      "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy", "LocalState", "Assets")
pathToTest = os.path.join("C:\\", "Users", "<USERNAME>", "Pictures")
filesWithSizes = []
filteredFiles = []

os.chdir(pathToImages)
files = os.listdir(".")

for file in files: 
    locationOfFile = os.path.join(pathToImages, file)
    sizeOfFile = os.path.getsize(file)
    filesWithSizes.append((sizeOfFile, file))

for file in filesWithSizes:
    if(file[0] > 150000):
        filteredFiles.append(file[1])
        
filteredFiles.sort(key=lambda s: s[0])
filteredFiles.reverse()

for file in filteredFiles:
    print("File path: ", os.path.abspath(file))
    shutil.copy(os.path.abspath(file), pathToTest)
    os.chdir(pathToTest)
    os.rename(file, str(datetime.datetime.now().isoformat().replace(":", "-")) + ".jpg")
    os.chdir(pathToImages)

