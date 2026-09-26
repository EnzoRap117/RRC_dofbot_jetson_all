#!/usr/bin/env python
# coding: utf-8

# In[146]:


#defining everything
import numpy as np
import time
from Arm_Lib import Arm_Device
import cv2
from PIL import Image as im
import glob
import matplotlib.pyplot as plt
import sys
import math

#Dofbot/0.py_install/Arm_Lib/Arm_Lib.py

# Define the link lengths in meterss
l0 = 0.061   # base to servo 1
l1 = 0.0435  # servo 1 to servo 2
l2 = 0.08285 # servo 2 to servo 3
l3 = 0.08285 # servo 3 to servo 4
l4 = 0.07385 # servo 4 to servo 5
l5 = 0.05457 # servo 5 to gripper

# Define the base axis
ex = np.array([1, 0, 0]).T  # x axis
ey = np.array([0, 1, 0]).T  # y axis
ez = np.array([0, 0, 1]).T  # z axis
    
# Get DOFBOT object
Arm = Arm_Device()
time.sleep(.2)

#defining constants: 
#need to get camera calibration matrix


# In[147]:


def arm_move(q):
    Arm.Arm_serial_servo_write6(q[0], q[1], q[2], q[3], q[4], q[5], 500)
    
def measure_arm(): 
    return np.array([Arm.Arm_serial_servo_read(1),Arm.Arm_serial_servo_read(2),Arm.Arm_serial_servo_read(3), Arm.Arm_serial_servo_read(4),Arm.Arm_serial_servo_read(5)])


# In[150]:


#initilize arm configeration
initial_config = np.array([0, 90, 45, 45, 90, 180])
arm_move(initial_config)
time.sleep(0.5)


# In[151]:


starting_config = np.array([Arm.Arm_serial_servo_read(1),Arm.Arm_serial_servo_read(2),Arm.Arm_serial_servo_read(3), Arm.Arm_serial_servo_read(4),Arm.Arm_serial_servo_read(5)])
print(starting_config)


# In[152]:


#for picking color
#do this later
def color_correction(image):
    image_og = image
    #converts image to hsv
    hsv_image = cv2.cvtColor(image_og, cv2.COLOR_RGB2HSV)
    # Split the HSV channels
    h, s, v = cv2.split(hsv_image)
    # Increase the saturation channel
    saturation_factor = 1.4  # Adjust this factor to control the saturation increase
    s = np.clip(s * saturation_factor, 0, 255).astype(np.uint8)
    # Merge the HSV channels back
    hsv_image = cv2.merge([h, s, v])
    #adjustest overall brightness
    hsv_image[:, :, 2] = hsv_image[:, :, 2] * 0.9

    #trying to fix white balance
    #hsv_image[:,:,0] = hsv_image[:,:,0]/250*150 #blue channel
    #hsv_image[:,:,1] = hsv_image[:,:,1]/235*150 #green channel

    #so didn't have to do with camera? idk what it was doing

    # Convert the image back to BGR color space
    convert_RGB = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)

    #blurring image to reduce color noise
    blurred_rgb = cv2.GaussianBlur(convert_RGB, (7, 7), 0)
    #final image output
    rgb_image = blurred_rgb
    
    return rgb_image


# In[153]:


def color_masking(image):
    rgb_image = image
    red_lower_rgb = np.array([100, 0, 0], np.uint8) 
    red_upper_rgb = np.array([255, 100, 100], np.uint8)
    red_mask_rgb = cv2.inRange(rgb_image, red_lower_rgb, red_upper_rgb)
    red_output_rgb = cv2.bitwise_and(rgb_image, rgb_image, mask = red_mask_rgb)
    #red_masked = cv2.cvtColor(rgb_image, cv2.COLOR_HSV2RGB) 

    #blue
    #values from yahboom
    #blue_lower_rgb = np.array([0, 0, 135], np.uint8) 
    #blue_upper_rgb = np.array([100, 100, 255], np.uint8) 
    blue_lower_rgb = np.array([0, 0, 104], np.uint8) 
    blue_upper_rgb = np.array([100, 100, 255], np.uint8) 
    #custom
    blue_mask_rgb = cv2.inRange(rgb_image, blue_lower_rgb, blue_upper_rgb)
    blue_output_rgb = cv2.bitwise_and(rgb_image, rgb_image, mask = blue_mask_rgb)
    #blue_masked = cv2.cvtColor(blue_output, cv2.COLOR_HSV2RGB) 
    
    #green
    #values from yahboom
    #green_lower_rgb = np.array([0, 50, 0], np.uint8) 
    #green_upper_rgb = np.array([100, 255, 100], np.uint8) 
    #custom
    green_lower_rgb = np.array([35, 60, 75], np.uint8) 
    green_upper_rgb = np.array([80, 255, 125], np.uint8) 
    green_mask_rgb = cv2.inRange(rgb_image, green_lower_rgb, green_upper_rgb)
    green_output_rgb = cv2.bitwise_and(rgb_image, rgb_image, mask = green_mask_rgb)
    #green_masked = cv2.cvtColor(green_output, cv2.COLOR_HSV2RGB)
    
    return red_mask_rgb, red_output_rgb, blue_mask_rgb, blue_output_rgb, green_mask_rgb, green_output_rgb


