import sys
import os
import stat

def readwrite():
    try:
        input=open("a.txt","r")
        output=open("b.txt","w")
        s=input.readlines()
        for line in s:
            singleline=line.rstrip()
            output.write(singleline)
    except IOError:
        print ("oops error accured")
    input.close()
    output.close()
readwrite() 
    
        
        
