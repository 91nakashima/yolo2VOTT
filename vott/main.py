import random
import string
from PIL import Image
import os
import urllib.parse
import json
from glob import glob
import hashlib


def get_default_json(state=2, v_type=1):
    """
    vottのデフォルトのjson
    """
    return {
        "asset": {
            "format": "",  # jpg
            "id": "",
            "name": "",  # xxx.jpg
            "path": "",  # file:****.jpg
            "size": {
                "width": 3024,
                "height": 4032
            },
            "state": state,
            "type": v_type
        },
        "regions": [],
        "version": "2.2.0"
    }


def del_vott_json(path: str):
    """
    VOTTのjsonを削除する
    """
    if path[-1] == '/':
        path = path[:-1]

    for file in glob(f'{path}/*.json'):
        os.remove(file)

        """
        assetsの中身
        "336d14450664b2d932f22966bcee17b4": {
            "format": "jpeg",
            "id": "336d14450664b2d932f22966bcee17b4",
            "name": "1.jpeg",
            "path": "file:/Users/****/%E3%82%A8%E3%83%92%E3%82%99%E3%81%AE%E8%87%AA%E5%8B%95%E6%A4%9C%E5%87%BA%202/1.jpeg",
            "size": {
                "width": 3024,
                "height": 4032
            },
            "state": 1,
            "type": 1
        },
        """


class AutoVottAnnotation:
    def __init__(self, img_path: str, state=2, v_type=1):
        """
        画像のパスを指定して初期化
        """
        self.state = state
        self.type = v_type
        self.regions = []
        self.save_json = get_default_json(state, v_type)
        self.img_path = img_path

        img = Image.open(img_path)
        width, height = img.size

        self.save_json['asset']['size']['width'] = width
        self.save_json['asset']['size']['height'] = height
        self.save_json['asset']['format'] = img.format.lower()
        self.save_json['asset']['id'] = hashlib.md5(f'file:{urllib.parse.quote(img_path)}'.encode()).hexdigest()
        self.save_json['asset']['name'] = os.path.basename(img.filename)
        self.save_json['asset']['path'] = f'file:{urllib.parse.quote(img_path)}'

        vott_paths = glob(f'{os.path.dirname(img_path)}/*.vott')
        if len(vott_paths) == 0:
            raise ValueError('vottファイルが存在しません')

        for file in vott_paths:
            self.vott_path = file

    def add_regions(self, label: int, xyxy: list):
        region = {
            "id": AutoVottAnnotation._randomname(9),  # 9桁のランダム英数字
            # TODO 自動検出にする必要がある RECTANGLE or POLYGON
            "type": "RECTANGLE",  # 長方形: RECTANGLE, ポリゴン: POLYGON
            "tags": [label],  # 自動検出なので基本的に1つだけ入る
            "boundingBox": {
                    "height": xyxy[3] - xyxy[1],
                    "width": xyxy[2] - xyxy[0],
                    "left": xyxy[0],
                    "top": xyxy[1]
            },
            "points": []
        }

        top_left = [xyxy[0], xyxy[1]]
        top_right = [xyxy[2], xyxy[1]]
        bottom_right = [xyxy[2], xyxy[3]]
        bottom_left = [xyxy[0], xyxy[3]]

        for n in [top_left, top_right, bottom_right, bottom_left]:
            region['points'].append({
                "x": n[0],
                "y": n[1]
            })

        self.regions.append(region)

    def save(self):
        self.save_json['regions'] = self.regions

        dir_path = self.img_path.replace(os.path.basename(self.img_path), '')

        with open(f'{dir_path}{self.save_json["asset"]["id"]}-asset.json', 'w') as f:
            json.dump(self.save_json, f, indent=4)

        with open(self.vott_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_data['assets'][self.save_json['asset']['id']] = {
                "format": self.save_json['asset']['format'],
                "id": self.save_json['asset']['id'],
                "name": self.save_json['asset']['name'],
                "path": self.save_json['asset']['path'],
                "size": self.save_json['asset']['size'],
                "state": 2,
                "type": self.type
            }
            json_data['lastVisitedAssetId'] = self.save_json['asset']['id']

        with open(self.vott_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        print('jsonを保存')

    def _randomname(n: int = 32):
        """
        ランダムな英数字を作成
        """
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)
