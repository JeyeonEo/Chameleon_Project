
from deepface import DeepFace
import random
import os
import glob
from PIL import Image
import shutil


# index i를 000, 001, 002 형태로 바꾼다
def get_3_num(index) :
    res = ""
    index_len = len(str(index))
    for _ in range(3-index_len ):
        res+= '0'
    res += str(index)
    return res


# face 정보가 있는 obj를 받아서, age와 Gender에 따라 face db의 디렉토리를 리턴하다
def set_face_type(obj) :
    dir_name = ""

    # age
    age = obj["age"]
    if  age< 10 :
        dir_name += "0-"
    elif 10 <= age and age < 20 :
        dir_name += "10-"
    elif 20 <= age and age < 40 :
        dir_name += "2030-"
    else :
        dir_name += "4050-"

    # gender
    gender = obj["gender"]
    if gender == "Woman" :
        dir_name += "female"
    else :
        dir_name += "male"

    return dir_name


# 디렉토리의 파일 중 하나를 랜덤하게 골라 파일 이름을 리턴한다
def get_random_face_addr(dir_name) :
    fake_face_dir = 'database/fakefaces/'
    img_list = os.listdir(fake_face_dir + dir_name)
    return random.choice(img_list)

# 성별, 얼굴 디렉토리중 하나를 랜덤하게 골라 디렉토리 이름을 리턴한다
def get_random_face_dir() :
    fake_face_dir_list = ['0-female', '0-male', '10-female', '10-male', '2030-female', '2030-male', '4050-male', '4050-female']
    return random.choice(fake_face_dir_list)

# swap config directory의 파일들에게 해당하는 가짜 얼굴 DST_0X.jpg들을 만들어준다.
def set_fake_faces(chosen_arr, swap_config_dir, random_face=True) :

    # fakeface 저장하는 디렉토리 만듦
    SRC_list = os.listdir(swap_config_dir)
    fake_face_dir = 'database/fakefaces/'

    # 각 source image마다 가짜 얼굴을 매칭시켜 DST_001.jpg 식으로 저장한다.
    for src_img in SRC_list :

        if random_face :  # random_Face = False :: 성별, 나잇대를 분석한 얼굴을 매칭할때
            try :
                obj = DeepFace.analyze(img_path = swap_config_dir+"/"+src_img, actions = ['age', 'gender'])
                print('>>>>>>>>>>>>>obj 내용 : ' + str(obj))
                dir_name = set_face_type(obj)
            except :
                dir_name = '2030-female'
        else : # random_face = True : # 완전 랜덤 얼굴을 배치할때
            dir_name = get_random_face_dir()
            dst_img = get_random_face_addr(dir_name)

        shutil.copy(fake_face_dir+'/'+dir_name+'/'+dst_img, swap_config_dir)
        shutil.move(swap_config_dir+'/'+dst_img, swap_config_dir+'/'+'DST_'+src_img[4:])
    print("fake faces all copied!")


def resize_into_224(dir_addr) :
    files = glob.glob("./"+dir_addr+"/*")
    for f in files :
        img = Image.open(f)
        img_resize = img.resize((224,224), Image.LANCZOS)
        img_resize = img_resize.convert("RGB")
        img_resize.save(f)

