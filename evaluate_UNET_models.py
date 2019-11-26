# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:33:31 2019

@author: Nikos
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
import pandas as pd

from keras.models import load_model

path = './data/'
fnames_ts = [f[0] for f in pd.read_csv(path+'fnames_ts.csv',header=None).values.tolist()]#need to unpack list of lists

##get the shape of the data by loading a single image
#IMG_SHAPE = list(img_to_array(load_img(fnames_tr[0],color_mode='rgb',target_size=(400,400))).shape)#convert to list to change width
#IMG_SHAPE[1]=int(IMG_SHAPE[1]/2)#calculate shape after splitting to satellite and map images (halve the width)
#IMG_SHAPE = tuple(IMG_SHAPE)#switch the shape back to a tuple

def load_split_normalize_img(fname, target_size=(400,int(2*400))):
    '''
    Loads an image corresponding to a path given by the filename (fname).
    Then it splits the image in half, the left part is the satellite and
    the right part corresponds to the map portion of the image.
    Additionally, each image is normalized to 0-1.
    By default resizes to 400x400 to make the image dimensions UNET-friendly
    '''
    from keras.preprocessing.image import load_img, img_to_array
    img = img_to_array(load_img(fname,color_mode='rgb',target_size=target_size))/255#normalize 8bit image to 0-1
    img_sat = img[:,:int(img.shape[1]/2),:]#get satellite image (left half)
    img_map = img[:,int(img.shape[1]/2):,:]#get map image (right half)
    return (img_sat, img_map)

def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
    """
    Add a vertical color bar to an image plot.
    https://stackoverflow.com/questions/18195758/set-matplotlib-colorbar-size-to-match-graph
    """
    from mpl_toolkits import axes_grid1
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1./aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    current_ax = plt.gca()
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(current_ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)

#get the shape of the data by loading a single image
IMG_SHAPE = load_split_normalize_img(fnames_ts[0])[0].shape #(400, 400, 3)

#initialize empty matrices to load images
n_images = 20 #how many test images to load
X_ts = np.zeros((n_images,)+IMG_SHAPE)
Y_ts = np.zeros((n_images,)+IMG_SHAPE)
for i in np.arange(n_images):
    X_ts[i,:,:,:], Y_ts[i,:,:,:] = load_split_normalize_img(fnames_ts[i])

#%% evaluate small UNET with binary-cross-entropy loss

#modelname = 'mcd_unet_div8_495K_drop0.0'
#model = load_model('./trained_models/mcd_unet_div8_495K_drop0.0.hdf5')
#Y_ts_hat = model.predict(X_ts)
#M=np.abs(Y_ts-Y_ts_hat)
#mae_pixel=np.mean(M.flatten())#pixel level mae on the test subset
#
##%% evaluate small UNET with MAE loss
#
#modelname = 'mcd_unet_div8_495K_drop0.0_mae'
#model = load_model('./trained_models/mcd_unet_div8_495K_drop0.0_mae.hdf5')
#Y_ts_hat = model.predict(X_ts)
#M=np.abs(Y_ts-Y_ts_hat)
#mae_pixel=np.mean(M.flatten())#pixel level mae on the test subset
#
##%% evaluate UNET with binary-cross-entropy loss
#
#modelname = 'mcd_unet_31M_drop0.0'
#model = load_model('./trained_models/mcd_unet_31M_drop0.0.hdf5')
#Y_ts_hat = model.predict(X_ts)
#M=np.abs(Y_ts-Y_ts_hat)
#mae_pixel=np.mean(M.flatten())#pixel level mae on the test subset

#%% evaluate UNET with MAE loss

modelname = 'mcd_unet_31M_drop0.0_mae'
model = load_model('./trained_models/mcd_unet_31M_drop0.0_mae.hdf5')
Y_ts_hat = model.predict(X_ts)
M=np.abs(Y_ts-Y_ts_hat)
mae_pixel=np.mean(M.flatten())#pixel level mae on the test subset

#%%
fig, axes = plt.subplots(n_images,4,figsize=(4*4,n_images*4))
for i in range(n_images):
    print(i)
    ax=axes[i,0]
    ax.set_title('Satellite')
    ax.imshow(X_ts[i,:,:,:])
    ax.set_xticks(np.arange(0,401,100))
    ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,1]
    ax.set_title('Map - True')
    ax.imshow(Y_ts[i,:,:,:])
    ax.set_xticks(np.arange(0,401,100))
    ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,2]
    ax.set_title('Map - Predicted')
    ax.imshow(Y_ts_hat[i,:,:,:])
    ax.set_xticks(np.arange(0,401,100))
    ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,3]
    ax.set_title('Map - Error: '+str(np.round(M[i,:,:,:].mean(axis=-1).flatten().mean(),3)))#averaged over channels and pixels
    im = ax.imshow(M[i,:,:,:].mean(axis=-1),cmap='gray')
    ax.set_xticks(np.arange(0,401,100))
    ax.set_yticks(np.arange(0,401,100))
    add_colorbar(im)
    
plt.savefig('./figures/'+modelname+'_MAE_'+str(np.round(mae_pixel,3))+'.png',bbox_inches='tight',dpi=100)

#%%
n_images=3
fig, axes = plt.subplots(n_images,4,figsize=(4*4,n_images*4))
idx=[9,10,11]
for i in range(3):
    print(i)
    ax=axes[i,0]
    ax.set_title('Satellite')
    ax.imshow(X_ts[idx[i],:,:,:])
    #ax.set_xticks(np.arange(0,401,100))
    #ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,1]
    ax.set_title('Map - True')
    ax.imshow(Y_ts[idx[i],:,:,:])
    #ax.set_xticks(np.arange(0,401,100))
    #ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,2]
    ax.set_title('Map - Predicted')
    ax.imshow(Y_ts_hat[idx[i],:,:,:])
    #ax.set_xticks(np.arange(0,401,100))
    #ax.set_yticks(np.arange(0,401,100))
    
    ax=axes[i,3]
    ax.set_title('Map - Error: '+str(np.round(M[idx[i],:,:,:].mean(axis=-1).flatten().mean(),3)))#averaged over channels and pixels
    im = ax.imshow(M[idx[i],:,:,:].mean(axis=-1),cmap='gray',vmin=0,vmax=1)
    #ax.set_xticks(np.arange(0,401,100))
    #ax.set_yticks(np.arange(0,401,100))
    add_colorbar(im)
    plt.suptitle('UNET',fontsize=40)
plt.savefig('./figures/cropped_'+modelname+'_MAE_'+str(np.round(mae_pixel,3))+'.png',bbox_inches='tight',dpi=100)