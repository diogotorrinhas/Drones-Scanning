import cv2
import numpy as np

def need_water(green_percent, yellow_percent, brown_percent):
    """Return True if the plant needs water, False otherwise"""
    if green_percent >= 80 and yellow_percent < 75:
        return False
    elif yellow_percent >= 85:
        return True
    elif brown_percent >= 50:
        return True
    else:
        return False

def analyse_image(filename):
    # Load the image and convert it to the HSV color space
    img = cv2.imread(filename)
    
    if img is None:
        print("Could not read the image file.")
        exit()
        
    #Transform the image to HSV color space
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the range of colors to look for
    lower_green = np.array([25, 52, 72])
    upper_green = np.array([102, 255, 255])
    mask_green = cv2.inRange(hsv_img, lower_green, upper_green)

    lower_yellow = np.array([15, 80, 80])
    upper_yellow = np.array([40, 255, 255])
    mask_yellow = cv2.inRange(hsv_img, lower_yellow, upper_yellow)

    lower_brown = np.array([0, 20, 20])
    upper_brown = np.array([20, 255, 255])
    mask_brown = cv2.inRange(hsv_img, lower_brown, upper_brown)

    # Combine the masks
    mask = mask_green + mask_yellow + mask_brown

    # Count the number of pixels that are green, yellow, or brown
    green_pixels = cv2.countNonZero(mask_green)
    yellow_pixels = cv2.countNonZero(mask_yellow)
    brown_pixels = cv2.countNonZero(mask_brown)

    # Count the total number of pixels
    total_pixels = img.shape[0] * img.shape[1]

    # Calculate the percentage of green, yellow, and brown pixels
    green_percent = (green_pixels / total_pixels) * 100
    yellow_percent = (yellow_pixels / total_pixels) * 100
    brown_percent = (brown_pixels / total_pixels) * 100

    # Print the percentages of green, yellow, and brown pixels
    print("The percentage of green pixels in the image is: ", green_percent)
    print("The percentage of yellow pixels in the image is: ", yellow_percent)
    print("The percentage of brown pixels in the image is: ", brown_percent)
    
    return green_percent, yellow_percent, brown_percent
    
#Test the function

#filename = input("Enter the name of the image file: ")
#green_percent, yellow_percent, brown_percent = analyse_image(filename)
#water = need_water(green_percent, yellow_percent, brown_percent)
#print("The farm area needs water: ", water)

