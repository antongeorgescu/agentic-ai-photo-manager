import os
from ultralytics import YOLO
import cv2
import numpy as np

model = YOLO("yolov8n.pt")  # Nano version

# Load YOLOv3 model
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

IN_IMAGE_FILE = f"{os.getenv("MEDIA_SOURCE_PATH")}/IMG_4042.jpg"

# Load image
image = cv2.imread(IN_IMAGE_FILE)
height, width = image.shape[:2]

# Prepare the image
blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), swapRB=True, crop=False)
net.setInput(blob)
outs = net.forward(output_layers)

# Process detections
boxes, confidences, class_ids = [], [], []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x, center_y = int(detection[0]*width), int(detection[1]*height)
            w, h = int(detection[2]*width), int(detection[3]*height)
            x, y = int(center_x - w/2), int(center_y - h/2)
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

# Apply Non-Max Suppression
indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

# Draw boxes
for i in indices.flatten():
    x, y, w, h = boxes[i]
    label = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save and show result
OUT_IMAGE_FILE = f"{os.getenv("MEDIA_SOURCE_PATH")}/IMG_4042_X.jpg"
cv2.imwrite(OUT_IMAGE_FILE, image)
cv2.imshow("Detected Objects", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

