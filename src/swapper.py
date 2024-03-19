import argparse
import os
import json
import glob
import shutil
import pickle
import util_funcs
from PIL import Image
import subprocess

import logging
from datetime import datetime
import time


start_time = time.time() # 시간측정용

# get case number

ap = argparse.ArgumentParser()

ap.add_argument("-k", "--key", default=1, type=str,
                help="input case index")
ap.add_argument("-t", "--type", default="video", type=str,
                help="choose -> video or photo")
ap.add_argument("-o", "--option", type=str,
                help="to make mosaic, --option mosaic")
ap.add_argument("-m", "--model_path", type=str,
                help="face_swap_model path")

args = ap.parse_args()

# log 를 남기기 위한 객체 생성
logger = logging.getLogger()
formatter = logging.Formatter(u'line[%(lineno)d] %(pathname)s (%(asctime)s)>>>>>  %(message)s')
logPath = '/home/yona/projects/chameleon_project/log/' + args.key
if not os.path.exists(logPath):     os.makedirs(logPath)
fileHandler = logging.FileHandler(logPath + '/swapper_'+str(datetime.now())+'.txt') # 현재시간 이름으로 로그 파일을 만듦
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)
logger.info('swapper 시작함')

logger.info('arugment parsing 완료' )

apiServerPath = "chameleonServer/static/" + args.key
cropDirName = "LQ_faces"
cropPath = apiServerPath + "/" + cropDirName

fakeDirName = "fake_faces"
fakeDirPath = apiServerPath + "/" + fakeDirName

swappedDirName = "swapped_faces"
swappedDirPath = apiServerPath+"/"+swappedDirName

target_json = apiServerPath + "/" + "choice_"+args.key+".json"


file_list = os.listdir(apiServerPath)
src_img = [s for s in file_list if (".jpg" in s or ".png" in s or ".jpeg" in s)]
src_img = src_img[0]
src_img_type = src_img.split(".")[1]

logger.info('source 이미지 로딩 완료' )


# json파일 읽기
with open(target_json, 'r') as f :
    json_object = json.load(f)
# json에서 타겟 얼굴 리스트 읽기
target_face_list = json_object['faces']af

logger.info('choice_json 파일 읽어옴')


