# -*- coding: utf-8 -*-
import cv2
import numpy as np
import glob
import os

# === 1. 리프로젝션 에러 계산 함수 ===
def compute_reprojection_errors(objpoints, imgpoints, rvecs, tvecs, K, D):
    total_error = 0
    per_view_errors = []

    for i in range(len(objpoints)):
        projected, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], K, D)
        projected = projected.reshape(-1, 2)
        imgp = imgpoints[i].reshape(-1, 2).astype(np.float32)

        error = cv2.norm(imgp, projected, cv2.NORM_L2) / len(projected)
        per_view_errors.append(error)
        total_error += error

    mean_error = total_error / len(objpoints)
    return per_view_errors, mean_error

# === 2. 캘리브레이션 포인트 불러오기 ===
data = np.load("chessboard_points.npz", allow_pickle=True)
obj_raw = data["objpoints"]
img_raw = data["imgpoints"]
image_shape = tuple(data["image_shape"])[::-1]  # (height, width)

# === 3. 포인트 변환 ===
objpoints = [np.array(o, dtype=np.float32).reshape(-1, 3) for o in obj_raw]
imgpoints = [np.array(i, dtype=np.float32).reshape(-1, 2) for i in img_raw]

# === 4. 일반 카메라 보정 ===
ret, K, D, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, image_shape, None, None
)
print(f"? 일반 보정 RMS: {ret:.4f}")
print("K:\n", K)
print("D:\n", D)

# === 5. 리프로젝션 에러 계산 ===
errors, mean_error = compute_reprojection_errors(objpoints, imgpoints, rvecs, tvecs, K, D)
print(f"? 평균 리프로젝션 에러: {mean_error:.4f}")

# === 6. 보정 파라미터 저장 ===
np.savez("calibration_data_standard.npz", K=K, D=D)
print("? calibration_data_standard.npz 저장 완료")

# === 7. 샘플 이미지 불러오기 ===
valid_images = sorted(glob.glob("./image/*.jpg"))
if not valid_images:
    print("?? valid_images 폴더에 이미지가 없습니다.")
    exit()

sample_img = cv2.imread(valid_images[5])  # 원하는 인덱스로 변경
if sample_img is None:
    print("? 샘플 이미지 로딩 실패")
    exit()

h, w = sample_img.shape[:2]
print("? 샘플 이미지 shape:", sample_img.shape)
print("? 샘플 이미지 평균 밝기:", np.mean(sample_img))

# === 8. 시야 조절 + 중심 복원 ===
alpha = 0.0
new_K, roi = cv2.getOptimalNewCameraMatrix(K, D, (w, h), alpha=alpha, newImgSize=(w, h))

# 중심 복원 (cx, cy)
new_K[0, 2] = K[0, 2]
new_K[1, 2] = K[1, 2]
print("? new_K (중심 복원됨):\n", new_K)

# === 9. 왜곡 제거 ===
undistorted = cv2.undistort(sample_img, K, D, None, new_K)

# === 10. ROI로 crop ===
x, y, crop_w, crop_h = roi
undistorted_cropped = undistorted[y:y+crop_h, x:x+crop_w]
print(f"? Crop 영역: x={x}, y={y}, w={crop_w}, h={crop_h}")

# === 11. 저장 ===
cv2.imwrite("undistorted_final.jpg", undistorted)
cv2.imwrite("undistorted_cropped.jpg", undistorted_cropped)
print("? 보정 이미지 저장 완료: undistorted_final.jpg, undistorted_cropped.jpg")
