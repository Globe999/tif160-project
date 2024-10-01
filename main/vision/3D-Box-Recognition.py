import cv2
import numpy as np

image_path = r'D:\Hiomanoid Robots\Project\final\main\vision\test1.jpg'
frame = cv2.imread(image_path)
if frame is None:
    print("Error: Could not open image.")
else:
    # Apply median filter to reduce noise
    median_frame = cv2.GaussianBlur(frame, (3, 3), 0)

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(median_frame, cv2.COLOR_BGR2HSV)

    # Define color ranges for white, red, blue, and green
    color_ranges = {
        'white': ((0, 0, 200), (180, 25, 255)),
        'red': ((0, 100, 80), (10, 255, 255)),
        #'red2': ((170, 120, 70), (180, 255, 255)),
        'blue': ((100, 150, 70), (140, 255, 255)),
        'green': ((40, 50, 50), (90, 255, 255))
    }

    mask_bright = cv2.inRange(hsv, (0, 0, 150), (180, 255, 255))


    # Create masks for each color
    masks = {}
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, lower, upper)
        if color != 'white':  # Apply brightness filter to all non-white
            mask = cv2.bitwise_and(mask, mask_bright)
        masks[color] = mask
      #  Combine red masks for full red detection
    #masks['red'] = cv2.bitwise_or(masks['red1'], masks['red2'])

    # Sharpen red mask specifically
    kernel_sharpening = np.array([[-1, -1, -1], 
                                [-1, 9, -1], 
                                [-1, -1, -1]])

    masks['red'] = cv2.filter2D(masks['red'], -1, kernel_sharpening)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))


    # Define kernels for morphological operations
    # kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))

    # Reduce noise with morphological operations
    for color, mask in masks.items():
        cv2.imshow(f"{color} Mask", mask)

        # Opening to remove small noise
        masks[color] = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        # Closing to fill small holes in the object
        masks[color] = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        # Visualize each color mask
        cv2.imshow(f"{color} Mask", masks[color])

    for color, mask in masks.items():
        cv2.imshow(f"{color} Mask", mask)  # Visualize each mask

    # Combine all masks to create a foreground mask
    combined_mask = np.zeros_like(masks['white'])
    for color in ['white', 'red', 'blue', 'green']:
        combined_mask = cv2.bitwise_or(combined_mask, masks[color])

        cv2.imshow("Combined Mask", combined_mask)  # Add this after combining all color masks


    # Apply the mask to the frame to remove the background
    foreground = cv2.bitwise_and(frame, frame, mask=combined_mask)

    # Apply Canny edge detection to the foreground
    edges = cv2.Canny(foreground, 100, 200)
    cv2.imshow('Edges', edges)

    # Find contours for each color mask
    contours_data = {}
    for color, mask in masks.items():
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_data[color] = contours

    # Process and draw contours
    for color, contours in contours_data.items():
        for contour in contours:
            if cv2.contourArea(contour) > 2000:  
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(foreground, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(foreground, color, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the result
    cv2.imshow("Detected Shapes", foreground)

    if cv2.waitKey(0) & 0xFF == ord('q'):
        pass

cv2.destroyAllWindows()
