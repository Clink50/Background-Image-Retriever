# Background-Image-Retriever - Version 3.0

## Overview

### I was looking at the background images that I get on Windows 10 and I'm always wishing I could find images like that. I did a quick google on where these images are located and come to find out that the images are pulled from the internet and saved on my machine. So I decided to get those images before they are deleted by Windows by setting up a task and scheduled it to run every morning at 6 AM to save to a folder in my Pictures. It works like a charm and is pretty simple.

### Note: If you delete an image in the Test folder by mistake, and you run the exe file again, you're image will not be retrieved. To get the image back, simply go to your AppData file (may need to "Show hidden files") and delete the folder called "BackgroundImageRetriever". Hopefully that will get your image back and keep your old images. Let me know if you run into any issues!

## Installation/Use

### Get the executable from the dist folder and everything **_should_** go smoothly! Please let me know if you run into any issues!

## Improvements

### I have made the improvement now to move mobile images to the mobile folder and keep the desktop images in the Test folder. I used OpenCV to do this and was very simple to do surprisingly. I'm getting the dimensions of the picture to decide if it should move to the mobile folder or stay in the Test folder. I am also using OpenCV to decide if I already have the image stored in my Test folder. This is likely since my Task Scheduler is set to run everyday. 
### ~~One improvement that I would like to make that I have no clue how to do is that the images are mixed between Desktop and Mobile. Anything over 150KB is an image that I want to save in my folder. I don't know how to ignore the Mobile images and keep the Desktop images. So I still have a manual piece of going in and moving the mobile pictures to another folder by having to look at each individual picture and seeing that it has the dimensions for a mobile phone, but I thought what I have is good enough.~~ 

### I have implemented the hashing and couldn't be happier with the results! I went from a program that took an image and searched through each image in the Test folder to see if there was a duplicate using OpenCV which took about 25 seconds to run on February 16, 2019 and everyday I get new images, so that number of seconds would just continue to grow. So from that to half a second using the image hashing which was a lot of fun. I'll be happy to hear any other suggestions or improvements, but I don't have any other ideas at the moment, so I guess we will let this play out for a while.
### ~~My next improvement will be to add Mapping/Hashing. As of right now I take the image from the Assets folder => go through each image in the Test folder to see if their is a duplicate => if there is then delete it else keep it. So this takes a long time. I want to set up Mapping/Hashing that way we just do one check for a matching hash and that's it. I don't know anything about this so yet another opportunity to learn.~~

## Why?

### I'm new to python and have been wanting to learn it for a while, but I just haven't had a chance and just wanted to take this as an opportunity to learn a little bit and have a nice slideshow of backgrounds when I open my computer.
