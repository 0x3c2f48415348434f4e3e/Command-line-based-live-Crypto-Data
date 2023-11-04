#!/bin/bash

#before doing all of the above, lets just get the current working directory so we can go abck later
CWD=`pwd`
#Lets just first delete all of the files in the bin direcotry to make sure everything is clean
#Also we want to check if the direcotry is empty first
cd ../bin
isEmpty="total 0" #When we use the ls -lrt command it returns that if direcotry is empty

res=`ls -lrt`

if [[ $res = $isEmpty ]]
then
    echo "Directory is empty"
else
    FILE=`ls *.o`
    for value in $FILE
    do

    rm $value
    echo "$value deleted from `pwd`"
    done
fi

unset FILE

#Go back to initial current working direcoty
cd "$CWD"

#Here we shall run make to build all of the file for us
make

#remeber how make runs within the same direcotry and the result will be produced int he current directory, so we want to move it after

#Before doing the rest, lets just wait a few seconds, so we do not rush everything
sleep 5s # Waits 5 seconds.
echo "Waiting."

#lets get all files that ends with a .o

FILE=`ls *.db`

for value in $FILE
do
mv $FILE ../Database
echo "Moved object files to bin directory"
done
