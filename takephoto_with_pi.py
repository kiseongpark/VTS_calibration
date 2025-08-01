import cv2
import numpy as np
import os
import time
from picamera2 import Picamera2

# ���� ���� ����
SAVE_DIR = "./calib_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# üĿ���� ���� �ڳ� ����
CHECKERBOARD = (9, 10)

# Picamera2 ����
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (2592, 2100), "format": "RGB888"})
picam2.configure(config)
picam2.start()
time.sleep(2)

idx = 0

print("> üĿ���带 �پ��� ������ �����ְ�, Enter Ű�� ������ �Կ� �õ��մϴ�. (����: Ctrl+C)")

try:
    while True:
        input(f"[{idx}] ĸó�Ϸ��� Enter > ")

        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

        if ret:
            # �����ȼ� ����
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)

            # �ڳ� �� Ȯ��
            if corners2.shape[0] == CHECKERBOARD[0] * CHECKERBOARD[1]:
                vis = cv2.drawChessboardCorners(frame.copy(), CHECKERBOARD, corners2, ret)
                filename = os.path.join(SAVE_DIR, f"checkerboard_{idx:02d}.jpg")
                cv2.imwrite(filename, vis)
                print(f"? �����: {filename}")
                idx += 1
            else:
                print("�Ϻ� �ڳʸ� �νĵ� - �������� ����")
        else:
            print("üĿ���� �ν� ���� - �ٽ� �õ��ϼ���")

        if idx >= 25:
            print("25�� ���� �Ϸ�!")
            break

except KeyboardInterrupt:
    print("\n����ڿ� ���� �ߴܵ�")

picam2.stop()


