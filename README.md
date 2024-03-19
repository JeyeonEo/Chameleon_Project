<p align="center">
    <img alt="chameleon-logo" height="200" alt="chameleon Logo" src="https://velog.velcdn.com/images/yesterdaykite/post/be7ccd28-795f-4f46-a760-4def206ee43f/image.png"/>
</p>


# 🦎 Motivation & Introduction
As media consumption grows up, the problem of infringement of the right of portrait of those intentionally or unintentionally filmed in the video is emerging. This happens not only because it is difficult for editors to mosaic every face, but also because the mosaic-processed video lacks aesthetics. Therefore, we felt the need to solve the problem, and developed a technology that can conveniently and aesthetically perform face editing. Machine learning is used to extract all faces from photos and videos, and not only to mosaic them, but also to synthesize the faces of people who do not exist (hereafter, fake faces) generated through GAN with the faces to be covered to create aesthetically heterogeneous faces. We have developed a program that provides anonymization technology that is not It is expected that it will be helpful in the advent of the ethical media era by developing from the existing anonymization through mosaic, satisfying legal issues and aesthetics at the same time, and increasing user accessibility through the ios application.


# 🦎 Features

<p align="center">
    <img alt="chameleon-logo" height="300" alt="chameleon Logo" src="https://velog.velcdn.com/images/yesterdaykite/post/86f1d731-e1d7-4546-af3d-968fa8ecd8b7/image.gif"/>
	<img alt="chameleon-logo" height="300" alt="chameleon Logo" src="https://velog.velcdn.com/images/yesterdaykite/post/90869a04-9951-4e1f-a76a-c06b14436c63/image.gif"/>
</p>


iOS application with:

- Classify unknown faces and get index from user uploaded media
- Matches random fake faces
- 🦎 Swap random fake face and real face
- Otherwise, you can make mosaic on each faces that you choose
- Otherwise, you can make mosaic on fake-swapped face that you choose
	- It can prevent for inverse mosaic reasoning attack 👍



# 🦎 Getting Started

You can set up a local development environment and test an API.

## Environment

- Ubuntu 18 LTS
- Conda
- Git
- GPU in GTX Series


## Initializing all the packages and sources


1. Clone this project
```
git clone https://github.com/yesterdayKite/ChameleonProject_ML.git
```

2. Prepare Conda and create conda environment
```
conda create -n chameleon python=3.6
conda activate chameleon
conda install pytorch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 cudatoolkit=10.2 -c pytorch
(option): pip install --ignore-installed imageio
pip install insightface==0.2.1 onnxruntime moviepy
(option): pip install onnxruntime-gpu  (If you want to reduce the inference time)(It will be diffcult to install onnxruntime-gpu , the specify version of onnxruntime-gpu may depends on your machine and cuda version.)
```

3. download ```simswap``` in the root dir ./
```
git clone https://github.com/neuralchen/SimSwap.git SimsSwap
```

4. download pretrained model or fine-tune pre-trained model

There are two archive files in the drive: **checkpoints.zip** and **arcface_checkpoint.tar**

- **Copy the arcface_checkpoint.tar into ./SimSwap/arcface_model**
- **Unzip checkpoints.zip, place it in the ./SimSwap/ dir ./**

[[Google Drive]](https://drive.google.com/drive/folders/1jV6_0FIMPC53FZ2HzZNJZGMe55bbu17R?usp=sharing) Password: ```jd2v```

you can use this pretrained model, or fine-tune by your own
- we fine-tuned our own for Asian-face robust model 😊
- with [Asian-Face-Image_Dataset-AFD-dataset](https://github.com/X-zhangyang/Asian-Face-Image-Dataset-AFD-dataset)

# How to Run

## 1. Classify
1. place input media into database directory
```
./database/$$file_name$$
```

2. run command at root dir
- for picture
```
$ python src/classifier.py --type photo --key $$file_name$$
```


3. you can get your output in below dir
```
./database/$$file_name$$/
```

## 2. Face Swap with Fake Face

1. Choose target face (by json file)
```
$ database/$$file_name$$/choice_$$file_name$$.json
```
Inside the json file, you can choose target face by index
```
// .json file
{
	"faces" : [0, 2, 5]
}
```

2. run command

- swap
```
$ python src/swapper.py --type photo --key $$file_name$$ --model_path=$your_model$
```
- mosaic
```
$ python src/swapper.py --type photo --key $$file_name$$ --option mosaic
```
- swap & mosaic
```
$ python src/swapper.py --type photo --key $$file_name$$ --option swap_mosaic --model_path=$your_model$
```

3. get output file
you can get output file in below directory
```
./database/$$file_name$$/
```


# Open Source Used
- [SimSwap](https://github.com/neuralchen/SimSwap) : for face swap


## Ask a question about Amplication

You can ask questions, and participate in discussions about.

Plase note me 📧 [jeyeon.yona.eo@gmail.com](jeyeon.yona.eo@gmail.com)


