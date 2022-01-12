import tkinter
from tkinter import *
from tkinter import Label
import cv2
import threading

from os import listdir
from os.path import isfile, join

from PIL import Image, ImageTk

from pipeline_exec import Pipeline


class App:
    def __init__(self):
        self.root = Tk()
        self.label = None
        self.root.resizable(width=False, height=False)

        self.new_pipeline_name = None

        self.drawMainScreen()

        self.root.mainloop()

    def drawMainScreen(self):
        """Function draws main screen"""
        self.root.title('Main screen')

        self.pipeline_label = Label(self.root, text='Choose pipeline')
        self.pipeline_label.grid(row=0, column=0, sticky='nw', padx=(10, 10), pady=(30, 25))

        self.value = StringVar(self.root)
        self.value.set("Select pipeline")

        self.pipeline_names = self.retrievePipelineList()

        self.pipeline_list = OptionMenu(self.root, self.value, *self.pipeline_names, command=self.execute_pipeline)
        self.pipeline_list.grid(row=0, column=0, sticky='nw', padx=(100, 0), pady=(25, 25))

        self.create_new_pipeline_button = Button(self.root, text='Create new pipeline', command=self.open_name_new_pipeline_window)
        self.create_new_pipeline_button.grid(row=0, column=0, sticky='nw', padx=(250, 0), pady=(27, 0))

    def open_name_new_pipeline_window(self):
        self.create_pipeline_name = tkinter.Toplevel(self.root)
        self.create_pipeline_name.title('Create Pipeline Name')

        self.label1 = tkinter.Label(self.create_pipeline_name, text='Please type pipeline name')
        self.label1.pack(pady=(10, 0))

        self.text_field = tkinter.Entry(self.create_pipeline_name, width=50)
        self.text_field.pack(padx=(50, 50), pady=(10, 10))

        self.close_button = tkinter.Button(self.create_pipeline_name, text='Cancel', command=self.create_pipeline_name.destroy)
        self.close_button.pack(side=LEFT, padx=(150, 0), pady=(0, 15))

        self.start_button = tkinter.Button(self.create_pipeline_name, text='Start', command=lambda: self.open_create_pipeline_window(self.text_field.get()))
        self.start_button.pack(side=LEFT, padx=(10, 0), pady=(0, 15))

    def open_create_pipeline_window(self, name):
        self.new_pipeline_name = name

        self.create_pipeline = tkinter.Toplevel(self.root)
        self.create_pipeline.title('Create Pipeline')
        self.create_pipeline.geometry('1280x720')

        vid = cv2.VideoCapture(0)


    def execute_pipeline(self, name):
        PipelineExecuter(self.root)

    def retrievePipelineList(self) -> list:
        return [f.split('.')[0] for f in listdir('pipelines') if isfile(join('pipelines', f))]


class PipelineExecuter:
    def __init__(self, root):
        self.pipeline = Pipeline('pipeline1')

        self.label = tkinter.Label(root, relief=tkinter.RIDGE, width=1280, height=720)
        self.label.grid(row=1, column=0)

        self.root = root

        self.thread = threading.Thread(target=self.update_image)

        self.thread.start()

    def update_image(self):
        self.pipeline.execute()

        self.colored = cv2.cvtColor(self.pipeline.get_frame(), cv2.COLOR_BGR2RGB)

        self.resized_video = cv2.resize(self.colored, (1280, 720))

        self.img = Image.fromarray(self.resized_video)
        self.imgTk = ImageTk.PhotoImage(image=self.img)

        self.label.config(image=self.imgTk)

        self.update_image().after(2000, self.update_image)


if __name__ == "__main__":
    App()
