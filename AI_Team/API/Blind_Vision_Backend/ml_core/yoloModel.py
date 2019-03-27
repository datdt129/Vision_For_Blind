import numpy as np
import time
import cv2
import os
import matplotlib.pyplot as plt
import color

def load_label(labelpath):
    # load the COCO class labels our YOLO model was trained on
    labels = open(labelpath).read().strip().split("\n")
    #initialize a list of colors to represent each possible class label
    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
    return labels, colors

def load_image(imagepath):
    image = cv2.imread(imagepath)
    return image

def load_model():
     #load our YOLO object detector trained on COCO dataset (80 classes)
     #and determine only the *output* layer names that we need from YOLO
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, ln

def detectObjectFromImage(image, net, ln):
    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    H, W = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB = True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)
    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []
    centers = []

    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > 0.5:
                box = detection[0:4]*np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype('int')

                x = int(centerX - width/2)
                y = int(centerY - height/2)
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)
                centers.append((centerX, centerY))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.3)
    return idxs, boxes, confidences, centers, classIDs

def bouding_box(idxs, image, boxes, colors, labels, classIDs, confidences):
    H, W = image.shape[:2]
    if len(idxs) > 0:
	    # loop over the indexes we are keeping
        for i in idxs.flatten():
		    # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
 
		    # draw a bounding box rectangle and label on the image
            c = [int(c) for c in colors[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), c, 2)
            text = "{}: {:.4f}".format(labels[classIDs[i]], confidences[i])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 2)
    # show the output image
        img = cv2.resize(image, (H, W))
        return img

def getObjectProperty(idxs, image, boxes, colors, labels, classIDs, confiences):
    H, W = image.shape[:2]
    objectPropertyList = []
    if len(idxs) > 0:
	    # loop over the indexes we are keeping
        for i in idxs.flatten():
		    # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            if x < 0: x = 0
            if x > W: x = W
            if y > H: y = H
            if y < 0: y = 0
            if x+w > W: w = W - x
            if y+ h > H: y = H-h
		    # draw a bounding box rectangle and label on the image
            colorr = [int(c) for c in colors[classIDs[i]]]
            text = labels[classIDs[i]]
            confience = confiences[i]
            im = image[y:y+h, x:x+w]
            c = color.get_color(im)
            objectPropertyList.append({
                "text": text,
                "confidence": confience,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "color": c
            })
		    #cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    # show the output image
        return objectPropertyList
    else: 
        return "None" 


         

            