import argparse
import os
import json
from PIL import Image
import glob
import subprocess
import time
from util_funcs import get_3_num

import dlib
import cv2
import numpy as np
import pickle


import logging
from datetime import datetime
import time

def reorient_img(pil_img):
    img_exif = pil_img.getexif()

    if len(img_exif):
        if img_exif[274] == 3:
            pil_img = pil_img.transpose(Image.ROTATE_180)
        elif img_exif[274] == 6:
            pil_img = pil_img.transpose(Image.ROTATE_270)
        elif img_exif[274] == 8:
            pil_img = pil_img.transpose(Image.ROTATE_90)

    return pil_img


start_time = time.time() # 시간측정용

# argument parsing
ap = argparse.ArgumentParser()
ap.add_argument("-k", "--key", default=1, type=str,
                help="input case index")
ap.add_argument("-t", "--type", default="video", type=str,
                help="photo or video")
args = ap.parse_args()

# log 를 남기기 위한 객체 생성
logger = logging.getLogger()
formatter = logging.Formatter(u'line[%(lineno)d] %(pathname)s (%(asctime)s)>>>>>  %(message)s')
logPath = '/home/yona/projects/chameleon_project/log/' + args.key
if not os.path.exists(logPath):
    os.makedirs(logPath)
fileHandler = logging.FileHandler(logPath + '/classifier_'+str(datetime.now())+'.txt') # 현재시간 이름으로 로그 파일을 만듦
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)
logger.info('classifier 시작함')

# get name of directory and file
apiServerPath = "chameleonServer/static/" + args.key
cropDirName = "LQ_faces"
cropPath = apiServerPath + "/" + cropDirName

directory_name = "database/"+args.key # Working directory
target_name = os.listdir(directory_name)[0] # 변환할 파일 이름
target_type = target_name.split('.')[1] # jpg, jpeg, png등을 저장

tmp_dir = directory_name+"/"+"tmp" # 임시 저장소
output_name = args.key+".json" # 결과 json 파일


if args.type == 'video' :
    print('video hasn\'t done')
    ############# undone for video ###############

elif args.type == 'photo' :

    image = cv2.imread(directory_name+'/'+target_name)
    pil_image = Image.open(directory_name+'/'+target_name) # crop을 위해 pil 형태로 열어둠

    h, w, c = image.shape
    os.makedirs(apiServerPath, exist_ok=True)

    maxSize = max(w, h)
    resizeValue = 1024
    scale_down_factor = 1
    scale_up_factor = 1
    if ( maxSize > resizeValue) : # 이미지 크기가 500을 넘어갈 경우, 너비 기준 500으로 이미지 크기 조정
        scale_down_factor = resizeValue / maxSize
        scale_up_factor = maxSize / resizeValue
        image = cv2.resize(image, None, fx=scale_down_factor, fy=scale_down_factor, interpolation= cv2.INTER_LINEAR)

    detect_start_time = time.time() # 시간측정용

    face_detector = dlib.get_frontal_face_detector() # dlib model 이용해 face crop
    detected_faces = face_detector(image, 2)

    logger.info('{} 개 얼굴 감지'.format(len(detected_faces)))
    logger.info("Detect: "+str(time.time() - detect_start_time)+" 소요")
    assert len(detected_faces) > 0, 'No faces detected'

    # 감지된 얼굴이 없을때, result.json에 0을 적고 프로그램 종료
    if (detected_faces == 0) :
        output_json = apiServerPath+'/'+'return1-'+args.key+'.json'
        d = {"data" : []}
        with open (output_json, 'w') as make_file :
            json.dump(d, make_file, ensure_ascii=False, indent='\t')
        exit(0)


    cropped_face_index = 0
    face_list = []

    os.makedirs(cropPath, exist_ok=True)

    for det in detected_faces :
        if isinstance(face_detector, dlib.cnn_face_detection_model_v1):
            rec = det.rect
            print('using CNN model..')
        else:
            rec = det

        width = rec.right() - rec.left()
        height = rec.bottom() - rec.top()

        scaleWidth = width * 0.1
        scaleTop = height * 0.20
        scaleBottom = height * 0.25
        # 얼굴 좌표 저장하기
        top = int(max(0, rec.top() - scaleTop) * scale_up_factor)
        bottom = int(min(rec.bottom() + scaleBottom, image.shape[0]) * scale_up_factor)
        left = int(max(0, rec.left() - scaleWidth) * scale_up_factor)
        right = int(min(rec.right() + scaleWidth, image.shape[1]) * scale_up_factor)
        area = (left, top, right, bottom)
        face_list.append([cropped_face_index, area])

        # 얼굴 크롭해서 저장하기
        cropped_face = pil_image.crop(area)
        cropped_face.save(cropPath+'/'+get_3_num(cropped_face_index)+'.'+target_type, quality=100)

        cropped_face_index += 1

    logger.info('얼굴 인덱스와 위치를 pickle로 저장 완료')
    # 얼굴 인덱스와 위치를 pickle로 저장하기
    with open(apiServerPath+'/rec_list.pickle', 'wb') as f :
        pickle.dump(face_list, f)

    # crop된 결과를 json 파일로 만들기
    output_json = apiServerPath+'/'+'return1-'+args.key+'.json'
    d_list = []
    for i in range (cropped_face_index) :
        d_list.append({"index" : get_3_num(i), "img" : cropPath + "/" +get_3_num(i)+'.'+target_type})
    d = {"data" : d_list}
    with open (output_json, 'w') as make_file :
        json.dump(d, make_file, ensure_ascii=False, indent='\t')

    os.system("cp "+directory_name+'/'+target_name+' '+apiServerPath)
    logger.info('json 파일 작성 완료')

else :
    print("wrong args")
    exit(1)

print('classifier.py 종료\n')
print("총 "+str(time.time() - start_time)+" 소요")

logger.info("총 "+str(time.time() - start_time)+" 소요")

