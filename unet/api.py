# -*- coding: utf-8 -*-
"""
Functions to integrate your model with the DEEPaaS API.
It's usually good practice to keep this file minimal, only performing the interfacing tasks.
In this way you don't mix your true code with DEEPaaS code and everything is more modular.
That is, if you need to write the predict() function in api.py, you would import your true predict
function and call it from here (with some processing/postprocessing in between if needed).
For example:

    import utils

    def predict(**kwargs):
        args = preprocess(kwargs)
        resp = utils.predict(args)
        resp = postprocess(resp)
        return resp

To start populating this file, take a look at the docs [1] and at a canonical exemplar module [2].

[1]: https://docs.deep-hybrid-datacloud.eu/
[2]: https://github.com/deephdc/demo_app
"""


# Basic modules for api
from functools import wraps
import shutil
import tempfile
#
from aiohttp.web import HTTPBadRequest
from webargs import fields, validate

#import pickle
#import base64

########## Importing Other packages start from here 


# OS and others packages
import os
import sys

import numpy as np
import matplotlib.pyplot as plt


# image processing libraries

#import skimage.io as io
#import cv2

from PIL import Image
from skimage.io import imread, imsave

from skimage.color import rgb2gray

from skimage import transform
from skimage import img_as_bool


# Tensorflow packages 
import tensorflow as tf

from tensorflow.keras.models import Model, load_model

#from tensorflow import keras
#from tensorflow.keras import backend as K
   

from tensorflow.keras.losses import CategoricalCrossentropy, BinaryCrossentropy
#from focal_loss import BinaryFocalLoss

import h5py


#import zipfile
if sys.version_info >= (3, 6):
    import zipfile
else:
    import zipfile36 as zipfile
#import shutil



# Some parametres for preprocessing image_input

IMG_WIDTH = 1024
IMG_HEIGHT = 1024
IMG_CHANNELS = 3

input_size_2 = (IMG_WIDTH, IMG_HEIGHT)
input_size_3 = (IMG_WIDTH, IMG_HEIGHT, IMG_CHANNELS)



## Metrics for prediction 

def dice_coefficient(y_true, y_pred):
    eps = 1e-6
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection) / (K.sum(y_true_f * y_true_f) + K.sum(y_pred_f * y_pred_f) + eps) #eps pour éviter la division par 0 








#### API functions start from here 


