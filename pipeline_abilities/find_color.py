import tkinter
import os

class FindColor:
    def __init__(self, pipeline_name, root):
        self.color_listbox_label = None
        self.image_listbox_label = None
        self.finish_next_button = None
        self.average_checkbox = None
        self.color_listbox = None
        self.canvas = None
        self.image_listbox = None
        self.find_color_window = None
        self.pipeline_name = pipeline_name
        self.root = root

        self.average_value = tkinter.IntVar()

        self.execute_find_color()

        self.load_images()

    def execute_find_color(self):
        self.find_color_window = tkinter.Toplevel(self.root)
        self.find_color_window.title('Find color')

        self.image_listbox_label = tkinter.Label(self.find_color_window, text='Images:')
        self.image_listbox_label.grid(row=0, column=0)

        self.image_listbox = tkinter.Listbox(self.find_color_window, height=45)
        self.image_listbox.grid(row=1, column=0, rowspan=3)
        # self.image_listbox.bind('<Double-Button-1>')

        self.canvas = tkinter.Canvas(self.find_color_window, width=1280, height=720)
        self.canvas.grid(row=1, column=1, rowspan=3)

        # self.canvas.bind()
        # self.canvas.bind()

        self.color_listbox_label = tkinter.Label(self.find_color_window, text='Check color:')
        self.color_listbox_label.grid(row=0, column=2)

        self.color_listbox = tkinter.Listbox(self.find_color_window, height=20)
        self.color_listbox.grid(row=1, column=2)

        self.average_checkbox = tkinter.Checkbutton(self.find_color_window,
                                                    text='Get average color value',
                                                    onvalue=1,
                                                    offvalue=0,
                                                    variable=self.average_value,
                                                    command=self.switch_find_color_type)
        self.average_checkbox.grid(row=2, column=2)

        self.finish_next_button = tkinter.Button(self.find_color_window, text='Finish')
        self.finish_next_button.grid(row=3, column=2)

    def switch_find_color_type(self):
        if self.average_value.get() == 0:
            self.finish_next_button['text'] = 'Finish'
        else:
            self.finish_next_button['text'] = 'Next'

    def load_images(self):
        image_list = os.listdir('pipelines/{}/data/temp_data/images/'.format(2))
        for image in image_list:
            self.image_listbox.insert(tkinter.END, 'Image #{}'.format(image.split('_')[1][:len(image.split('_')[1]) - 4]))