# In[154]:


#capturing current field of view
camera = cv2.VideoCapture(0)
camera.set(5,10)
ret, image = camera.read()
image_og = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
camera.release()

plt.imshow(image_og)
plt.show()


# In[155]:


altered_im = color_correction(image_og)

plt.imshow(altered_im)
plt.show()


# In[156]:


red_mask_array, red_mask_img, blue_mask_array, blue_mask_img, green_mask_array, green_mask_img = color_masking(altered_im)


# In[157]:


plt.imshow(blue_mask_img)
plt.show()


# In[158]:


mask_blue = im.fromarray(blue_mask_img)
blue_bbox = mask_blue.getbbox()
lx, ly, rx, ry = blue_bbox
print(lx)
print(ly)
print(rx)
print(ry)
boxed_blue = image_og.copy()
boxed_blue = cv2.rectangle(boxed_blue, (lx, ly), (rx, ry), (0, 255, 0), 5)

plt.imshow(boxed_blue)
plt.show()


# In[159]:


box_x_center = int((lx+rx)/2)
print(box_x_center)
box_y_center = int((ly+ry)/2)
print(box_y_center)

img_x_center = int(640/2)
img_y_center = int(480/2)

img_copy = image_og.copy()

circle_center = cv2.circle(img_copy, (box_x_center, box_y_center), 5, (255, 0, 0), -1)
circle_center = cv2.circle(img_copy, (img_x_center, img_y_center), 5, (0, 0, 255), -1)
plt.imshow(circle_center)
plt.show()


# In[165]:


#original no scalar
cam_matrix = np.array([[1.0372e3, 0, 2.8098e2],
                      [0, 1.0373e3, 2.3956e2],
                      [0, 0, 1],])

theta = 9.5

z_dist = 0.9906

world_x2 = ((box_x_center - cam_matrix[0, 2]) / cam_matrix[0, 0]) * z_dist
world_y2 = ((box_y_center - cam_matrix[1, 2]) / cam_matrix[1, 1]) * z_dist

world_y3 = (((box_y_center - cam_matrix[1, 2]) / cam_matrix[1, 1]) * z_dist) * math.sin(theta)
world_x3 = (((box_x_center - cam_matrix[0, 2]) / cam_matrix[0, 0]) * z_dist) - world_y3*math.cos(theta)

print(world_x2)
print(world_y2)
print(world_x3)
print(world_y3)


# In[188]:


#real world is the difference in distance, if negative to the left, if positve to the right

#so they are the same...

adjustment_angle_rad = math.atan(world_x2/ z_dist)
adjustment_angle_rad_ii = math.atan(world_x3/ z_dist)

adj_ang_deg = math.degrees(adjustment_angle_rad)
print(adj_ang_deg)
adj_ang_deg_ii = math.degrees(adjustment_angle_rad_ii)
print(adj_ang_deg_ii)


# In[191]:


config = np.array([0, 90, 45, 45, 90, 180], dtype=np.float64)
config[0] = adj_ang_deg
print(config)

arm_move(config)
time.sleep(1)


# In[192]:


#need to align with zero, only issue is not being able to read angle above 180
#but cannot go back to negative 90 - just one move no correction hope for best

if config[0] < 0:
    config[0] += 180
else:
    config[0] -= 180

#so if negative need to add 180, if postive need to subjectract 180checking
arm_move(config)
time.sleep(1)


# In[193]:


#moving arm back to throw

q2_cock = 45
q3_cock = 40
q4_cock = 90

config[[1, 2, 3]] = [q2_cock, q3_cock, q4_cock]
print(config)

arm_move(config)

time.sleep(1)



# In[194]:



q2_throw = 90
q3_throw = 100

config[[1, 2]] = [q2_throw, q3_throw]
print(config)

q = config

Arm.Arm_serial_servo_write6(q[0], q[1], q[2], q[3], q[4], q[5], 1)



# In[ ]:




