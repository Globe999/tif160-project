
import numpy as np
import cv2


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cap.release()
    cv2.destroyAllWindows()


    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred_image, 50, 150)



    # Define range for red color in HSV
    lower_red = (0, 120, 70)
    upper_red = (10, 255, 255)
    mask_red = cv2.inRange(hsv_image, lower_red, upper_red)
    red_detected = cv2.bitwise_and(frame, frame, mask=mask_red)



    # Define range for blue color in HSV
    lower_blue = (110, 50, 50)
    upper_blue = (130, 255, 255)
    mask_blue = cv2.inRange(hsv_image, lower_blue, upper_blue)
    blue_detected = cv2.bitwise_and(frame, frame, mask=mask_blue)

    # Define range for green color in HSV
    lower_green = (50, 50, 50)
    upper_green = (70, 255, 255)
    mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
    green_detected = cv2.bitwise_and(frame, frame, mask=mask_green)

    # Define range for white color in HSV
    lower_white = (0, 0, 200)  
    upper_white = (180, 25, 255)
    mask_white = cv2.inRange(hsv_image, lower_white, upper_white)
    white_detected = cv2.bitwise_and(frame, frame, mask=mask_white)




        # Combine all detected colors into one image
    combined_detected = cv2.addWeighted(red_detected, 1, blue_detected, 1, 0)
    combined_detected = cv2.addWeighted(combined_detected, 1, green_detected, 1, 0)
    combined_detected = cv2.addWeighted(combined_detected, 1, white_detected, 1, 0)

te
        