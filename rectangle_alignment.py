import cv2
import numpy as np
import math


#Function returns dictionary of information of line and rectangle contours

def getContours(img, imgContour, contourType):
    if contourType == "line":
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
                                del lineContours[j]
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
original_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

blankImg = cv2.imread(r'C:\Users\ajna\Downloads\shishir\blank.jpg')
imgContour = img.copy()

imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

imgCanny = cv2.Canny(imgGray, 20, 23)

lineContours = getContours(imgCanny, imgContour, "line")
rectangleContours = getContours(imgCanny, imgContour, "rectangle")

rotatedImgContour = img.copy()

for rectContour in rectangleContours:
    cv2.rectangle(rotatedImgContour, (rectContour['BBpoints'][0], rectContour['BBpoints'][1]), (rectContour['BBpoints'][2], rectContour['BBpoints'][3]), (219, 67, 119), 3)
    cv2.rectangle(blankImg, (rectContour['BBpoints'][0], rectContour['BBpoints'][1]),
                  (rectContour['BBpoints'][2], rectContour['BBpoints'][3]), (0, 0, 0), 2)


for lineContour in lineContours:
    if lineContour['size'][0] > lineContour['size'][1]:
        lineContour['length'] = lineContour['size'][0]
        lineContour['width'] = lineContour['size'][1]
    else:
        lineContour['length'] = lineContour['size'][1]
        lineContour['width'] = lineContour['size'][0]



def findPerpendicularDist(x1, y1, x2, y2, x, y):
    A = y1 - y2
    B = x2 - x1
    C = x1 * y2 - x2 * y1
    pd = abs((A * x + B * y + C)) / (math.sqrt(A * A + B * B))
    return pd


for i in range(0, len(lineContours)):
    (linePoint_x, linePoint_y) = lineContours[i]['box'][3]
    (rect_x1, rect_y1) = rectangleContours[i]['box'][3]
    (rect_x2, rect_y2) = rectangleContours[i]['box'][0]
    (rect_x3, rect_y3) = rectangleContours[i]['box'][2]

    pd1 = findPerpendicularDist(rect_x1, rect_y1, rect_x2, rect_y2, linePoint_x, linePoint_y)
    pd2 = findPerpendicularDist(rect_x1, rect_y1, rect_x3, rect_y3, linePoint_x, linePoint_y)
    pd1 = round(pd1, 0)
    pd2 = round(pd2, 0)

    box = rectangleContours[i]['box']
    x_start = box[3][0]
    y_start = box[3][1]
    length = round(lineContours[i]['length'], 0)
    
    a = box[0][0]
    b = box[0][1]
    c = box[2][0]
    d = box[2][1]
    d1 = math.sqrt((x_start - a) ** 2 + (y_start - b) ** 2)
    d2 = math.sqrt((x_start - c) ** 2 + (y_start - d) ** 2)
    if d1 >= d2:
        x_start = x_start - pd2
        x_end = x_start - length
        y_start = y_start - pd1
        y_end = y_start
    else:
        x_start = x_start + pd1
        x_end = x_start + length
        y_start = y_start - pd2
        y_end = y_start
    

    cv2.rectangle(rotatedImgContour, (int(x_start), int(y_start)), (int(x_end), int(y_end)), (219, 67, 119), 2)

    cv2.putText(rotatedImgContour, "Rectangle Alligned Image", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

    cv2.rectangle(blankImg, (int(x_start), int(y_start)), (int(x_end), int(y_end)), (0, 0, 0), 2)
    cv2.putText(blankImg, "", (120, 28), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Rectangular Allignment Window", blankImg)


cv2.waitKey(0)

print("Success!!!")