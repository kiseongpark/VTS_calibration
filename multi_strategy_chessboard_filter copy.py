# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
import glob

CHECKERBOARD = (9, 10)  # 내부 코너 수
square_size = 0.09  # 단위: m

INPUT_DIR = './image'
OUTPUT_DIR = './valid_images'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 3D object point template
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
objp *= square_size

objpoints = []  # 3D 실제 좌표
imgpoints = []  # 2D 이미지 코너
_img_shape = None

images = glob.glob(os.path.join(INPUT_DIR, '*.jpg'))
valid_count = 0

def try_all_methods(img, gray):
    h, w = gray.shape

    # 1. 기본 탐지
    ret1, corners1 = cv2.findChessboardCorners(
        gray, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    if ret1:
        return True, corners1, '기본'

    # 2. Symmetric Board 방식
    try:
        ret2, corners2 = cv2.findChessboardCornersSB(gray, CHECKERBOARD)
        if ret2:
            return True, corners2, 'SB'
    except:
        pass

    # 3. 히스토그램 평활화 + 블러
    gray_eq = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray_eq, (5, 5), 0)
    ret3, corners3 = cv2.findChessboardCorners(
        blurred, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    if ret3:
        return True, corners3, 'equalize + blur'

    # 4. 적응형 이진화
    thresh = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    ret4, corners4 = cv2.findChessboardCorners(
        thresh, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    if ret4:
        return True, corners4, 'adaptive threshold'

    # 5. 중앙 사각형 크롭
    crop = gray[h//4:h*3//4, w//4:w*3//4]
    ret5, corners5 = cv2.findChessboardCorners(
        crop, CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )
    if ret5:
        corners5 += np.array([[[w//4, h//4]]], dtype=np.float32)
        return True, corners5, '중앙 크롭'

    return False, None, '실패'

# ------------- MAIN LOOP -------------
for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"⚠️ 이미지 로드 실패: {fname}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if _img_shape is None:
        _img_shape = gray.shape[::-1]  # (width, height)

    success, corners, method = try_all_methods(img, gray)

    if success:
        cv2.cornerSubPix(
            gray, corners, (3, 3), (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
        )

        basename = os.path.basename(fname)
        vis = cv2.drawChessboardCorners(img.copy(), CHECKERBOARD, corners, True)
        cv2.imwrite(os.path.join(OUTPUT_DIR, basename), vis)

        objpoints.append(objp.copy())
        imgpoints.append(corners)

        valid_count += 1
        print(f"✅ {basename} - 성공 ({method})")
    else:
        print(f"❌ {os.path.basename(fname)} - 실패")

# npz 저장
if valid_count >= 5:
    np.savez(
        'chessboard_points.npz',
        objpoints=np.array(objpoints, dtype=object),
        imgpoints=np.array(imgpoints, dtype=object),
        image_shape=np.array(_img_shape)
    )
    print(f"\n📁 npz 저장 완료: chessboard_points.npz")
else:
    print("\n🚫 유효한 이미지가 부족합니다. 최소 5장이 필요합니다.")

print(f"📊 최종 유효 이미지 수: {valid_count} / {len(images)}")
