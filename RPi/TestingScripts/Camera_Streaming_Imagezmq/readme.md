pip install imagezmq

Server side:
pip install opencv-python
pip install imagezmq
pip install torch
pip install numpy
pip install pillow
pip install yolov5

I have cloned YoloV5's repo into the packages folder as a submodule, and added a entry in the .gitmodules file.

Code used to clone:
git submodule add https://github.com/ultralytics/yolov5.git

For future git clones, you will need to do this additional step to add YoloV's submodule to your project:
git clone --recurse-submodules https://github.com/yourusername/yourproject.git