def _catch_error(f):
    """Decorate function to return an error as HTTPBadRequest, in case
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            raise HTTPBadRequest(reason=e)
    return wrap


def get_metadata():
    metadata = {
        "author": "Adnane"
    }
    return metadata


def get_predict_args():
    """
    Input fields for the user.
    """
    arg_dict = {
        "demo-image": fields.Field(
            required=False,
            type="file",
            location="form",
            description="image",  # needed to be parsed by UI
        ),
        # Add format type of the response of predict()
        # For demo purposes, we allow the user to receive back
        # either an image or a zip containing an image.
        # More options for MIME types: https://mimeapplication.net/
        "accept": fields.Str(
            description="Media type(s) that is/are acceptable for the response.",
            validate=validate.OneOf(["image/*", "application/zip"]),
        ),
    }
    return arg_dict





@_catch_error
def predict(**kwargs):
    """
    Return same inputs as provided.
    """
    filepath = kwargs['demo-image'].filename
    name = kwargs['demo-image'].name
    content_type_info = kwargs['demo-image'].content_type
    original_filename = kwargs['demo-image'].original_filename

    ## Import file
    #data = imread(filepath)

    



    # Return the result directly
    if kwargs['accept'] == 'image/*':
    
        ########## Preprocessing 

        # 1 case , one image
        #read_image = data
        list_images = []

        read_image = imread(filepath)   
        image_resized = transform.resize(read_image, input_size_2).astype(np.float32)
        
        list_images.append(image_resized) 
        
        X_test = np.array(list_images)

        print("Shape of this image" , X_test.shape)
        print("Preprocessing Done")


        #load the best model
        path_ = os.getcwd()

        print("this is the path", path_)

        load_model = tf.keras.models.load_model('./unet/unet/models_folder/best_model.h5', custom_objects={'dice_coefficient': dice_coefficient})

        print("Model : successfully loaded")

        # inference for image
        prediction = load_model.predict(X_test) #

        preds_test_t = (prediction > 0.3).astype(np.uint8)

        X_test_result = np.squeeze(preds_test_t[0,:,:,2])*255

        print('inference Done')


        # Saving result 
        imsave("output.png", X_test_result)



        return open("output.png", 'rb')

    


    # Return a zip
    elif kwargs['accept'] == 'application/zip' :

        
        zip_dir = tempfile.TemporaryDirectory()

        # Add original image to output zip
        #shutil.copyfile("output.png",
        #                zip_dir.name + '/demo.png')

        shutil.copyfile(filepath,
                zip_dir.name + '/demo.png')        
        # Add for example a demo txt file
        with open(f'{zip_dir.name}/demo.txt', 'w') as f:
            f.write('Add here any additional information!')


        # Pack dir into zip and return it
        shutil.make_archive(zip_dir.name, format='zip', root_dir=zip_dir.name)
        zip_path = zip_dir.name + '.zip'

        
        ########## Preprocessing 
        # 2 case , dataset.zip

        #read_image = data
        #list_images = []

        #shutil.unpack_archive(filepath, "data_output")
        
        
        #with zipfile.ZipFile(filepath, 'r') as zip_ref:
        #    zip_ref.extractall("./unet/")
        
        #data_dir_path = r'/My Drive/ESRF_Seg_Hands_on/'
        
        #root = os.getcwd()
        
        #data_dir_path = filepath
        #os.makedirs(root+data_dir_path, exist_ok=True)
        #os.listdir(root+data_dir_path)
        #full_path = root+data_dir_path

        print("This is the file path as filename", filepath)
        print("THis is the name", name)
        print("THis is the content_type", content_type_info) 
        print("THis is the original_file_name", original_filename) 

        #with ZipFile(f"{filepath}", 'r') as zipObj:
            # Extract all the contents of zip file in current directory
        #    zipObj.extractall()

        #!unzip -q filepath
        print('unpack done')
        #read_image = imread(filepath)   
        #image_resized = transform.resize(read_image, input_size_2).astype(np.float32)
        
        #list_images.append(image_resized) 
        
        #X_test = np.array(list_images)

        #print("Shape of this image" , X_test.shape)
        #print("Preprocessing Done")
        

        
        #inference for dataset
        # ...
        




        return open(zip_path, 'rb')

# def get_metadata():
#     return {}
#
#
# def warm():
#     pass
#
#
# def get_predict_args():
#     return {}
#
#
# @_catch_error
# def predict(**kwargs):
#     return None
#
#
# def get_train_args():
#     return {}
#
#
def train(**kwargs):
    return predict(**kwargs)


################################################################
# Some functions that are not mandatory but that can be useful #
# (you can remove this if you don't need them)                 #
################################################################

# import pkg_resources
# import os


# BASE_DIR = os.path.dirname(os.path.normpath(os.path.dirname(__file__)))


# def _fields_to_dict(fields_in):
#     """
#     Function to convert mashmallow fields to dict()
#     """
#     dict_out = {}
#
#     for key, val in fields_in.items():
#         param = {}
#         param['default'] = val.missing
#         param['type'] = type(val.missing)
#         if key == 'files' or key == 'urls':
#             param['type'] = str
#
#         val_help = val.metadata['description']
#         if 'enum' in val.metadata.keys():
#             val_help = "{}. Choices: {}".format(val_help,
#                                                 val.metadata['enum'])
#         param['help'] = val_help
#
#         try:
#             val_req = val.required
#         except:
#             val_req = False
#         param['required'] = val_req
#
#         dict_out[key] = param
#     return dict_out
#
#
# def get_metadata():
#     """
#     Predefined get_metadata() that renders your module package configuration.
#     """
#
#     module = __name__.split('.', 1)
#
#     try:
#         pkg = pkg_resources.get_distribution(module[0])
#     except pkg_resources.RequirementParseError:
#         # if called from CLI, try to get pkg from the path
#         distros = list(pkg_resources.find_distributions(BASE_DIR,
#                                                         only=True))
#         if len(distros) == 1:
#             pkg = distros[0]
#     except Exception as e:
#         raise HTTPBadRequest(reason=e)
#
#     ### One can include arguments for train() in the metadata
#     train_args = _fields_to_dict(get_train_args())
#     # make 'type' JSON serializable
#     for key, val in train_args.items():
#         train_args[key]['type'] = str(val['type'])
#
#     ### One can include arguments for predict() in the metadata
#     predict_args = _fields_to_dict(get_predict_args())
#     # make 'type' JSON serializable
#     for key, val in predict_args.items():
#         predict_args[key]['type'] = str(val['type'])
#
#     meta = {
#         'name': None,
#         'version': None,
#         'summary': None,
#         'home-page': None,
#         'author': None,
#         'author-email': None,
#         'license': None,
#         'help-train': train_args,
#         'help-predict': predict_args
#     }
#
#     for line in pkg.get_metadata_lines("PKG-INFO"):
#         line_low = line.lower()  # to avoid inconsistency due to letter cases
#         for par in meta:
#             if line_low.startswith(par.lower() + ":"):
#                 _, value = line.split(": ", 1)
#                 meta[par] = value
#
#     return meta
