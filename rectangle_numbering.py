import cv2
import numpy as np
import math

def empty(a):
    pass

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                                None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver


def getContours(img, imgContour, contourType):
    if contourType == "line":
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))

    rectangleContours = []
    lineContours = []
    for i in range(0, len(contours)):
        peri = cv2.arcLength(contours[i], True)

        approx = cv2.approxPolyDP(contours[i], 0.02 * peri, True)
    
        area = cv2.contourArea(contours[i])

        rect = cv2.minAreaRect(contours[i])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        center = rect[0]
        size = rect[1]
        angle = rect[2]
      
        if contourType == "line":
            if area >= 5:
                if size[0] < 20 or size[1] < 20:
                    cv2.drawContours(imgContour, [box], 0, (0, 0, 255), 2)
                    print(f"Contour {i} may be line.")
                    line_dict = {'contour': i,
                                 'center': center,
                                 'size': size,
                                 'angle': angle,
                                 'area': area,
                                 'box': box}
                    lineContours.append(line_dict)
        else:
            x_start = box[3][0]
            y_start = box[3][1]
            a = box[0][0]
            b = box[0][1]
            c = box[2][0]
            d = box[2][1]
            d1 = math.sqrt((x_start - a) ** 2 + (y_start - b) ** 2)
            d2 = math.sqrt((x_start - c) ** 2 + (y_start - d) ** 2)
            if d1 >= d2:
                x_end = x_start - int(size[0])
                y_end = y_start - int(size[1])
            else:
                x_end = x_start + int(size[1])
                y_end = y_start - int(size[0])

            cv2.drawContours(imgContour, [box], 0, (0, 0, 255), 3)
            rect_dict = {'contour': i,
                         'center': center,
                         'size': size,
                         'angle': angle,
                         'area': area,
                         'box': box,
                         'BBpoints': [x_start, y_start, x_end, y_end]}
            rectangleContours.append(rect_dict)

    if contourType == "line":
        print(len(lineContours))
        similarLineList = []
        while len(lineContours) != 0:
            similarLine = []
            line = lineContours[0]
            similarLine.append(line)
            for j in range(1, len(lineContours)):
                if j < len(lineContours):
                    if abs(line['center'][0] - lineContours[j]['center'][0] < 10 and line['center'][1] -
                           lineContours[j]['center'][1] < 10.0):
                        if abs(line['angle'] - lineContours[j]['angle']) < 1.0:
                            if abs(line['area'] - lineContours[j]['area']) < 175:
                                similarLine.append(lineContours[j])
                                print(f"Contours- {line['contour']} and {lineContours[j]['contour']} are same !!!")
                                del lineContours[j]
                                print(f"Length of lineContours : {len(lineContours)}")
            del lineContours[0]
            similarLineList.extend([similarLine])
        for similarLines in similarLineList:
            if len(similarLines) > 1:
                if similarLines[0]['area'] < similarLines[1]['area']:
                    lineContours.append(similarLines[0])
                else:
                    lineContours.append(similarLines[1])

            else:
                lineContours.append(similarLines[0])
        return lineContours

    else:
        return rectangleContours


img = cv2.imread(r'C:\Users\ajna\Downloads\shishir\5.jpg')
imgContour = img.copy()

imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

imgCanny = cv2.Canny(imgGray, 20, 23)
lineContours = getContours(imgCanny, imgContour, "line")

rectangleContours = getContours(imgCanny, imgContour, "rectangle")
numberedImgContour = img.copy()


sorted_index = []
i = 0
for lineContour in lineContours:
    line_box = lineContour['box']
    cv2.drawContours(numberedImgContour, [line_box], 0, (0, 0, 255), 1)
    if lineContour['size'][0] > lineContour['size'][1]:
        lineContour['length'] = lineContour['size'][0]
        lineContour['width'] = lineContour['size'][1]
    else:
        lineContour['length'] = lineContour['size'][1]
        lineContour['width'] = lineContour['size'][0]
    dict = {'index': i,
            'length': lineContour['length'],
            'width': lineContour['width']}
    sorted_index.append(dict)
    i = i + 1

temp = sorted_index.copy()
sorted_index = sorted(sorted_index, key=lambda d: d['length'])

#numbering the rectangles
for i in range(0, len(sorted_index)):
    index = sorted_index[i]['index']
    length = sorted_index[i]['length']
    x = int(rectangleContours[index]['center'][0])
    y = int(rectangleContours[index]['center'][1])

    cv2.putText(numberedImgContour, f"{i + 1}", (x - 100, y + 100), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0, 255, 0), 2)


    cv2.putText(numberedImgContour, "", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Rectangular Numbering Window", numberedImgContour)

cv2.waitKey(0)

print("Success!!!")