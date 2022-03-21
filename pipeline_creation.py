import queue
from worker import worker
import tkinter
import cv2
import os
from PIL import Image, ImageTk, ImageGrab


class CreatePipeline:
    def __init__(self, pipeline, root, pipeline_name):
        self.image_listbox_image_id = None
        self.boxes_listbox = None
        self.thread = None
        self.finish_button = None
        self.next_button = None
        self.abort_button = None
        self.take_snapshot_button = None
        self.image_listbox = None
        self.image_count_label = None

        self.pipeline_sequence = pipeline
        self.pipeline_name = pipeline_name
        self.root = root

        self.canvas = None

        self.q = queue.Queue()
        self.q.put(True)

        self.start_x = None
        self.start_y = None

        self.rects = {}

        self.rect = None
        self.original_rects = None

        self.rect_count = 0

        self.x = self.y = 0

        self.curX = self.curY = 0

        self.cap = cv2.VideoCapture(0)

        self.isNamingWindowOpened = False

        self.image_index = 0

        self.current_image = 0

        self.classes = {}

        self.sv = tkinter.StringVar()

        self.isTakingSnapshot = True

        self.terminal()

    def terminal(self):
        for action in self.pipeline_sequence:
            if action == 'Find item':
                self.execute_find_item()

    def execute_find_item(self):
        self.labeling_window = tkinter.Toplevel(self.root)
        self.labeling_window.title('Labelimg')

        self.image_listbox = tkinter.Listbox(self.labeling_window, height=40)
        self.image_listbox.grid(row=0, column=0, rowspan=6)
        self.image_listbox.bind('<Double-Button-1>', lambda x: self.switch_image_alert())

        self.canvas = tkinter.Canvas(self.labeling_window, width=1280, height=720)
        self.canvas.grid(row=0, column=1, rowspan=6)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.image_count_label = tkinter.Label(self.labeling_window, text='0/50 images labeled')
        self.image_count_label.grid(row=0, column=2)

        self.boxes_listbox = tkinter.Listbox(self.labeling_window)
        self.boxes_listbox.grid(row=1, column=2)
        self.boxes_listbox.bind('<Double-Button-1>', lambda x: self.delete_box(self.boxes_listbox))

        self.take_snapshot_button = tkinter.Button(self.labeling_window, text='Take snapshot',
                                                   command=self.take_snapshot)
        self.take_snapshot_button.grid(row=2, column=2)

        self.abort_button = tkinter.Button(self.labeling_window, text='Abort', command=self.abort_snapshot)
        self.abort_button['state'] = 'disabled'
        self.abort_button.grid(row=3, column=2)

        self.next_button = tkinter.Button(self.labeling_window, text='Next image', command=self.next_image)
        self.next_button['state'] = 'disabled'
        self.next_button.grid(row=4, column=2)

        self.finish_button = tkinter.Button(self.labeling_window, text='Finish')
        self.finish_button['state'] = 'disabled'
        self.finish_button.grid(row=5, column=2)

        self.thread = self.update_canvas()

    def delete_box(self, listbox):
        listbox_item = listbox.get(listbox.curselection()[0])

        index = int(listbox_item.split(' ')[1][1:])
        self.canvas.delete(self.rects[index][0])
        self.canvas.delete(self.rects[index][1])
        listbox.delete(listbox.curselection()[0])

        class_name = listbox_item.split(' - ')[1]

        self.classes[class_name] -= 1

        if self.classes[class_name] == 0:
            del self.classes[class_name]

        del self.rects[index]

        if self.boxes_listbox.size() == 0:
            self.next_button['state'] = 'disabled'

    def on_button_press(self, event):
        if self.abort_button['state'] == 'normal' and not self.isNamingWindowOpened:
            self.start_x = event.x
            self.start_y = event.y

            self.rect = self.canvas.create_rectangle(self.x, self.y, 0, 0, outline="green", width=2)

    def on_move_press(self, event):
        if self.abort_button['state'] == 'normal' and not self.isNamingWindowOpened:
            self.curX, self.curY = (event.x, event.y)

            self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        if self.abort_button['state'] == 'normal' and not self.isNamingWindowOpened:
            self.isNamingWindowOpened = True
            naming_window = tkinter.Toplevel(self.root)
            naming_window.title('Name box')

            self.root.register(self.disable_enable_btn_by_entry)

            self.sv = tkinter.StringVar()

            self.entry = tkinter.Entry(naming_window)
            self.entry.grid(row=0, column=0, columnspan=2)
            self.sv.trace('w', lambda nm, idx, mode, var=self.sv: self.disable_enable_btn_by_entry(var))
            self.entry.config(textvariable=self.sv)
            self.entry.focus()

            cancel_button = tkinter.Button(naming_window, text='Cancel',
                                           command=lambda: [self.remove_rect(self.rect), naming_window.destroy()])
            cancel_button.grid(row=1, column=0)

            self.ok_button = tkinter.Button(naming_window, text='Ok',
                                            command=lambda: [self.add_rect(event), naming_window.destroy()])
            self.ok_button.grid(row=1, column=1)

            self.ok_button['state'] = 'disabled'

    def disable_enable_btn_by_entry(self, value):
        if len(value.get()) == 0:
            self.ok_button['state'] = 'disabled'
        else:
            self.ok_button['state'] = 'normal'

    def remove_rect(self, rect):
        self.canvas.delete(rect)

    def add_rect(self, event):

        top_left = [self.curX if self.start_x > self.curX else self.start_x,
                    self.curY if self.start_y > self.curY else self.start_y]
        bottom_right = [self.curX if self.start_x < self.curX else self.start_x,
                        self.curY if self.start_y < self.curY else self.start_y]

        self.rects[self.rect_count] = [self.rect,
                                       self.canvas.create_text(top_left[0] + 50, top_left[1] - 20, fill='green',
                                                               font='Helvetica 12 bold',
                                                               text='Box #{} - {}'.format(self.rect_count,
                                                                                          self.entry.get())),
                                       [top_left[0], top_left[1], bottom_right[0], bottom_right[1]], self.entry.get()]
        if self.entry.get() in self.classes:
            self.classes[self.entry.get()] += 1
        else:
            self.classes[self.entry.get()] = 1

        self.boxes_listbox.insert(tkinter.END, 'Box #{} - {}'.format(self.rect_count, self.entry.get()))
        self.rect_count += 1
        self.isNamingWindowOpened = False

        if self.boxes_listbox.size() > 0:
            self.next_button['state'] = 'normal'

    def take_snapshot(self):
        self.take_snapshot_button['state'] = 'disabled'
        self.abort_button['state'] = 'normal'
        self.next_button['state'] = 'disabled'

        self.current_image = self.image_index

        self.rects = {}

        self.image_listbox.insert(tkinter.END, 'Image: #{}'.format(self.image_index))

        self.save_image()

        self.isTakingSnapshot = True

        self.thread.abort()

    def abort_snapshot(self):
        # Disabling Abort and Next buttons while user changing positions of details on table
        self.take_snapshot_button['state'] = 'normal'
        self.abort_button['state'] = 'disabled'
        self.next_button['state'] = 'disabled'

        # Changing Save button text to Next image and Delete button to Abort
        self.next_button['text'] = 'Next image'
        self.abort_button['text'] = 'Abort'

        # Deleting already existing boxes
        for key, value in self.rects.items():
            self.canvas.delete(value[0])
            self.canvas.delete(value[1])

        # Clearing self.rects dictionary
        self.rects = {}

        # Setting self.rect_count to 0
        self.rect_count = 0

        # Getting all boxes on the image
        boxes = self.boxes_listbox.get(0, tkinter.END)

        # Iterating through all boxes in the image
        for item in boxes:

            # Getting class name of current box
            class_name = item.split(' - ')[1]

            # Decreasing current class boxes count
            self.classes[class_name] -= 1

            # Deleting current class if there is no boxes with such class
            if self.classes[class_name] == 0:
                del self.classes[class_name]

        # Deleting current image
        self.delete_image(self.current_image)

        # Also deleting label if user is deleting already existing image
        if self.image_index != self.current_image:
            self.delete_label(self.current_image)

            # Deleting current image from image listbox
            self.image_listbox.delete(self.image_listbox_image_id)

            # Updating image count in UI
            self.image_count_label.config(text='{}/50 images labeled'.format(self.image_listbox.size()))

            # Checking if there is enough images to continue
            if self.image_listbox.size() < 50:
                self.finish_button['state'] = 'disabled'
        else:
            self.image_listbox.delete(self.image_listbox.get(0, tkinter.END).index('Image: #{}'.format(self.image_index)))

        # Clearing boxes listbox
        self.boxes_listbox.delete(0, tkinter.END)

        # Continuing to stream webcam image on canvas
        self.thread = self.update_canvas()

        self.isTakingSnapshot = False

    def next_image(self):
        # Disabling Abort and Next buttons while user changing positions of details on table
        self.take_snapshot_button['state'] = 'normal'
        self.abort_button['state'] = 'disabled'
        self.next_button['state'] = 'disabled'

        self.save_image_data()

        # Changing label data in existing label file
        if self.next_button['text'] == 'Next image':
            # Increasing image counter
            self.current_image += 1
            self.image_index += 1

        # Zeroing rectangle count
        self.rect_count = 0

        # Clearing boxes listbox
        self.boxes_listbox.delete(0, tkinter.END)

        # Continuing to stream webcam image on canvas
        self.thread = self.update_canvas()

        # Changing Save button text to Next image and Delete button to Abort
        self.next_button['text'] = 'Next image'
        self.abort_button['text'] = 'Abort'

        self.isTakingSnapshot = False

    def delete_image(self, image):
        os.remove('pipelines/{}/data/temp_data/images/img_{}.png'.format(self.pipeline_name, image))

    def delete_label(self, label):
        os.remove('pipelines/{}/data/temp_data/labels/label_{}.txt'.format(self.pipeline_name, label))

    def save_image(self):
        if not os.path.isdir('pipelines/{}/data/temp_data'.format(self.pipeline_name)):
            os.mkdir('pipelines/{}/data'.format(self.pipeline_name))
            os.mkdir('pipelines/{}/data/temp_data'.format(self.pipeline_name))
            os.mkdir('pipelines/{}/data/temp_data/images'.format(self.pipeline_name))
            os.mkdir('pipelines/{}/data/temp_data/labels'.format(self.pipeline_name))

        frame = self.cap.read()

        cv2.imwrite('pipelines/{}/data/temp_data/images/img_{}.png'.format(self.pipeline_name, self.image_index),
                    frame[1])

    def save_image_data(self):
        # Opening current label file
        with open('pipelines/{}/data/temp_data/labels/label_{}.txt'.format(self.pipeline_name, self.current_image),
                  'w') as file:
            # Starting loop to write each box to file
            for key, value in self.rects.items():
                # Getting class name but not it's ID because image classes could change during labeling
                class_name = value[3]

                # Bringing X1Y1X2Y2 coordinates to form that YOLO model could use it
                center_x = int((value[2][0] + value[2][2]) / 2) / 1280
                center_y = int((value[2][1] + value[2][3]) / 2) / 720
                width = int(value[2][2] - value[2][0]) / 1280
                height = int(value[2][3] - value[2][1]) / 720

                # Writing current line to file
                file.write('{} {} {} {} {} \n'.format(class_name, center_x, center_y, width, height))

        self.image_count_label.config(text='{}/50 images labeled'.format(self.image_listbox.size()))

        if self.image_listbox.size() >= 50:
            self.finish_button['state'] = 'normal'

        self.isTakingSnapshot = False

    def switch_image_alert(self):
        if (self.image_index != self.current_image and self.rects != self.original_rects) or self.isTakingSnapshot:
            save_menu = tkinter.Toplevel(self.root)
            save_menu.title('Alert!')

            label = tkinter.Label(save_menu, text='Are you sure you want to leave unsaved image?')
            label.grid(row=0, column=0, columnspan=3)

            tkinter.Button(save_menu, text='Save',
                           command=lambda: [self.save_image_data(), self.switch_image(), save_menu.destroy()]).grid(
                row=1, column=0)
            if self.isTakingSnapshot:
                tkinter.Button(save_menu, text='Leave',
                               command=lambda: [self.abort_snapshot(), self.switch_image(), save_menu.destroy()]).grid(
                    row=1, column=1)
            else:
                tkinter.Button(save_menu, text='Leave',
                               command=lambda: [self.switch_image(), save_menu.destroy()]).grid(row=1, column=1)

            tkinter.Button(save_menu, text='Cancel', command=save_menu.destroy).grid(row=1, column=2)

            self.root.wait_window(save_menu)
        else:
            self.switch_image()

    def switch_image(self):
        # Making Save and Delete buttons active while Taking Snapshot
        self.take_snapshot_button['state'] = 'disabled'
        self.abort_button['state'] = 'normal'
        self.next_button['state'] = 'normal'

        # Changing Next button text to Save and Abort button to Delete
        self.next_button['text'] = 'Save'
        self.abort_button['text'] = 'Delete'

        # Stopping live stream from webcam
        self.thread.abort()

        # Deleting already existing boxes
        for key, value in self.rects.items():
            self.canvas.delete(value[0])
            self.canvas.delete(value[1])

        # Clearing boxes list
        self.boxes_listbox.delete(0, tkinter.END)

        # Clearing rects dictionary
        self.rects = {}

        # Getting id of image that user was clicked on
        image_id = int(self.image_listbox.get(self.image_listbox.curselection()[0]).split(' ')[1][1:])

        # Setting current image id to class variable self.current_image so other methods could use that information
        self.current_image = image_id

        self.image_listbox_image_id = self.image_listbox.curselection()[0]

        # Changing image in the canvas
        image = cv2.imread('pipelines/{}/data/temp_data/images/img_{}.png'.format(self.pipeline_name, image_id))
        img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        imgTk = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, image=imgTk, anchor=tkinter.NW)

        # Opening current image label file
        label = open('pipelines/{}/data/temp_data/labels/label_{}.txt'.format(self.pipeline_name, image_id), 'r')

        # Initializing index that represent id of box in image
        index = 0

        # Starting while loop
        while label:
            # Reading new line
            line = label.readline()

            # Exiting loop if line is empty
            if line == "":
                break

            # Splitting received row to separate pieces
            line = line.split(' ')

            # Restoring coordinates to pixels
            x1 = int(float(line[1]) * 1280) - int((float(line[3]) / 2) * 1280)
            y1 = int(float(line[2]) * 720) - int((float(line[4]) / 2) * 720)
            x2 = int(float(line[1]) * 1280) + int((float(line[3]) / 2) * 1280)
            y2 = int(float(line[2]) * 720) + int((float(line[4]) / 2) * 720)

            # Adding box and label to image and at the same moment adding those objects to self.rects dictionary
            self.rects[index] = [self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2),
                                 self.canvas.create_text(x1 + 50, y1 - 20, fill='green',
                                                         font='Helvetica 12 bold',
                                                         text='Box #{} - {}'.format(index, line[0])),
                                 [x1, y1, x2, y2],
                                 line[0]]
            self.boxes_listbox.insert(tkinter.END, 'Box #{} - {}'.format(index, line[0]))

            # Increasing index by 1
            index += 1

        self.original_rects = self.rects

        self.isTakingSnapshot = False

    @worker
    def update_canvas(self):
        while True:
            _, self.frame = self.cap.read()

            self.img = Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
            self.imgTk = ImageTk.PhotoImage(image=self.img)

            self.canvas.create_image(0, 0, image=self.imgTk, anchor=tkinter.NW)
            self.canvas.image = self.imgTk
