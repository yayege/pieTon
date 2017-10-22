#!/usr/bin/python
import sys
import struct
import copy
import os
import shutil
import pickle
from ctypes import *

lib = cdll.LoadLibrary("./libfast_filter.so")

def loadBMPImage( img_name ):
	f = open(img_name,"rb")
	data = (c_char*os.path.getsize(img_name))()
	for i in range(len(data)):
		data[i] = f.read(1)
	f.close()
	return data

def parseFilterCmdArgs( cmd_args ):

  filter_width = int( cmd_args[2] )
  filter_weights = []
  filter_offsets = []

  for i in range(0,filter_width*filter_width):
    filter_weights.append( float(cmd_args[3+i] ))

  return ( filter_width, filter_weights )

def doConvolution( img_data, filter_width, filter_weights, img_height, img_width ):
  
  out_img_data = copy.deepcopy(img_data)
  for row in range(filter_width/2,img_height-filter_width/2-1):
    for col in range(filter_width/2,img_width-filter_width/2-1):
      for color in range(0,3):
        out_img_data[row][col][color] = 0
        filter_index = 0
        for row_offset in range(-filter_width/2,filter_width/2):
          for col_offset in range(-filter_width/2,filter_width/2):
            weight = filter_weights[filter_index]
            out_img_data[row][col][color] += weight*img_data[row+row_offset][col+col_offset][color]
            filter_index = filter_index+1
          
  return out_img_data     
  
def saveBMPImage( out_data, out_fname):
  img_out = open( out_fname, 'wb' )
  for i in range(len(out_data)):
    img_out.write(out_data[i])
  img_out.close()

if sys.argv[1] == "load":
	try:
		os.remove("result.bmp")
	except:
		pass
	finally:
		shutil.copy(sys.argv[2],"result.bmp")
		try:
			os.remove("history.pickle")
		except:
			pass
		history = open("history.pickle","wb")
		history.write('c')
		for byte in open(sys.argv[2],"rb"):
			history.write(byte)
		history.close()
elif sys.argv[1] == "undo":
	print("undo")
	data_saved = open("history.pickle","rb").read()
	data_result = open("result.bmp","rb").read()
	if data_saved[0] == "c" or data_saved[0] == 'n':
		print("Can't undo")
	else:
		os.remove("result.bmp")
		os.remove("history.pickle")
		result = open("result.bmp","wb")
		history = open("history.pickle","wb")

		history.write("n")
		for byte in data_result:
			history.write(byte)
		history.close()

		data_saved = data_saved[1:]
		for byte in data_saved:
			result.write(byte)
		result.close()
		
elif sys.argv[1] == "redo":
	print("undo")
	data_saved = open("history.pickle","rb").read()
	data_result = open("result.bmp","rb").read()
	if data_saved[0] == "c" or data_saved[0] == 'b':
		print("Can't redo")
	else:
		os.remove("result.bmp")
		os.remove("history.pickle")
		result = open("result.bmp","wb")
		history = open("history.pickle","wb")

		history.write("b")
		for byte in data_result:
			history.write(byte)
		history.close()

		data_saved = data_saved[1:]
		for byte in data_saved:
			result.write(byte)
		result.close()
else:
	print("filter")
	(filter_width, filter_weights) = parseFilterCmdArgs( sys.argv )
	
	try:
		os.remove("history.pickle")
	except:
		pass

	history = open("history.pickle","wb")
	history.write("b")
	for byte in open("result.bmp","rb"):
		history.write(byte)
	history.close()

	data_in = loadBMPImage( "result.bmp")
	file_out_name="result.bmp"

	data_out = (c_char*len(data_in))()

	filter_converted = (c_float*len(filter_weights))()
	for i in range(len(filter_weights)):
	  filter_converted[i] = filter_weights[i]

	lib.doFiltering.argTypes=[c_char_p,c_float*len(filter_weights),c_int,c_char_p]
	lib.doFiltering( data_in, filter_converted, c_int(filter_width), data_out )
	saveBMPImage( data_out,file_out_name)


