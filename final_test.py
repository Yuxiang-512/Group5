#importing the libraries
import tensorflow as tf  
import keras
import numpy as np
import pandas as pd
import sys
import json
from matplotlib.animation import FuncAnimation


if len(sys.argv) > 1:
    list_str = sys.argv[1]
    try:
        # 解析命令行传来的 JSON 字符串
        address_list = json.loads(list_str)
        print("Received list:", address_list)

        # 确保有足够的文件路径
        if len(address_list) >= 2:
            baseline_df = pd.read_excel(address_list[0])
            toolwear_df = pd.read_excel(address_list[1])
            print("Datasets loaded successfully.")
            # 进行数据处理
        else:
            print("Error: Not enough file paths provided.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
else:
    print("No file paths provided.")
    sys.exit(1)

#convert data frame into arrays
good_features = baseline_df.values
bad_features = toolwear_df.values

#train test split to divide the data into training data (70%) and test data (30%)
#This is done on both healthy (good) and toolwear (bad) data

from sklearn.model_selection import train_test_split

good_train, good_test = train_test_split(good_features, test_size=0.2, random_state=40)
bad_train, bad_test = train_test_split(bad_features, test_size=0.2, random_state=40)

#Training data is further split into 70% for model training and 30% for threshold setting

good_train, good_threshold = train_test_split(good_train, test_size=0.3, random_state=40)
bad_train, bad_threshold = train_test_split(bad_train, test_size=0.3, random_state=40)

#data scalling

from sklearn.preprocessing import StandardScaler

sc = StandardScaler()
good_train = sc.fit_transform(good_train)
good_test = sc.transform(good_test)
good_threshold = sc.transform(good_threshold)
bad_train = sc.fit_transform(bad_train)
bad_test = sc.transform(bad_test)
bad_threshold = sc.transform(bad_threshold)

combine_test = np.vstack([good_test , bad_test])

#specify the number of condensed features. This will be the number of neurons in the hidden layer
condensed_f = 20

#constructing the good autoencoder model

#input layer which number of neurons equals the number of original features
l_in_good = keras.Input(shape=(good_features.shape[1],))

#hidden layer which condenses the feature into the specified number of condensed features
l_condensed_good = keras.layers.Dense(condensed_f)(l_in_good)

#output layer which is the same as the input
l_out_good = keras.layers.Dense(good_features.shape[1])(l_condensed_good)

#defining the good autoencoder
autoencoder_good = keras.Model(l_in_good, l_out_good)

#constructing the bad autoencoder model

#input layer which number of neurons equals the number of original features
l_in_bad = keras.Input(shape=(bad_features.shape[1],))

#hidden layer which condenses the feature into the specified number of condensed features
l_condensed_bad = keras.layers.Dense(condensed_f)(l_in_bad)

#output layer which is the same as the input
l_out_bad = keras.layers.Dense(good_features.shape[1])(l_condensed_bad)

#defining the bad autoencoder
autoencoder_bad = keras.Model(l_in_bad, l_out_bad)

#compile the model
autoencoder_good.compile(optimizer='adam', loss='mse')
#train the model
autoencoder_good.fit(good_train, good_train, epochs = 50, batch_size = 8, validation_split = 0.1)

#compile the model
autoencoder_bad.compile(optimizer='adam', loss='mse')
#train the model
autoencoder_bad.fit(bad_train, bad_train, epochs = 50, batch_size = 8, validation_split = 0.1)

from sklearn.metrics import mean_absolute_error

#Testing the good autoencoder with healthy datasets
GAE_pred_good = autoencoder_good.predict(good_threshold)
print(mean_absolute_error(good_threshold,GAE_pred_good))

#Testing the good autoencoder with toolwear datasets
GAE_pred_bad = autoencoder_good.predict(bad_threshold)
print(mean_absolute_error(bad_threshold,GAE_pred_bad))

#Testing the bad autoencoder with healthy datasets
BAE_pred_good = autoencoder_bad.predict(good_threshold)
print(mean_absolute_error(good_threshold,BAE_pred_good))

#Testing the bad autoencoder with healthy datasets
BAE_pred_bad = autoencoder_bad.predict(bad_threshold)
print(mean_absolute_error(bad_threshold,BAE_pred_bad))

GAE_MSE_toolwear = []
GAE_MSE_healthy = []

for i in range(len(bad_threshold)):
    GAE_MSE_healthy.append(mean_absolute_error(good_threshold[i],GAE_pred_good[i]))
    GAE_MSE_toolwear.append(mean_absolute_error(bad_threshold[i],GAE_pred_bad[i]))

import matplotlib.pyplot as plt 
import threading

# plot lines 
def data_generator():
    """模拟实时数据生成，此函数运行在单独的线程中"""
    while True:
        GAE_MSE_healthy.append(np.random.rand() * 20)
        GAE_MSE_toolwear.append(np.random.rand() * 20 + 1)
        time.sleep(0.5)  # 模拟数据生成间隔

fig, ax = plt.subplots()
ax.set_xlabel("Test Entry")
ax.set_ylabel("Mean Square Error (MSE)")
ax.set_xlim(0, 100)  # 初始x轴范围，可能需要动态调整
ax.set_ylim(0, 30)   # 假定的y轴范围

line1, = ax.plot([], [], 'r-', label="baseline")
line2, = ax.plot([], [], 'b-', label="toolwear")
ax.legend(loc='upper right')

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

def update(frame):
    xdata = list(range(1, len(GAE_MSE_healthy) + 1))
    line1.set_data(xdata, GAE_MSE_healthy)
    line2.set_data(xdata, GAE_MSE_toolwear)
    
    # 调整x轴范围以适应数据
    ax.set_xlim(0, len(GAE_MSE_healthy) + 1)
    
    return line1, line2

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=500)

