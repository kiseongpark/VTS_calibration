## fisheyelens camera calibration


### 1. 체커보드 인식

새로운 카메라를 통해 이미지 100장 정도를 촬영하고(takephoto_with_pi.py활용), 그 중 20장의 이미지를 선별하여 사용하였다.

[image.zip](attachment:d5f44757-cf2c-4d10-b9b4-b0a960efbf28:image.zip)

최대한 비슷한 필드에 체커보드가 오는 이미지 몇장을 선별하였다. 위 폴더가 선별된 이미지이다.

### 2. 이미지 필터링(코너 인식확인)후, npz파일 형성

결과

필터링 알고리즘 하나만 적용한 코드를 돌렸더니, 중요한 가장자리 부분에 체커 보드가 있는 사진은 코너가 인식되지 않는 현상이 나왔다. 그래서 예전에 썻던, 인식 알고리즘을 최대한 많이 써서, 사진 속 대부분의 체커보드의 코너가 잘 인식되도록 하였다. 나중 결과를 보면 오히려 rms가 더 감소한 것을 확인할 수 있다. 

<img width="750" height="350" alt="Image" src="https://github.com/user-attachments/assets/dab7f88e-15b6-410b-8113-bad714ac7ae8" />

- 결과로 나온 npz 파일

[chessboard_points.npz](attachment:62f80aea-4613-4926-b6c1-97952b153d94:chessboard_points.npz)

### 3. 캘리브레이션 및 이미지 보정

결과

<img width="800" height="350" alt="Image" src="https://github.com/user-attachments/assets/1c389e2b-9073-4f31-9a01-dc18d8e39682" />

- 파라미터
    
    K:
    [[9.08248874e+02 0.00000000e+00 1.19471816e+03]
    [0.00000000e+00 8.99015826e+02 1.03228973e+03]
    [0.00000000e+00 0.00000000e+00 1.00000000e+00]]
    D:
    [[-0.22773718  0.03887236  0.0085078   0.00710741 -0.00269294]]
    
    new_K (중심 복원됨):
    [[9.08248874e+02 0.00000000e+00 1.19471816e+03]
    [0.00000000e+00 8.99015826e+02 1.03228973e+03]
    [0.00000000e+00 0.00000000e+00 1.00000000e+00]]
    ? Crop 영역: x=0, y=0, w=2591, h=2099
    

rms는 5.6562 로 준수한 수치가 나왔고, 캘리브레이션 파라미터도 호모그래피를 다시 해봐야 알겠지만 잘 나온 것을 확인할 수 있다.

- 이미지

  
<img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/7d73aaaa-077a-4f07-a7ad-6b21595a4b36" />  <img width="400" height="300" alt="Image" src="https://github.com/user-attachments/assets/fa2f1ab4-ac3a-4b94-9911-e20d993d99bd" />

시야가 좀 좁아지긴 했어도, 예전에 문제였던 가장자리 부분의 왜곡이 어느정도 보정이 된 것을 확인 할 수 있다. 시야를 넓히는 방안도 생각하면 좋겠지만, 빠른 프로젝트 진행을 위해 지금부턴 여기서 나온 파라미터를 가지고, 호모그래피, 측위 과정을 쭉 파볼 예정이다.
