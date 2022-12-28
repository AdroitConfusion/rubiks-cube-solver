import cv2
import numpy as np
import scipy.spatial as sp

def checkCentroid(centroids, x, y):
    for cubie in centroids:
        if cubie[0] - x < 30 and cubie[1] - y < 30:
            return False
    return True

cap = cv2.VideoCapture(0)

print("Cap opened: " + str(cap.isOpened()))

while (cap.isOpened()):
    ret, img = cap.read()

    if ret:
        #Convert image to 8-bit and convert to grayscale
        img = np.uint8(img)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  

        # Open and close to remove noise
        open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
        close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))

        img_gray = cv2.morphologyEx(img_gray, cv2.MORPH_OPEN, open_kernel, iterations=1)
        img_gray = cv2.morphologyEx(img_gray, cv2.MORPH_CLOSE, close_kernel, iterations=1)

        # # Blur then canny edge detection
        blurred = cv2.GaussianBlur(img_gray, (17, 17), 0)
        canny = cv2.Canny(blurred, 15, 30)

        # #Dilate to make lines more prominent
        kernel = np.ones((3,3), np.uint8)
        thresh = cv2.dilate(canny, kernel, iterations=2)

        # # Find contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        edges = img
        cv2.drawContours(edges,contours,0,(0,255,0),5)

        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        b_l = 30
        w = int(img.shape[1] / 2) - b_l
        h = int(img.shape[0] / 2) - b_l

        # colors = {
        #       'white': [[180, 18, 255], [0, 0, 231]],
        #       'red1': [[180, 255, 255], [159, 50, 70]],
        #       'red2': [[9, 255, 255], [0, 50, 70]],
        #       'green': [[89, 255, 255], [36, 50, 70]],
        #       'blue': [[128, 255, 255], [90, 50, 70]],
        #       'yellow': [[35, 255, 255], [25, 50, 70]],
        #       'orange': [[24, 255, 255], [10, 50, 70]]}

        # colors = {
        #     # "red": (255, 0, 0),
        #     # "green": (0, 255, 0),
        #     # "blue": (0, 0, 255),
        #     # "white": (255, 255, 255),
        #     # "orange": (250, 128, 0),
        #     # "yellow": (255, 255, 0)
        #     "red": (108, 195, 183),
        #     "green": (90, 87, 163),
        #     "blue": (75, 156, 70),
        #     "white": (216, 137, 127),
        #     "orange": (149, 190, 197),
        #     "yellow": (209, 124, 211)
        # }
        colors = {
            "white": [[125, 120], [140, 138]],
            "yellow": [[100, 170], [140, 215]],
            "blue": [[20, 150], [50, 175]],
            "green": [[80, 130], [100, 150]],
            "red": [[180, 165], [210, 185]],
            "orange": [[150, 150], [179, 170]],
        }
        
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        color_vals = np.array(list(colors.values()))
        color_names = np.array(list(colors.keys()))

        colors_tree = sp.KDTree(color_vals)

        crop_img = img.copy()[h : h + 2 * b_l, w : w + 2 * b_l]
        avg_color_per_row = np.average(crop_img, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)

        img = cv2.rectangle(img, (w, h), (w + 2 * b_l, h + 2 * b_l), (0,255,0), 5)

        for color, (low, high) in colors.items():
            low_np = np.array(low)
            high_np = np.array(high)
            # if (low[0] <= )
                
            # mask = cv2.inRange(crop_img, low_np, high_np)

            # if np.sum(mask) > 0:
            #     print(color + " found!")

        # avg_color_per_row = np.average(crop_img, axis=0)
        # avg_color = np.average(avg_color_per_row, axis=0)
        # _, idx = colors_tree.query((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
        
        print(color_names[idx] + " found!")

        cv2.imshow("Image", img)
        cv2.imshow("Mask", crop_img)

        # Define color lower and upper limits
        # cubie_colors = []
        # centroids = []
        

        # # Calculate area and perimeter approximation for each closed contour
        # for cont in contours:
        #     perim = cv2.arcLength(cont, True)
        #     # epsilon = 0.01 * perim
        #     # appr = cv2.approxPolyDP(cont, epsilon, True)
        #     area = cv2.contourArea(cont)
        #     area_from_perim = (perim / 4) * (perim / 4)
        #     if area < 4000 and area > 1000 and abs(area_from_perim - area) < 100:
        #         (x, y, w, h) = cv2.boundingRect(cont)
        #         ratio = w / h
        #         M = cv2.moments(cont)
        #         cX = int(M["m10"] / M["m00"])
        #         cY = int(M["m01"] / M["m00"])
        #         # Create bounding rectangle if cubie detected
        #         if ratio > 0.9 and ratio < 1.1 and checkCentroid(centroids, x, y):
        #             rect = cv2.minAreaRect(cont)
        #             box = cv2.boxPoints(rect)
        #             box = np.uint0(box)

        #             cv2.drawContours(img,[box],0,(0,255,0),5)
        #             cv2.circle(img, (cX, cY), 7, (255, 255, 255), -1)

        #             cubie_colors.append((x, y, w, h))
        #             centroids.append((cX, cY))
        
        # if len(cubie_colors) > 9:
        #     print("Greater than 9")

        # #Color detection
        # cubie_img = img
        # if len(cubie_colors) == 1:
        #     for cubie in cubie_colors:
        #         cubie_img = img[cubie[1] : cubie[1] + cubie[3], cubie[0] : cubie[0] + cubie[2]]
        #         # for color, (low, high) in colors_limits:
                    
        # thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)
        # concat = np.concatenate((img, thresh), axis=0)
        # cv2.imshow("Image", concat)
        

        # open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
        # close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))

        # for color, (low, high) in colors.items():
        #     color_mask = cv2.inRange(hsv_img, low, high)
        #     color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
        #     color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, close_kernel, iterations=1)
        #     ret,thresh = cv2.threshold(color_mask,127,255,0)
        #     contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        #     areas = [cv2.contourArea(c) for c in contours]

        #     color_mask = cv2.merge([color_mask, color_mask, color_mask])
        #     mask = cv2.bitwise_or(mask, color_mask)

        # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        # hsv = cv2.bitwise_and(hsv_img, hsv_img, mask=mask)

        if (cv2.waitKey(1) == ord('q')):
            break 
    else:
        break

cap.release()
cv2.destroyAllWindows()