# 启动数据生成线程
thread = threading.Thread(target=data_generator)
thread.daemon = True  # 设置为守护线程，当主程序退出时线程也退出
thread.start()

plt.show()


BAE_MSE_toolwear = []
BAE_MSE_healthy = []

for i in range(len(bad_threshold)):
    BAE_MSE_healthy.append(mean_absolute_error(good_threshold[i],BAE_pred_good[i]))
    BAE_MSE_toolwear.append(mean_absolute_error(bad_threshold[i],BAE_pred_bad[i]))


import matplotlib.pyplot as plt 

#create index for x axis
index = list(range(1,(len(bad_threshold)+1)))

# plot lines 
plt.plot(index, BAE_MSE_healthy, label = "baseline") 
plt.plot(index, BAE_MSE_toolwear, label = "toolwear") 
plt.xlabel("Test Entry")
plt.ylabel("Mean Square Error (MSE)")
plt.legend(loc='upper right') 
plt.show()


window_size = 10
GAE_average_healthy = []
GAE_average_toolwear = []

for ind in range(len(GAE_MSE_healthy) - window_size + 1):
    GAE_average_healthy.append(np.mean(GAE_MSE_healthy[ind:ind+window_size]))
    GAE_average_toolwear.append(np.mean(GAE_MSE_toolwear[ind:ind+window_size]))

test_entries = list(range(1,len(GAE_average_healthy)+1))

# plot lines 
plt.plot(test_entries, GAE_average_healthy, label = "baseline") 
plt.plot(test_entries, GAE_average_toolwear, label = "toolwear") 
plt.xlabel("Test Entry")
plt.ylabel("Mean Square Error (MSE)")
plt.legend(loc='upper right') 
plt.show()


window_size = 10
BAE_average_healthy = []
BAE_average_toolwear = []

for ind in range(len(BAE_MSE_healthy) - window_size + 1):
    BAE_average_healthy.append(np.mean(BAE_MSE_healthy[ind:ind+window_size]))
    BAE_average_toolwear.append(np.mean(BAE_MSE_toolwear[ind:ind+window_size]))


index = list(range(1,len(BAE_average_healthy)+1))

# plot lines 
plt.plot(index, BAE_average_healthy, label = "baseline") 
plt.plot(index, BAE_average_toolwear, label = "toolwear") 
plt.xlabel("Test Entry")
plt.ylabel("Mean Square Error (MSE)")
plt.legend(loc='upper right') 
plt.show()


#Threshold is determined as the mid point 

#Threshold for good autoencoder
GAE_threshold = max(GAE_average_healthy) + (min(GAE_average_toolwear) - max(GAE_average_healthy))/2
print(GAE_threshold)

#Threshold for bad autoencoder
BAE_threshold = max(BAE_average_toolwear) + (min(BAE_average_healthy) - max(BAE_average_toolwear))/2
print(BAE_threshold)

#Moving average filter is also applied to the data. 
#To implement this 10 data entries are inputted into the model in each iteration. 
#The MSE from each iteration is compared with the threshold to determine the state of toolwear

import time 

window_size = 10
result = []
MSE_GAE = []
MSE_BAE = []


for j in range (1, combine_test.shape[0] - window_size + 1):
    gae_pred = autoencoder_good.predict(combine_test[j: j + window_size])
    bae_pred = autoencoder_bad.predict(combine_test[j: j + window_size])
    
    gae_error = mean_absolute_error(combine_test[j: j + window_size],gae_pred)
    bae_error = mean_absolute_error(combine_test[j: j + window_size],bae_pred)

    MSE_GAE.append(gae_error)
    MSE_BAE.append(bae_error)
    

    if ((gae_error < GAE_threshold) and (bae_error > BAE_threshold)):
        result.append("healthy")
    elif ((gae_error > GAE_threshold) and (bae_error < BAE_threshold)):
        result.append("toolwear")
    else:
        result.append("anomaly")


test_entries = list(range(1,len(MSE_BAE)+1))

# plot lines 
plt.plot(test_entries, MSE_GAE, label = "Good AE") 
plt.plot(test_entries, MSE_BAE, label = "Bad AE") 
plt.xlabel("Test Entry")
plt.ylabel("Mean Square Error (MSE)")
plt.legend(loc='upper right') 
plt.show()


print(result)

