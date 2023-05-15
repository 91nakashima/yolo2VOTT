# YOLO to VOTT

## Install

```bash
git clone https://github.com/91nakashima/yolo2VOTT
cd yolo2VOTT
pip install -r requirements.txt  # install
```

## YOLO to Vott

You must create a xxxx.vott file.

```bash
python detect.py --weights yolov5s.pt --is-vott --source {your annotation dir path}
```

Notes:<br />

1.Provider is Local File System.<br />
2.The Source connection and the target connection are the same dir.<br />

### Operation has been confirmed

- MacOS(M1)

### Tips

- If you could not install requirements.txt, you should update pip.
  ```bash
  pip install --upgrade pip
  ```
