# using face recognition package
# usingg cv2

import face_recognition
import os
import cv2


KNOWN_FACES_DIR = 'known_faces'
UNKNOWN_FACES_DIR = 'unknown_faces'
TOLERANCE = 0.6	# whta is the match percentage so that it resukts true
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'cnn'  # 'hog' or 'cnn' - CUDA accelerated (if available) deep-learning pretrained model



'''
We'll be using os for working with directories and cv2 for labeling/drawing on our images.

The first two constants are just the names of our known and unknown directories.

Next we have TOLERANCE. This is a value from 0 to 1 that will allow you to tweak the sensitivity of labeling/predictions. 
The default value here in the face_recognition package is 0.6. The lower the tolerance, the more "strict" the labels will be.

If you're getting a bunch of labels of some identity on a bunch of faces that aren't correct, you may want to lower the TOLERANCE. 
If you're not getting any labels at all, then you might want to raise the TOLERANCE.

The FRAME_THICKNESS value is how many pixels wide do you want the rectangles that encase a face to be and 
FONT_THICKNESS is how thick you want the font with the label to be.

Finally, you can choose what model to use. We'll use the cnn (convolutional neural network), 
but you can also use hog (histogram of oriented gradients) which is a non-deep learning approach to object detection.

The first things we need to do is prepare the faces that we intend to look for/identify. 
We'll start with a couple of lists. One for the faces, the other for the names associated with these faces:
'''


print('Loading known faces...')
known_faces = []
known_names = []

'''
Now we iterate over our known faces directory, 
which contains possibly many directories of identities, 
which then contain one or more images with that person's face. 
From here, we want to load in this image with the face_recognition package, like:
'''

for name in os.listdir(KNOWN_FACES_DIR):

    # Next we load every file of faces of known person
    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):

        # Load an image
        image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')


# Continuing along in this same loop, we will encode each of these faces, then store the encodings and the associated identity to our lists:
for name in os.listdir(KNOWN_FACES_DIR):

    # Next we load every file of faces of known person
    for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):

        # Load an image
        image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')

        # Get 128-dimension face encoding
        # Always returns a list of found faces, for this purpose we take first face only (assuming one face per image as you can't be twice on one image)
        encoding = face_recognition.face_encodings(image)[0]

        # Append encodings and name
        known_faces.append(encoding)
        known_names.append(name)

# At this point, we're ready to check unknown images for faces, and then to try to identify those faces!
# This loop will start in a familiar way:
print('Processing unknown faces...')
# Now let's loop over a folder of faces we want to label
for filename in os.listdir(UNKNOWN_FACES_DIR):

    # Load image
    print(f'Filename {filename}', end='')
    image = face_recognition.load_image_file(f'{UNKNOWN_FACES_DIR}/{filename}')


# While known_images are just face shots, we assume that unknown images might have multiple people and other objects in them. 
# Thus, we want to first locate those faces. We do that with:
locations = face_recognition.face_locations(image, model=MODEL)


# Then we'd encode these images:
encodings = face_recognition.face_encodings(image, locations)

# Notice that this method of encoding for the unknown faces is different than the encoding we used for the known face, 
# which was: encoding = face_recognition.face_encodings(image)[0]

# It's expected that our known face isn the only face in the image, so we're going with the first encoding, 
# and we didnt first grab locations because we don't really care about locations of faces in the known_images, 
# but we want these locations in the unknown images so that we can label them.

# Now we can iterate over the faces found in the unknown images, to see if we can find a match with any of our known faces. 
# If we find one, we want to draw a rectangle around them. For that reason, we're going to use OpenCV to draw, 
# and we'll first convert the image from RGB to BGR since OpenCV uses BGR. Doing that is as simple as:
image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


# This makes our current loop so far:

print('Processing unknown faces...')
# Now let's loop over a folder of faces we want to label
for filename in os.listdir(UNKNOWN_FACES_DIR):

    # Load image
    print(f'Filename {filename}', end='')
    image = face_recognition.load_image_file(f'{UNKNOWN_FACES_DIR}/{filename}')

    # This time we first grab face locations - we'll need them to draw boxes
    locations = face_recognition.face_locations(image, model=MODEL)

    # Now since we know loctions, we can pass them to face_encodings as second argument
    # Without that it will search for faces once again slowing down whole process
    encodings = face_recognition.face_encodings(image, locations)

    # We passed our image through face_locations and face_encodings, so we can modify it
    # First we need to convert it from RGB to BGR as we are going to work with cv2
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)




# Now we're going to iterate over each face found in the unknown image and check for any matches with our known faces:

print('Processing unknown faces...')
# Now let's loop over a folder of faces we want to label
for filename in os.listdir(UNKNOWN_FACES_DIR):

    # Load image
    print(f'Filename {filename}', end='')
    image = face_recognition.load_image_file(f'{UNKNOWN_FACES_DIR}/{filename}')

    # This time we first grab face locations - we'll need them to draw boxes
    locations = face_recognition.face_locations(image, model=MODEL)

    # Now since we know loctions, we can pass them to face_encodings as second argument
    # Without that it will search for faces once again slowing down whole process
    encodings = face_recognition.face_encodings(image, locations)

    # We passed our image through face_locations and face_encodings, so we can modify it
    # First we need to convert it from RGB to BGR as we are going to work with cv2
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # But this time we assume that there might be more faces in an image - we can find faces of dirrerent people
    print(f', found {len(encodings)} face(s)')
    for face_encoding, face_location in zip(encodings, locations):

        # We use compare_faces (but might use face_distance as well)
        # Returns array of True/False values in order of passed known_faces
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)


# The results variable holds a list of booleans, regarding if any matches were found:
print(results)


# We take the index value for any of the True's here, and look for the name from our known_names variable:

match = known_names[results.index(True)]
print(match)



# Now we want to draw a rectangle around this recognized face. 
# To draw a rectangle in OpenCV, we need the top left and bottom right coordinates, and we use cv2.rectangle to draw it.

# We also need a color for this box, and it would be neat to have this box color fairly unique to the identity.

# Daniel (DhanOS) came up with the following code to take the first 3 letters in the string, and convert these to RGB values:

color = [(ord(c.lower())-97)*8 for c in match[:3]]
print(color)

# Which we'll convert to a function:

# Returns (R, G, B) from name
def name_to_color(name):
    # Take 3 first letters, tolower()
    # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
    color = [(ord(c.lower())-97)*8 for c in name[:3]]
    return color


# Beyond having a rectangle for the face itself, we'll add a smaller rectangle for the text for the identity, 
# then of course place the text for that identity. The part just for that:

        if True in results:  # If at least one is true, get a name of first of found labels
            match = known_names[results.index(True)]
            print(f' - {match} from {results}')

            # Each location contains positions in order: top, right, bottom, left
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])

            # Get color by name using our fancy function
            color = name_to_color(match)

            # Paint frame
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

            # Now we need smaller, filled grame below for a name
            # This time we use bottom in both corners - to start from bottom and move 50 pixels down
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2] + 22)

            # Paint frame
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

            # Wite a name
            cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_H