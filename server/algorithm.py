import cv2
import numpy as np
import pytesseract
import base64
from io import BytesIO

import re
# def extract_info(text):
#     # Your regex extraction logic here
#     college_name_pattern = re.compile(r'(Indian Institute of Technology|Ahalia Integrated Campus).*')
#     college_name_match = college_name_pattern.search(text)
#     college_name = college_name_match.group() if college_name_match else None

#     student_info_pattern = re.compile(r'([A-Z]+)\. (B\.Tech [A-Za-z ]+)\) (\d+) Valid')
#     student_info_match = student_info_pattern.search(text)
#     student_name = student_info_match.group(1) if student_info_match else None
#     degree = student_info_match.group(2) if student_info_match else None
#     roll_number = student_info_match.group(3) if student_info_match else None

#     return {
#         "college_name": college_name,
#         "student_name": student_name,
#         "degree": degree,
#         "roll_number": roll_number
#     }

def algo(image):

    # image = cv2.imread(img)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(image,(5,5),0)
    canny = cv2.Canny(blur, 100, 200, 5)
    img_cont = image.copy()
    contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_cont, contours, -1, (0,255,0), 3)
    largest_contour = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(largest_contour,True)
    biggest = cv2.approxPolyDP(largest_contour, 0.02*peri, True)

    def reorder(myPoints):
        myPoints = myPoints.reshape((4, 2))
        myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
        add = myPoints.sum(1)
        myPointsNew[0] = myPoints[np.argmin(add)]
        myPointsNew[3] =myPoints[np.argmax(add)]
        diff = np.diff(myPoints, axis=1)
        myPointsNew[1] =myPoints[np.argmin(diff)]
        myPointsNew[2] = myPoints[np.argmax(diff)]
        return myPointsNew
    biggest=reorder(biggest)
    old_pts = np.float32([[biggest[0][0][0], biggest[0][0][1]], [biggest[1][0][0], biggest[1][0][1]], [biggest[2][0][0],biggest[2][0][1]], [biggest[3][0][0],biggest[3][0][1]]])
    maxH = old_pts[0][1]
    maxW = old_pts[0][0]
    minH = old_pts[0][1]
    minW = old_pts[0][0]
    for i in range(len(old_pts)):
        curr = old_pts[i]
        if maxH < old_pts[i][1]:
            maxH = old_pts[i][1]
        if minH > old_pts[i][1]:
            minH = old_pts[i][1]
        if maxW < old_pts[i][0]:
            maxW = old_pts[i][0]
        if minW > old_pts[i][0]:
            minW = old_pts[i][0]
    width = int(maxW-minW)
    height = int(maxH-minH)
    new_pts = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    old_pts = np.float32([[biggest[0][0][0], biggest[0][0][1]], [biggest[1][0][0], biggest[1][0][1]], [biggest[2][0][0],biggest[2][0][1]], [biggest[3][0][0],biggest[3][0][1]]])
    matrix = cv2.getPerspectiveTransform(old_pts, new_pts)
    result = cv2.warpPerspective(image, matrix, (width, height))
    toSend = []
    toSend.append(result)
    clahe = cv2.createCLAHE(clipLimit=1, tileGridSize=(8, 8))
    result = clahe.apply(result)
    toSend.append(result)
    alpha = 1.6
    adjusted_image = cv2.convertScaleAbs(result, alpha=alpha, beta=2)
    kernel_sharpening = np.array([[-1, -1, -1],
                                [-1, 9, -1],
                                [-1, -1, -1]])
    result = cv2.filter2D(adjusted_image, -1, kernel_sharpening)
    toSend.append(result)
    extracted_text = pytesseract.image_to_string(result)
    extracted_text = extracted_text.splitlines()
    extracted_text = [item for item in extracted_text if item.strip()]

    print(extracted_text)
    imgs = []
    for i in toSend:
        _, img_encoded = cv2.imencode('.png', i)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        imgs.append(img_base64)
    cv2.destroyAllWindows()
    # extracted_text = extract_info(extracted_text)
    keys = ['Institution','Address','Affiliation','Website','ContactName','Degree','ID','ValidUntil','Issuer','Signature']
    info_dict = {keys[i]: extracted_text[i] for i in range(len(keys))}

    return [info_dict,imgs]


