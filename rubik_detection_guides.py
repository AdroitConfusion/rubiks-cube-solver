import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

color_limits = {
    "white": [[90, 0, 10], [120, 179, 255]],
    "yellow": [[26, 90, 10], [49, 255, 255]],
    "green": [[50, 150, 10], [99, 255, 255]],
    "blue": [[100, 180, 10], [120, 255, 255]],
    "orange": [[4, 100, 10], [25, 255, 255]],
    "red1": [[140, 100, 10], [179, 255, 255]],
    "red2": [[0, 100, 10], [3, 255, 255]],
}

display_colors = {
    "white": (255, 255, 255),
    "yellow": (0, 255, 255),
    "blue": (255, 0, 0),
    "green": (0, 255, 0),
    "red1": (0, 0, 255),
    "red2": (0, 0, 255),
    "orange": (0, 150, 255)
}

display_x = 1050
display_y = 100

display_len = 20
display_dist = display_len

guide_len = 60
guide_dist = 80 + guide_len

#Distance between each display face
face_dist = 3 * display_len

display_face_trans = {
    #Front
    "white": [display_x, display_y],
    #Left
    "blue": [display_x - face_dist, display_y],
    #Up
    "red": [display_x, display_y - face_dist],
    #Down
    "orange": [display_x, display_y + face_dist],
    #Right
    "green": [display_x + face_dist, display_y],
    #Back
    "yellow": [display_x - 2 * face_dist, display_y],
}

face_colors = {
    "red": {},
    "green": {},
    "white": {},
    "orange": {},
    "blue": {},
    "yellow": {}
}

writing_map = {
    "white": "f",
    "blue": "l",
    "red1": "u",
    "red2": "u",
    "orange": "d",
    "green": "r",
    "yellow": "b"
}

display_outline_pos = {}
cubie_guide_pos = {}

def calculatePositions(x, y, len, dist):
    pos = {
        "mid_mid" : [[x, x + len], [y, y + len]],
        "mid_left" : [[x - dist, x + len - dist], [y, y + len]],
        "mid_right" : [[x + dist, x + len + dist], [y, y + len]],

        "top_mid" : [[x, x + len], [y - dist, y + len - dist]],
        "top_left" : [[x - dist, x + len - dist], [y - dist, y + len - dist]],
        "top_right" : [[x + dist, x + len + dist], [y - dist, y + len - dist]],

        "bot_mid" : [[x, x + len], [y + dist, y + len + dist]],
        "bot_left" : [[x - dist, x + len - dist], [y + dist, y + len + dist]],
        "bot_right" : [[x + dist, x + len + dist], [y + dist, y + len + dist]]
    }

    return pos
        
def detectCubies(curr_face_color, cubie_guide_pos, display_outline_pos, face_colors):
    #To returrn
    cubie_colors = {
        "mid_mid" : "",
        "mid_left" : "",
        "mid_right" : "",

        "top_mid" : "",
        "top_left" : "",
        "top_right" : "",

        "bot_mid" : "",
        "bot_left" : "",
        "bot_right" : ""
    }
    save = False
    
    while not save:
        _, frame = cap.read()
        #Flip frame along its y-axis
        #This way, when the user moves the cube to the right, then the cube on the screen will also move to the right
        #More intuitive and natural than the user moving the cube to the right and the cube moving to the left on the screen
        frame = cv2.flip(frame, 1)
        lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        cubie_frames = {}

        #Crop image at each guide position and save it in cubie_frams
        for cubie, pos in cubie_guide_pos.items():
            crop_frame = lab_frame.copy()[pos[1][0] : pos[1][1], pos[0][0] : pos[0][1]]
            cubie_frames[cubie] = crop_frame


        #Find color for each cubie
        for cubie, crop_frame in cubie_frames.items():
            for color, (low, high) in color_limits.items():
                low_np = np.array(low)
                high_np = np.array(high)
                #Create mask of cropped image by thesholding for each color
                mask = cv2.inRange(crop_frame, low_np, high_np)
                #If cubie color is within this range, set display color to this color
                if np.sum(mask == 255) > 300:
                    cubie_colors[cubie] = color
                    break
    
        #Assign cubie colors to appropriate face
        face_colors[curr_face_color] = cubie_colors
    
        #Show guide
        for pos in cubie_guide_pos.values():
            frame = cv2.rectangle(frame, (pos[0][0], pos[1][0]), (pos[0][1], pos[1][1]), (0,255,0), 5)
        
        #Show display outlines
        for face_color, pos in display_outline_pos.items():
            for cubie, (start, end) in pos.items():
                cubies = face_colors[face_color]
                if (len(cubies) != 0):
                    color = cubies[cubie]
                    if color != "":
                        frame = cv2.rectangle(frame, (start[0], end[0]), (start[1], end[1]), display_colors[color], -1)
                frame = cv2.rectangle(frame, (start[0], end[0]), (start[1], end[1]), (0,0,0), 2)
        
        cv2.imshow("Frame", frame)

        if (cv2.waitKey(1) == ord('s')):
            save = True
        elif cv2.waitKey(1) == ord('q'):
            break
    
def writeToFile(face_colors):
    file = open("backend/rubikData", "w")
    for cubies in face_colors.values():
        str = ""
        for color in cubies.values():
            str += writing_map[color]
        file.write(str + "\n")

    file.close()


def main():
    _, frame = cap.read()
    #Middle of screen - half the length
    guide_x = int(frame.shape[1] / 2) - (guide_len // 2)
    guide_y = int(frame.shape[0] / 2) - (guide_len // 2)

    cubie_guide_pos = calculatePositions(guide_x, guide_y, guide_len, guide_dist)

    for face, (x, y) in display_face_trans.items():
        display_outline_pos[face] = calculatePositions(x, y, display_len, display_dist)
        
    for face_color in face_colors.keys():
        detectCubies(face_color, cubie_guide_pos, display_outline_pos, face_colors)
        # if cv2.waitKey(1) == ord('q'):
        #     break


    cap.release()
    cv2.destroyAllWindows()
    writeToFile(face_colors)

if __name__ == "__main__":
    main()