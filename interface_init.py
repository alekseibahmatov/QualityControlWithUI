import tkinter
from tkinter import *
from tkinter import Label, messagebox
import cv2
import threading

from os import listdir, mkdir
from os.path import isfile, join, isdir

from PIL import Image, ImageTk

from pipeline_exec import Pipeline
from pipeline_creation import CreatePipeline


class App:
    def __init__(self):
        self.root = Tk()
        self.label = None
        self.root.resizable(width=False, height=False)

        self.actions_list = ['Find item', 'Find color']

        self.new_pipeline_name = None
        self.task_sequence = []
        self.last_action_chosen = None

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

        self.create_new_pipeline_button = Button(self.root, text='Create new pipeline',
                                                 command=self.open_name_new_pipeline_window)
        self.create_new_pipeline_button.grid(row=0, column=0, sticky='nw', padx=(250, 0), pady=(27, 0))

    def open_name_new_pipeline_window(self):
        self.create_pipeline_name = tkinter.Toplevel(self.root)
        self.create_pipeline_name.title('Create Pipeline Name')

        self.label1 = tkinter.Label(self.create_pipeline_name, text='Please enter pipeline name')
        self.label1.pack(pady=(10, 0))

        self.text_field = tkinter.Entry(self.create_pipeline_name, width=50)
        self.text_field.pack(padx=(50, 50), pady=(10, 10))

        self.close_button = tkinter.Button(self.create_pipeline_name, text='Cancel',
                                           command=self.create_pipeline_name.destroy)
        self.close_button.pack(side=LEFT, padx=(150, 0), pady=(0, 15))

        self.start_button = tkinter.Button(self.create_pipeline_name, text='Start',
                                           command=lambda: self.open_create_pipeline_window(self.text_field.get(),
                                                                                            self.create_pipeline_name))
        self.start_button.pack(side=LEFT, padx=(10, 0), pady=(0, 15))

    def open_create_pipeline_window(self, name, previous_window):
        if self.text_field.get() != "" and self.create_new_pipeline_folder():
            previous_window.destroy()
            self.new_pipeline_name = name

            self.create_pipeline = tkinter.Toplevel(self.root)
            self.create_pipeline.title('Create Pipeline')

            self.action_label = tkinter.Label(self.create_pipeline, text='Select actions')
            self.action_label.grid(row=0, column=0)

            self.action_listbox = tkinter.Listbox(self.create_pipeline)

            for i, entry in enumerate(self.actions_list):
                self.action_listbox.insert(i, entry)
            self.action_listbox.grid(row=1, column=0)

            self.param_label = tkinter.Label(self.create_pipeline, text='Select parameters')
            self.param_label.grid(row=0, column=1)

            self.action_parameters_listbox = tkinter.Listbox(self.create_pipeline)
            self.action_parameters_listbox.grid(row=1, column=1)

            self.sequence_label = tkinter.Label(self.create_pipeline, text='Current sequence')
            self.sequence_label.grid(row=2, column=0)

            self.sequence_listbox = tkinter.Listbox(self.create_pipeline)
            self.sequence_listbox.grid(row=3, column=0)

            self.execute_sequence_button = tkinter.Button(self.create_pipeline, text='Execute',
                                                          command=lambda: [self.create_pipeline.destroy(),
                                                                           CreatePipeline(self.task_sequence, self.root, self.new_pipeline_name)])
            self.execute_sequence_button.grid(row=3, column=1)

            self.action_listbox.bind('<Double-Button-1>',
                                     lambda x: self.open_add_task_window(self.action_listbox, self.sequence_listbox))
            self.sequence_listbox.bind('<Double-Button-1>',
                                       lambda x: self.change_action_parameters(self.sequence_listbox,
                                                                               self.action_parameters_listbox))
            self.action_parameters_listbox.bind('<Double-Button-1>', lambda x: self.action_parameters_processing(
                self.action_parameters_listbox, self.sequence_listbox))

    def create_new_pipeline_folder(self):
        if not isdir('pipelines/{}'.format(self.text_field.get())):
            mkdir('pipelines/{}'.format(self.text_field.get()))
            return True
        else:
            messagebox.showerror('Error', 'Pipeline name is already taken')
            return False

    def open_add_task_window(self, listbox1, listbox2):
        self.add_task_window = tkinter.Toplevel(self.root)
        self.add_task_window.title('Add task')

        self.close_button = tkinter.Button(self.add_task_window, text='Close', command=self.add_task_window.destroy)
        self.close_button.pack(side=LEFT)

        self.add_button = tkinter.Button(self.add_task_window, text='Add',
                                         command=lambda: [self.add_task(listbox1, listbox2),
                                                          self.add_task_window.destroy()])
        self.add_button.pack(side=LEFT)

    def add_task(self, listbox1, listbox2):
        self.task_sequence.append(listbox1.get(listbox1.curselection()[0]))

        listbox2.insert(END, '{}'.format(listbox1.get(listbox1.curselection()[0])))

    def action_parameters_processing(self, parameters_listbox, sequence_listbox):
        if parameters_listbox.get(parameters_listbox.curselection()[0]) == 'Delete':
            parameters_listbox.delete(0, END)
            self.delete_task(sequence_listbox)

    def delete_task(self, sequence_listbox):
        del self.task_sequence[self.last_action_chosen]
        sequence_listbox.delete(self.last_action_chosen)

    def change_action_parameters(self, listbox1, listbox2):
        self.action_params = [
            ['Delete'],
            ['Delete']
        ]

        self.last_action_chosen = listbox1.curselection()[0]

        listbox2.delete(0, tkinter.END)

        for entry in self.action_params[listbox1.curselection()[0]]:
            listbox2.insert(END, entry)

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

        self.update_image().after(0, self.update_image)


if __name__ == "__main__":
    App()
