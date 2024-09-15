# 3D Strand-Based Hair Generation and Editing System: Using HairStep to Generate Hair from Images and Export Editable and Applicable Files

## Requirements
Anaconda 3, Blender 4.3

## Installation & Execution
```
git clone --recursive https://github.com/asd56585452/3D-hair-reconstruction-interface.git

cd 3D-hair-reconstruction-interface

cd HairStep

conda env create -f environment.yml
conda activate hairstep

pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html

pip install -r requirements.txt

cd external/3DDFA_V2
sh ./build.sh
cd ../../
cd ..

rm -r HairStep/results
pip install PyQt6==6.2.3
pip install pyrr
pip install PyOpenGL
cp -r HairStepCpuPatch/* HairStep
cd grid_less
```

Next, download the model files from the HairStep GitHub repository.

Download the [SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) checkpoint and place it in `./HairStep/checkpoints/SAM-models/`.

Download the [3D networks](https://drive.google.com/file/d/1-akuukaYYtJDta24AAqVdgUOGte4EmQf/view?usp=drive_link) checkpoint and place it in `./HairStep/checkpoints/recon3D/`.

Then, execute the following command (make sure to run the command in the `./grid_less/` folder):
```
python grid_slicer.py
```

The code has been tested on Ubuntu 24.04 LTS.

If you encounter an "ld" error while running "sh ./build.sh", it could be due to an issue with `anaconda3/envs/hairstep/compiler_compat/ld`. You can delete it. Refer to:
- https://github.com/ninia/jep/issues/446
- https://github.com/ContinuumIO/anaconda-issues/issues/11152

## Demo and Usage Examples

[Google Drive link](https://drive.google.com/drive/folders/1_6hng2yhaZRj3WhFUzHleKHKf7HK7atU?usp=sharing)
