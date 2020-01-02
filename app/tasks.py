# USAGE
# python recognize_faces_image.py --encodings encodings.pickle --image examples/example_01.png

# import the necessary packages
import face_recognition
import argparse
import pickle
import cv2
import time
import imutils

import os
import smtplib
from email.message import EmailMessage
import imghdr
# construct the argument parser and parse the arguments
# load the known faces and embeddings


def recognition(imgPath, picklePath):
    print("[INFO] loading encodings...")
    name = 'Unknown'
    # load the input image and convert it from BGR to RGB
    data = pickle.loads(open(picklePath, "rb").read())
    image = cv2.imread(imgPath)
    image = imutils.resize(image, width=200)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # detect the (x, y)-coordinates of the bounding boxes corresponding
    # to each face in the input image, then compute the facial embeddings
    # for each face
    print("[INFO] recognizing faces...")
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    # initialize the list of names for each face detected
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number of
            # votes (note: in the event of an unlikely tie Python will
            # select first entry in the dictionary)
            name = max(counts, key=counts.get)

        # update the list of names

        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(image, name, (left, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # show the output image
    # image=cv2.resize(image,(500,500))
    #cv2.imshow("Image", image)
    # cv2.imwrite('color_img.jpg',image)
    pname = name
    return image, pname


# path = '/home/nicat/Pictures/IMG_1064.JPG'
# picklePath = '/home/nicat/Documents/paper/face_recognition_api/app/encodings.pickle'
# face, name = recognition(path,picklePath)
# print(name)

def sendMessage(to, content, fileDir):
    EMAIL_ADD = 'face.recognition.iot@gmail.com'  # os.environ.get("MAIL_USER")
    EMAIL_PASS = 'tostwepjoygywzjn'  # os.environ.get("MAIL_PASS")

    msg = EmailMessage()
    msg["Subject"] = content
    msg["From"] = EMAIL_ADD
    msg["To"] = to
    msg.set_content(f"{content} sizi gozleyir!")

    with open(fileDir, "rb") as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = f.name

    msg.add_attachment(file_data, maintype="image",
                        subtype=file_type, filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADD, EMAIL_PASS)
        smtp.send_message(msg)
