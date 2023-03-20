import torch
import cv2
import torchvision
from torchvision import transforms
import os


class Model:
    def __init__(self, path, name):
        self.model_name = name
        self.model = torch.load(path)
        self.model.cuda()
        self.model.eval()
        self.transforms = transforms.Compose([torchvision.transforms.ToTensor(),
                                              torchvision.transforms.Normalize(
                                                  (0.1307,), (0.3081,))])

    # 图片预处理
    def img_preprocessing(self, img_path):
        img = cv2.imread(img_path)
        # 灰度转换
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 缩放成(28, 28)大小的图片
        gray = cv2.resize(gray, (28, 28))
        # 转置（EMNIST数据集里的图片格式）
        gray = cv2.transpose(gray)
        # 二值处理
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        # 膨胀处理
        binary = cv2.dilate(binary, (2, 2))
        return binary

    # 图片检测
    def output(self, img_path):
        # 图片预处理
        binary = self.img_preprocessing(img_path)
        # 格式转换
        inp = self.transforms(binary)
        inp = torch.unsqueeze(inp, 0)
        inp = inp.cuda()
        # 检测
        with torch.no_grad():
            out = self.model(inp)
        return out


if __name__ == '__main__':
    selection = {'SpinalVGG': './CharacetrRecognition/SpinalVGG.pth',
                 'WaveMix': './CharacetrRecognition/SpinalVGG.pth'}

    m = Model(selection['SpinalVGG'], 'SpinalVGG')
    img_path = input("输入识别单字母图片的文件夹路径") 
    # img_path = './CharacetrRecognition/example'
    acc = 0
    sum_ = 0
    lst = os.listdir(img_path)
    for i in lst:
        if i.endswith('.png') or i.endswith('.jpg'):
            sum_ += 1
            path = os.path.join(img_path, i)
            out = m.output(path)
            # 输出分类结果
            res = chr(out.argmax(1) + 64)
            acc += res == i[0]
            print("res: {} real: {} {} {}".format(res, i[0], res == i[0], acc/sum_))
