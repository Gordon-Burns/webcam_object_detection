import glob
import os
import cv2
import numpy
import time
from datetime import datetime
from emailing import send_email
from threading import Thread

video = cv2.VideoCapture(1)
time.sleep(0.5)

first_frame = None
status_list = []
count = 1


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


while True:
    status = 0
    check, frame = video.read()
    now = datetime.now()

    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grey_frame_gau = cv2.GaussianBlur(grey_frame, (15, 15), 0)
    # cv2.imshow("My Video", grey_frame_gau)

    if first_frame is None:
        first_frame = grey_frame_gau

    delta_frame = cv2.absdiff(first_frame, grey_frame_gau)
    # cv2.imshow("My Video", delta_frame)

    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    # cv2.imshow("My Video", dil_frame)

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 10000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if rectangle.any:
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]
    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(target=send_email,args=(image_with_object,))
        email_thread.daemon = True
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()


    cv2.putText(img=frame, text=now.strftime("%A"), org=(30, 80),
                fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(255, 255, 255),
                thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(img=frame, text=now.strftime("%H:%M:%S"), org=(30, 140),
                fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=3, color=(255, 0, 0),
                thickness=2, lineType=cv2.LINE_AA)
    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)

    if key == ord("q"):
        break

video.release()
clean_thread.start()