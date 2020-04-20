import efficientnet_pytorch
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
import os

from PIL import Image
from torch.autograd import Variable
from torchvision import transforms

class TransferedEfficientNet(nn.Module):
	"""
	Pretrained EfficientNet as feature extractor + couple of FC Layers
    	See: https://github.com/lukemelas/EfficientNet-PyTorch
	"""

	def __init__(self):
        	super(TransferedEfficientNet, self).__init__()
        	self.feature_extractor = efficientnet_pytorch.EfficientNet.from_pretrained('efficientnet-b0')
        	self.fc1 = nn.Linear(1280 * 7 * 7, 600)
        	self.fc2 = nn.Linear(600, 33)
    
	def forward(self, x):
        	x = self.feature_extractor.extract_features(x)
        	x = x.view(-1, 1280 * 7 * 7)
        	x = F.relu(self.fc1(x))
        	x = self.fc2(x)
        	return x

def image_processing(image_name):
	"""
	Function, which predicts top 3 most probable classes of given image.
	Output is in string format.
	"""

	image = Image.open(image_name)

	# Resize image to 224x224 pixel size + convert to tensor.
	loader = transforms.Compose([transforms.Resize((224, 224)),
	                             transforms.ToTensor()])
	image = loader(image).float()
	image = Variable(image, requires_grad=True)
	
	# Creating skeleton of the model.
	model = TransferedEfficientNet()

	# Loading one of our trained models onto skeleton.
	model.load_state_dict(torch.load('augmented_98', map_location='cpu'))

	# Getting predictions from the model.
	output = model(image[None, ...])  

	# Getting names for all classes, that can be predicted.
	with open('labels.txt', "r", encoding='utf-8') as f:
	    classes_text = f.read()
	classes = classes_text.split('\n')

	# Get top 3 results from output.
	values, idx = torch.topk(output.data, 3)
	prediction = 'TOP 3 probabilities:\n'
	
	# Giving text output as a result.
	prediction += '\n'.join(classes[i] for i in idx[0])

	return prediction