if args.type == 'photo' :
    '''
    사진 - 모자이크 기능
    '''
    if args.option == 'mosaic' :

        logger.info('모자이크 시작')

        with open(apiServerPath+"/rec_list.pickle", "rb") as f :
            rec_list = pickle.load(f)

        source_image = Image.open(apiServerPath+'/'+src_img)

        logger.info('좌표 데이터 불러옴')

        print("===================================")
        print("rec_list :::::::" + str(rec_list))
        print("target list ::::::::"+str(target_face_list))

        logger.info('Swap 시작')
        for target_face in target_face_list :
            index, area = rec_list[int(target_face)][0], rec_list[int(target_face)][1]
            width, height = abs(area[2]-area[0]), abs(area[3]-area[1])

            if width <= 0 or height <= 0 :
                continue

            width_mosaic_strength = int(width/50)
            height_mosaic_strength = int(height/50)

            if width_mosaic_strength <= 0 or height_mosaic_strength <= 0 :
                width_mosaic_strength, height_mosaic_strength = 30, 30

            cropped_img = Image.open(cropPath+'/'+util_funcs.get_3_num(index)+'.'+src_img_type)
            cropped_img = cropped_img.resize((width_mosaic_strength, height_mosaic_strength)) # 원본크기 > 확대 > 원본크기 통해 모자이크
            cropped_img = cropped_img.resize((width, height))

            logger.info('모자이크 이미지 크롭 완료')

            # 이미지 합성
            source_image.paste(im=cropped_img, box=(area[0], area[1]))
            print("최종합성 완료!")
            logger.info('모자이크 이미지 합성 완료')

        # 최종 합성 이미지 저장
        source_image.save(apiServerPath+'/'+'return2-'+args.key+'.'+src_img_type)
        print("최종합성 완료!")
        logger.info(' 최종 합성 이미지 저장 완로')
    '''
    사진 - face swap기능
    '''
    else :
        # set fake face
        os.makedirs(fakeDirPath, exist_ok=True)
        os.makedirs(swappedDirPath, exist_ok=True)

        logger.info('target face list ::::' + str(target_face_list))

        # 사용자가 고른 crop된 얼굴을  setting
        for target_index in target_face_list :
            target_file = target_index+'.'+src_img_type # 1.jpg 형태로 바꿈
            shutil.copy(cropPath+'/'+target_file, fakeDirPath)
            shutil.move(fakeDirPath+'/'+target_file, fakeDirPath+"/SRC_"+util_funcs.get_3_num(target_index)+'.'+src_img_type)

        # 각 SRC*.jpg 마다 가짜얼굴 DST_*.jpg를 부여
        util_funcs.set_fake_faces(target_face_list, fakeDirPath)

        logger.info('각 SRC*.jpg 마다 가짜얼굴 DST_*.jpg를 부여')

        # 224크기로 resize
        util_funcs.resize_into_224(fakeDirPath)

        logger.info('resize 완료')

        ### SimSwap 디렉토리 안에서 swap작업
        # fake_faces를 SimsSwap안으로 복사
        logger.info('fake_faces 디렉토리 SimSwap 내로 디렉토리 통채로 복사 시작')

        if (os.path.exists("./SimSwap/"+fakeDirName) == True) : # 이미 SimSwap 디렉토리안에 fake_faces 가 존재하는경우
            shutil.rmtree("./SimSwap/"+fakeDirName) # 삭제

        shutil.copytree("./"+fakeDirPath, "./SimSwap/"+fakeDirName)

        logger.info('fake_faces 디렉토리 SimSwap 내로 디렉토리 통채로 복사 완료')

        # fake_faces 디렉토리의 SRC와 DST 이미지들을 face swap
        os.system("cd SimSwap && \
            python test_one_image.py --name people --Arc_path "+args.model_path+"\
            --pic_a_path fake_faces --pic_b_path ../"+target_json +" --output_path ../"+swappedDirPath)

        # swap 작업 종료후 SimSwap안에 복사해둔 fake_faces 디렉토리 삭제
        if os.path.exists("./SimSwap/"+fakeDirName) :
            shutil.rmtree("./SimSwap/"+fakeDirName)

        logger.info('swap 작업 종료후 SimSwap안에 복사해둔 fake_faces 디렉토리 삭제')

        print("swap 완료!")

        # 스왑된 이미지를 원래 이미지에 맞추기
        logger.info('스왑된 이미지를 원래 이미지에 맞추기 : 좌표 불러오기')

        with open(apiServerPath+"/rec_list.pickle", "rb") as f :
            rec_list = pickle.load(f)

        logger.info('스왑된 이미지를 원래 이미지에 맞추기 : 원본 이미지 불러오기')
        source_image = Image.open(apiServerPath+'/'+src_img)

        logger.info('얼굴 맞추기')

        for target_face in target_face_list :
            index, area = rec_list[int(target_face)][0], rec_list[int(target_face)][1] # area = (left, top, right, bottom
            width, height = abs(area[2]-area[0]), abs(area[3]-area[1])

            logger.info(swappedDirPath+'/result'+util_funcs.get_3_num(index)+'.'+src_img_type+'열기 ::::'+str(os.path.exists(swappedDirPath+'/result'+util_funcs.get_3_num(index)+'.'+src_img_type)))
            cropped_img = Image.open(swappedDirPath+'/result'+util_funcs.get_3_num(index)+'.'+src_img_type)

            logger.info('크롭된 얼굴 이미지 열기 완료')


            # swap한 얼굴을 모자이크 시킨 후 합성하는 경우
            if args.option == "swap_mosaic" :
                if width <= 0 or height <= 0 :
                    continue
                width_mosaic_strength = int(width/50)
                height_mosaic_strength = int(height/50)

                if width_mosaic_strength <= 0 or height_mosaic_strength <= 0 : # 너무 작은 경우
                    width_mosaic_strength, height_mosaic_strength = 30, 30 # 그냥 상수로 진행

                cropped_img = cropped_img.resize((width_mosaic_strength, height_mosaic_strength))
                cropped_img = cropped_img.resize((width, height))

            # swap한 얼굴을 그대로 합성하는 경우
            else :
                 # 원본 이미지에 맞게 resize
                cropped_img = cropped_img.resize((width, height), Image.LANCZOS)

            logger.info('얼굴 합성 시작')

            # 이미지 합성
            source_image.paste(im=cropped_img, box=(area[0], area[1]))
            print('person '+str(index)+' 합성 완료')
            logger.info(str(index)+'번째 얼굴 합성 완료')

        logger.info(' 최종 합성 이미지 저장 시작')

        # 최종 합성 이미지 저장
        source_image.save(apiServerPath+'/'+'return2-'+args.key+'.'+src_img_type)
        print("최종합성 완료!")
        logger.info(' 최종 합성 이미지 저장 완로')

elif args.type == 'video' :
    print("sorry, video service hasn't done yet🥲")
    exit(1)
    ############# undone ###############

else :
    print("wrong args")
    exit(1)

print("총"+str(time.time() - start_time)+" 소요")
logger.info("총 "+str(time.time() - start_time)+" 소요")
