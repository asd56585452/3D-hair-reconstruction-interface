# 頭髮重建系統:利用HairStep從圖片生成頭髮並輸出成可編輯和應用的檔案 

## 需求
anaconda 3、Blender 4.3

## 安裝 & 執行
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
接著去HairStep的github下載模型檔案

下載 [SAM](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth) 的 checkpoint 並放在 ./HairStep/checkpoints/SAM-models/. 

下載 [3D networks](https://drive.google.com/file/d/1-akuukaYYtJDta24AAqVdgUOGte4EmQf/view?usp=drive_link) 的 checkpoint 並放在 ./HairStep/checkpoints/recon3D/.

之後靠以下命令執行。(記得要在./grid_less/資料夾下執行指令)
```
python grid_slicer.py
```

Code is tested on Ubuntu 24.04 LTS.

如果執行"sh ./build.sh"時遇到"ld"的報錯，anaconda3/envs/hairstep/compiler_compat/ld可能有問題，刪掉它。參考
https://github.com/ninia/jep/issues/446
和
https://github.com/ContinuumIO/anaconda-issues/issues/11152

## demo和使用範例

https://drive.google.com/drive/folders/1_6hng2yhaZRj3WhFUzHleKHKf7HK7atU?usp=sharing

