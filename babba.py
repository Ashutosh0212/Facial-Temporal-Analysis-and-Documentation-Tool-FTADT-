from tkinter import filedialog, ttk
import sys
import face_recognition
import cv2
import os
from xlwt import Workbook
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


root = Tk()


# this is the function called when the button is clicked
def bvideo():
    global video_label
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                          filetypes=(("video files", ".mp4"), ("all files", ".")))
    video_label.set(filename)


# this is the function called when the button is clicked
def bfolder():
    global folder_label
    filename = filedialog.askdirectory()
    folder_label.set(filename)


# this is the function called when the button is clicked
def bface():
    global face_label
    filename = filedialog.askdirectory()
    face_label.set(filename)


# this is the function called when the button is clicked
def btnClickFunction():
    x = maincall(video_label.get(), folder_label.get(), face_label.get())
    if x == 1:
        final_label.set("Done Please check the Output folder ")
    else:
        final_label.set(" Error ")


def maincall(input_video_path, output_location, faces_loc):
    # Function to create encodings from already known faces
    def create_encodings(Image):
        encodings = []
        name_encode = []
        for image in Image:
            img = face_recognition.load_image_file(faces_loc + "/" + image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodings.append(encode)
            name_encode.append(image[:-4])
        return [encodings, name_encode]

    # This is listing images in  the directory and seding it to encoding
    Image = os.listdir(faces_loc)
    x = create_encodings(Image)
    encodings = x[0]
    names = x[1]
    time_log = []
    time_stamp = []
    print("Encoding finsh...")
    unknown_c = 0

    # Update fun to update the all the known time features
    def update(frame, sec):
        time_log.append(frame)
        time_stamp.append(sec)

    # gettting the frames and scanning it
    def getFrame(sec):
        print("scanning : ", sec)
        frame_names = []
        vidcap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        hasFrames, img = vidcap.read()
        if not hasFrames:  # Checking wheteher we got any frame or not terminating cond
            update(frame_names, sec)
            return 0
        imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # this detects all the faces and their locations
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        print("faces detectd :", len(facesCurFrame))  # number of face detected

        for encodeFace, faceLoc in zip(encodesCurFrame,
                                       facesCurFrame):  # zip the faces with thei8r locs and pass it as a var

            matches = face_recognition.compare_faces(encodings, encodeFace)
            faceDis = face_recognition.face_distance(encodings,
                                                     encodeFace)  # cal the dis for each faec with the known encodings

            matchIndex = np.argmin(faceDis)  # Checking the min dis from all the encodings
            if matches[matchIndex]:  # if founde the match appending it to the frames list
                name = names[matchIndex]
                frame_names.append(name)
            else:  # if no face matched , so its unkown face
                print("adding unknown person:::")
                # appending the names and the encodins
                names.append("Unknwon" + str(len(names) + 1))
                encodings.append(encodeFace)
                frame_names.append("Unknwon" + str(len(names)))
                # saving the images in the folder
                xname = output_location + str("/Unknwon" + str(len(names))) + '.jpg'
                cv2.imwrite(xname, img)
        update(frame_names, sec)  # updating the time frame
        return 1

    # =====================================================================================================

    videoname = input_video_path
    vidcap = cv2.VideoCapture(videoname)

    sec = 0
    frameRate = 2
    count = 1

    success = getFrame(sec)
    i = 0
    log = [success]

    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = getFrame(sec)
        log.append(success)

    # Till here who9le database is made now we will be appending it to the csv
    # =====================================================================================================

    database = {}
    timepp = {}
    for i in names:
        database[i] = []
        timepp[i] = 0
        cur = 0
        flag = False
        print(time_log[0])
        if i in time_log[0]:
            flag = True
        for j in range(len(time_log)):
            if i in time_log[j]:
                if flag == False:
                    flag = True
                    database[i].append(str(cur) + " -absent- " + str(time_stamp[j]))
                    cur = time_stamp[j]
                # database[i].append(1)
            else:
                if flag == True:
                    flag = False
                    database[i].append(str(cur) + " -prsent- " + str(time_stamp[j]))
                    timepp[i] += time_stamp[j] - cur
                    cur = time_stamp[j]

    wb = Workbook()
    print(timepp)
    print(names)
    print(database)

    sheet1 = wb.add_sheet('Sheet 1')
    sheet1.write(0, 0, "Name")
    sheet1.write(0, 1, "Total Time")
    nline = 1
    for i in database:
        sheet1.write(nline, 0, i)
        for j in range(len(database[i])):
            sheet1.write(nline, j + 3, database[i][j])
        sheet1.write(nline, 1, timepp[i])

        nline += 1

        print(i, *database[i])

    wb.save(output_location + '/database.xls')
    return 1


# This is the section of code which creates the main window
root.geometry('530x600')
root.configure(background='#FAEBD7')
root.title('Face detection App')

video_label = StringVar()
video_label.set("Please select desired video (mp4)")

folder_label = StringVar()
folder_label.set("Please select desired Output location")

face_label = StringVar()
face_label.set("Please select known faces Folder")

final_label = StringVar()
final_label.set("")

# This is the section of code which creates a button
Button(root, text='Browse video', bg='#F0F8FF', font=('arial', 12, 'normal'), width=13, command=lambda: bvideo()).place(
    x=38, y=122)

Button(root, text='Browse folder', bg='#F0F8FF', font=('arial', 12, 'normal'), width=13,
       command=lambda: bfolder()).place(x=38, y=192)

Button(root, text='Known Faces', bg='#F0F8FF', font=('arial', 12, 'normal'), width=13, command=lambda: bface()).place(
    x=38, y=262)

l1 = Label(root, textvariable=video_label, bg='#FAEBD7', font=('arial', 12, 'normal')).place(x=238, y=132)

l2 = Label(root, textvariable=folder_label, bg='#FAEBD7', font=('arial', 12, 'normal')).place(x=238, y=202)

l3 = Label(root, textvariable=face_label, bg='#FAEBD7', font=('arial', 12, 'normal')).place(x=238, y=268)

Button(root, text='scan', bg='#EE7621', font=('arial', 12, 'normal'), width=13, command=btnClickFunction).place(x=190,
                                                                                                                y=344)

final = Label(root, textvariable=final_label, bg='#FAEBD7', font=('arial', 12, 'normal')).place(x=150, y=420)

Label(root, text='FACE DETECTION AND DATABASE GENERATION ', bg='#FAEBD7', font=('arial', 12, 'normal')).place(x=71,
                                                                                                              y=37)

root.mainloop()
