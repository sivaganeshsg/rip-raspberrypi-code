import sys
import datetime
from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average
import numpy as np

def to_grayscale(arr):
    "If arr is a color image (3D array), convert it to grayscale (2D array)."
    if len(arr.shape) == 3:
        return average(arr, -1)  # average over the last axis (color channels)
    else:
        return arr


def compare_images0(img1, img2):
    # normalize to compensate for exposure difference, this may be unnecessary
    # consider disabling it
    img1 = normalize(img1)
    img2 = normalize(img2)
    # calculate the difference and its norms
    diff = img1 - img2  # elementwise for scipy arrays
    m_norm = sum(abs(diff))  # Manhattan norm
    z_norm = norm(diff.ravel(), 0)  # Zero norm
    return (m_norm, z_norm)


def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng


def compare(file1, file2):
	img1=to_grayscale(imread(file1).astype(float))
	img2=to_grayscale(imread(file2).astype(float))

	n_m, n_0 = compare_images0(img1, img2)
	n_mp, n_0p = n_m/img1.size, n_0*1.0/img1.size

	print "Manhattan norm:", n_m, "/ per pixel:", n_mp
	print "Zero norm:", n_0, "/ per pixel:", n_0p
 
	
	return n_mp <= 11
