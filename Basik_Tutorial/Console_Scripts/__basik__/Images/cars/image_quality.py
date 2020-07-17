

from PIL import Image
import os

#------------------------------------------------------------------------------

def homogenize_images(standard:'name.png',
                      path,
                      new_path,
                      quality=85):
    
    '''
    A function to make all the vehicle images of the same size and 
    quality in terms of pixels. The main reasoning behind this is to ensure
    that the rotation of the image matrix takes the same amount of time
    for all vehicles thus allowing a for the program to be consistent in 
    terms of running time.
    '''
    
    # If the directory specified by new_path does not exist, we will
    # create one.
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    
    # Open the standard image and place it in the new directory/folder.
    standard_image = Image.open(path + '/' + standard)
    standard_image.save(new_path + '/'  + standard)
    
    # Get all the images in the path
    others = os.listdir(path)
    
    # If standard is in this list, we will remove it.
    try:
        others.remove(standard)
    except ValueError:
        # Not in the list!
        pass
    
    # Homogenize the images: make it the same quality as standard.
    for image_name in others:
        image = Image.open(path + '/' + image_name)
        image = image.resize(standard_image.size,Image.ANTIALIAS)
        image.save(new_path + '/'  + image_name,
                   optimize=True,quality=quality)
        
    return None


#------------------------------------------------------------------------------



if __name__ == '__main__':
    
    standard = 'green.png'
    path = './Original'
    # Path 1
    new_path = './Homogenized'
    homogenize_images(standard,
                      path,
                      new_path)
    # Path 2
    new_path = '.'
    homogenize_images(standard,
                      path,
                      new_path)
    
    
#------------------------------------------------------------------------------
        