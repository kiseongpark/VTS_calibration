import cv2
import numpy as np
import os
import time
from picamera2 import Picamera2

# 저장 폴더 설정
SAVE_DIR = "./calib_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# 체커보드 내부 코너 개수
CHECKERBOARD = (9, 10)

# Picamera2 설정
picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (2592, 2100), "format": "RGB888"})
picam2.configure(config)
picam2.start()
time.sleep(2)

idx = 0

print("> 체커보드를 다양한 각도로 보여주고, Enter 키를 누르면 촬영 시도합니다. (종료: Ctrl+C)")

try:
    while True:
        input(f"[{idx}] 캡처하려면 Enter > ")

        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

        if ret:
            # 서브픽셀 보정
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)

            # 코너 수 확인
            if corners2.shape[0] == CHECKERBOARD[0] * CHECKERBOARD[1]:
                vis = cv2.drawChessboardCorners(frame.copy(), CHECKERBOARD, corners2, ret)
                filename = os.path.join(SAVE_DIR, f"checkerboard_{idx:02d}.jpg")
                cv2.imwrite(filename, vis)
                print(f"? 저장됨: {filename}")
                idx += 1
            else:
                print("일부 코너만 인식됨 - 저장하지 않음")
        else:
            print("체커보드 인식 실패 - 다시 시도하세요")

        if idx >= 25:
            print("25장 저장 완료!")
            break

except KeyboardInterrupt:
    print("\n사용자에 의해 중단됨")

picam2.stop()


