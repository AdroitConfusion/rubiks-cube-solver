import cv2
import numpy as np

DS_SQUARE_SIDE_RATIO = 1.5
DS_MORPH_KERNEL_SIZE = 5
DS_MORPH_ITERATIONS = 2
DS_MIN_SQUARE_LENGTH_RATIO = 0.08
DS_MIN_AREA_RATIO = 0.7
DS_MIN_SQUARE_SIZE = 0.10 # Times the width of image
DS_MAX_SQUARE_SIZE = 0.25

def create_color_masks(hsv_frame):
    # Define HSV color ranges for the six Rubik's Cube colors
    # Note: These values are approximate and may need adjustment
    # color_ranges = {
    #     "red_one": (np.array([140, 100, 10]), np.array([179, 255, 255])),
    #     "red_two": (np.array([0, 100, 10]), np.array([3, 255, 255])),
    #     "blue": (np.array([110, 50, 50]), np.array([130, 255, 255])),
    #     "green": (np.array([50, 150, 10]), np.array([99, 255, 255])),
    #     "yellow": (np.array([25, 70, 120]), np.array([35, 255, 255])),
    #     "white": (np.array([0, 0, 200]), np.array([180, 55, 255])),
    #     "orange": (np.array([10, 100, 120]), np.array([25, 255, 255]))
    # }
    color_ranges = {
        "red_one": (np.array([170,110,110]), np.array([180, 255, 255])),
        "red_two": (np.array([0, 110, 110]), np.array([10,255,155])),
        "blue": (np.array([95,60,70]), np.array([120,255,220])),
        "green": (np.array([40,100,10]), np.array([90,255,255])),
        "yellow": (np.array([11, 80,150]), np.array([40,255,255])),
        "white": (np.array([0,  0, 120]), np.array([255, 50,255])),
        "orange": (np.array([10, 100, 120]), np.array([25, 255, 255]))
    }

    masks = {}
    for color, (lower, upper) in color_ranges.items():
        masks[color] = cv2.inRange(hsv_frame, lower, upper)
    return masks

def detect_cubies(frame):

    def remove_bad_contours(contours):
        new_contours = []
        
        for contour in contours:
            bound_rect = cv2.minAreaRect(contour)
            length, width = float(bound_rect[1][0]), float(bound_rect[1][1])
            perimeter = cv2.arcLength(contour, True)
            area = cv2.contourArea(contour)
            if (length != 0 and width != 0):
                if ((cv2.norm(((perimeter / 4) * (perimeter / 4)) - area) < 500) and
                    (max((length / width, width / length)) > DS_SQUARE_SIDE_RATIO) and
                    (cv2.contourArea(contour) / (length * width) < DS_MIN_AREA_RATIO) and
                    (not DS_MAX_SQUARE_SIZE * frame.shape[0] > max((length, width)) > DS_MIN_SQUARE_SIZE * frame.shape[0])):
                    new_contours.append(contour)
        return new_contours

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    # frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for each color
    masks = create_color_masks(hsv)

    # Process each color mask
    for color, mask in masks.items():
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # new_contours = remove_bad_contours(contours)

        # for contour in new_contours:
        #     x, y, w, h = cv2.boundingRect(contour)
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            # epsilon = 0.05 * perimeter
            # approx = cv2.approxPolyDP(contour, epsilon, True)
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Adjust these values as needed
                if cv2.norm(((perimeter / 4) * (perimeter / 4)) - area) < 500:  # Check for square/rectangle (4 sides)
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame

def main():
    cap = cv2.VideoCapture(0)
    # if cap.isOpened():
    #     cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
    #     cap.set(cv2.CAP_PROP_EXPOSURE, -4.0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        processed_frame = detect_cubies(frame)
        cv2.imshow("Frame", processed_frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

# import cv2
# import numpy as np
# from imutils import contours

# def detect_face(frame):

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

#     gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
#     gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

#     gray = cv2.adaptiveThreshold(gray, 20, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 0)

#     contours, hierarchy = cv2.findContours(gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)


#     i = 0
#     contour_id = 0
#     count = 0
#     blob_colors = []
#     for contour in contours:
#         area = cv2.contourArea(contour)

#         # Filter out small or too large contours
#         if 1000 < area < 3000:
#             # Approximate contour to a polygon
#             perimeter = cv2.arcLength(contour, True)
#             approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)

#             # Check if the approximated contour has 4 sides (indicating a square or rectangle)
#             if len(approx) == 4:
#                 x, y, w, h = cv2.boundingRect(contour)
#                 # Draw bounding rectangle
#                 cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)

#     return gray

# def main():
#     # Open camera
#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#     _, frame = cap.read()
#     frame = cv2.flip(frame, 1)

#     while True:
#         _, frame = cap.read()
#         frame = cv2.flip(frame, 1)
#         processed_frame = detect_face(frame)
#         cv2.imshow("Frame", processed_frame)
#         if cv2.waitKey(1) == ord('q'):
#             break


#     # Close camera
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()