from torchvision import models
from torchvision import transforms
from PIL import Image
import torchvision
import cv2
import json

class TorchRecognizer:
    COCO_INSTANCE_CATEGORY_NAMES = [
        '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
        'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
        'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
        'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
        'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
        'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
        'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
        'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
        'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]


    def __init__(self):
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
        self.model.cuda()
        self.model.eval()


    def get_prediction(self, img, threshold):
        transform = transforms.Compose([transforms.ToTensor()])  # Defing PyTorch Transform
        img = transform(img).cuda()  # Apply the transform to the image
        pred = self.model([img])  # Pass the image to the model
        pred_class = [self.COCO_INSTANCE_CATEGORY_NAMES[i] for i in list(pred[0]['labels'].cpu().numpy())]  # Get the Prediction Score
        pred_boxes = [((i[0], i[1]), (i[2], i[3])) for i in list(pred[0]['boxes'].detach().cpu().numpy())]  # Bounding boxes
        pred_score = list(pred[0]['scores'].detach().cpu().numpy())
        pred_t = [pred_score.index(x) for x in pred_score if x > threshold]
        pred_t = pred_t[-1] if pred_t else 0
        # Get list of index with score greater than threshold.
        pred_boxes = tuple(pred_boxes[:pred_t + 1])
        pred_class = tuple(pred_class[:pred_t + 1])

        return pred_boxes, pred_class

    def object_detection_api(self, img, threshold=0.30, rect_th=3, text_size=3, text_th=3):
        pilimg = Image.fromarray(frame)

        boxes, pred_cls = self.get_prediction(pilimg, threshold)  # Get predictions
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        for i in range(len(boxes)):
            print(boxes[i])
            cv2.rectangle(img, boxes[i][0], boxes[i][1], color=(0, 255, 0),
                          thickness=rect_th)  # Draw Rectangle with the coordinates
            cv2.putText(img, pred_cls[i], boxes[i][0], cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0),
                        thickness=text_th)  # Write the prediction class

        boxes = tuple((*box[0], *box[1]) for box in boxes)
        boxes = tuple(tuple(map(float, box)) for box in boxes)
        return frame, [(pred_cls[i], boxes[i]) for i in range(len(boxes))]


recognizer = TorchRecognizer()

cap = cv2.VideoCapture('/home/algernon/Downloads/_-T2Dwp0_q1hU.mkv')
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
out = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"XVID"), fps, (cap_width, cap_height))
all_detections = {}
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_num = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    print(f'{frame_num}/{length}')
    frame, detections_per_frame = recognizer.object_detection_api(frame)
    all_detections[frame_num] = detections_per_frame

with open('detections.json', 'w') as json_file:
    json.dump(all_detections, json_file)

out.release()
cap.release()


