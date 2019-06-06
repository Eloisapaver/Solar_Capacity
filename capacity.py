"""
Program to calculate the capacity of a solar farm from a satellite image

Eloisa Paver Owen Huxley Jamie Taylor
2018-09-21
"""
import os
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.feature import blob_dog
from skimage import util
from PIL import Image, ImageEnhance

def main():
    """main function"""
    ##### Config #####
    directory = # Your directory here
    image_file = # Your filename here
    # Put 0 for image_file_2 if no second image
    image_file_2 = 0
    # Show image?
    plot_ = True
    ##################
    image = Image.open(os.path.join(directory, image_file))
    # Increase contrast to improve effectiveness of panel detection
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(2)
    # Convert to floats
    image = np.array(image, dtype=np.float64) / 255.
    image[np.argmax(image, axis=2) != 2] = np.array([1, 1, 1])
    _, axis = plt.subplots(2, 2)
    # Create copy of image so it is not overwritten when testing brightness removal
    image1 = np.copy(image)
    # Run removal of brightness below a certain value for 4 different values, to allow the user
    # to select the optimum value
    darkremove(0.1, image1)
    axis[0, 0].imshow(image1)
    axis[0, 0].set_title('removal below 10% brightness')
    darkremove(0.2, image1)
    axis[0, 1].imshow(image1)
    axis[0, 1].set_title('removal below 20% brightness')
    darkremove(0.3, image1)
    axis[1, 0].imshow(image1)
    axis[1, 0].set_title('removal below 30% brightness')
    darkremove(0.4, image1)
    axis[1, 1].imshow(image1)
    axis[1, 1].set_title('removal below 40% brightness')
    plt.show()
    # Allow user to input the best percentage brightnes to filter below
    value = float(input('Percentage brightness to be filtered below: '))/100
    panel_count_1 = count(image, value, 'one', plot_)
    panel_count_2 = 0
    if image_file_2 != 0:
        image2 = Image.open(os.path.join(directory, image_file_2))
        contrast = ImageEnhance.Contrast(image2)
        image2 = contrast.enhance(2)
        # Convert to floats
        image2 = np.array(image2, dtype=np.float64) / 255.
        image2[np.argmax(image2, axis=2) != 2] = np.array([1, 1, 1])
        panel_count_2 = count(image2, value, 'two', plot_)
    # Combine counts from both images
    panel_count = panel_count_1 + panel_count_2
    # Calculate total farm capacity based on different nominal capacities
    print('Capacity if panel = 205W:', panel_count * 205/ 1E6, 'MW')
    print('Capacity if panel = 215W:', panel_count * 215/ 1E6, 'MW')
    print('Capacity if panel = 225W:', panel_count * 225/ 1E6, 'MW')
    print('Capacity if panel = 235W:', panel_count * 235/ 1E6, 'MW')
    print('Capacity if panel = 245W:', panel_count * 245/ 1E6, 'MW')
    print('Capacity if panel = 255W:', panel_count * 255/ 1E6, 'MW')
    print(panel_count)

def darkremove(value, image):
    """remove all colours below a specified brightness percentage"""
    image[np.all(image < value, axis=2)] = np.array([1, 1, 1])
    
def count(image, value, im, plot_):
    """count the number of panels within an image using difference of Gaussian
    blob detection"""
    darkremove(value, image)
    # Load image and transform to a 2D numpy array
    depth = tuple(image.shape)[2]
    assert depth == 3
    # Ask user to input image scale size to create correct 'blob' sizes
    min_s, max_s = sigmas(float(input('What is the scale bar size of image ' + im +'? ')))
    # Convert the image to greyscale and invert to allow processing by algorithm
    grey = rgb2gray(image)
    grey = util.invert(grey)
    # Detect and count blobs
    blobs_dog = blob_dog(grey, min_sigma=min_s, max_sigma=max_s, threshold=.1, overlap=0.1)
    blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
    blobs_area = []
    # Create plot overlaying blobs on image
    if plot_:
        fig = plt.figure(figsize=(15, 15))
        axis = fig.add_subplot(1, 1, 1)
        # Plot blobs
        axis.imshow(image, interpolation='nearest')
        for blob in blobs_dog:
            y, x, r = blob
            rect = plt.Rectangle(((x-r), (y-r)), 2*r, 2*r, color='yellow', linewidth=2, fill=False)
            blobs_area.append(np.pi*r**2)
            axis.add_patch(rect)
        axis.set_axis_off()
        plt.tight_layout()
        plt.show()
    return len(blobs_dog)

def myround(scale, base=5):
    """rounds the inputted scale value to the nearest 5"""
    return int(base * round(float(scale)/base))

def sigmas(scale):
    """ assign a minimum and maximum sigma for blobs_dog function
    based on scale size of image used"""
    zoom = {20:14, 25:11, 30:10.5, 35:8, 40:6, 45:5, 50:5, 55:4.5, 
            60:4.5, 65:4.5, 70:4.2, 75:4, 80:4, 85:3.6, 90:3.6, 95:3.5, 100:3, 105: 2.8,
            110:2.5, 115:2, 120:2.5, 125:2, 130:2}
    rounded = myround(scale)
    min_s = zoom[rounded]
    max_s = min_s + 1
    return(min_s, max_s)

if __name__ == '__main__':
    main()
