import queue
import threading
import tkinter
import cv2
from PIL import Image, ImageTk


class CreatePipeline:
    def __init__(self, pipeline, root):
        self.boxes_listbox = None
        self.thread = None
        self.finish_button = None
        self.next_button = None
        self.abort_button = None
        self.take_snapshot_button = None
        self.image_listbox = None

        self.pipeline_sequence = pipeline
        self.root = root

        self.boxes_cords = []

        self.canvas = None

        self.q = queue.Queue()
        self.q.put(True)

        self.start_x = None
        self.start_y = None

        self.rects = {}

        self.rect = None

        self.rect_count = 0

        self.x = self.y = 0

        self.curX = self.curY = 0

        self.cap = cv2.VideoCapture(0)

        self.terminal()

    def terminal(self):
        for action in self.pipeline_sequence:
            if action == 'Find item':
                self.execute_find_item()

    def execute_find_item(self):
        self.labeling_window = tkinter.Toplevel(self.root)
        self.labeling_window.title('Labelimg')

        self.image_listbox = tkinter.Listbox(self.labeling_window, height=40)
        self.image_listbox.grid(row=0, column=0, rowspan=5)

        self.canvas = tkinter.Canvas(self.labeling_window, width=1280, height=720)
        self.canvas.grid(row=0, column=1, rowspan=5)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.boxes_listbox = tkinter.Listbox(self.labeling_window)
        self.boxes_listbox.grid(row=0, column=2)
        self.boxes_listbox.bind('<Double-Button-1>', lambda x: self.delete_box(self.boxes_listbox))

        self.take_snapshot_button = tkinter.Button(self.labeling_window, text='Take snapshot', command=self.take_snapshot)
        self.take_snapshot_button.grid(row=1, column=2)

        self.abort_button = tkinter.Button(self.labeling_window, text='Abort', command=self.abort_snapshot)
        self.abort_button['state'] = 'disabled'
        self.abort_button.grid(row=2, column=2)

        self.next_button = tkinter.Button(self.labeling_window, text='Next image')
        self.next_button['state'] = 'disabled'
        self.next_button.grid(row=3, column=2)

        self.finish_button = tkinter.Button(self.labeling_window, text='Finish')
        self.finish_button['state'] = 'disabled'
        self.finish_button.grid(row=4, column=2)

        self.thread = threading.Thread(target=self.update_canvas)
        self.thread.start()

    def delete_box(self, listbox):
        index = int(listbox.get(listbox.curselection()[0]).split(' ')[1][1:])
        self.canvas.delete(self.rects[index][0])
        self.canvas.delete(self.rects[index][1])
        listbox.delete(listbox.curselection()[0])
        del self.rects[index]

    def on_button_press(self, event):
        if self.abort_button['state'] == 'normal':
            # inside_box = False
            # for cords in self.boxes_cords:
            #     if
            self.start_x = event.x
            self.start_y = event.y

            self.rect = self.canvas.create_rectangle(self.x, self.y, 0, 0, outline="green", width=2)

    def on_move_press(self, event):
        self.curX, self.curY = (event.x, event.y)

        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        if self.abort_button['state'] == 'normal':
            naming_window = tkinter.Toplevel(self.root)
            naming_window.title('Name box')

            self.entry = tkinter.Entry(naming_window)
            self.entry.grid(row=0, column=0, columnspan=2)

            cancel_button = tkinter.Button(naming_window, text='Cancel', command=lambda: [self.remove_rect(self.rect), naming_window.destroy()])
            cancel_button.grid(row=1, column=0)

            ok_button = tkinter.Button(naming_window, text='Ok', command=lambda: [self.add_rect(event), naming_window.destroy()])
            ok_button.grid(row=1, column=1)

    def remove_rect(self, rect):
        self.canvas.delete(rect)

    def add_rect(self, event):
        top_left = [self.curX if self.start_x > self.curX else self.start_x, self.curY if self.start_y > self.curY else self.start_y]
        bottom_right = [self.curX if self.start_x < self.curX else self.start_x, self.curY if self.start_y < self.curY else self.start_y]

        self.rects[self.rect_count] = [self.rect, self.canvas.create_text(top_left[0] + 50, top_left[1] - 20, fill='green', font='Helvetica 12 bold', text='Box #{} - {}'.format(self.rect_count, self.entry.get())), [top_left[0], top_left[1], bottom_right[0], bottom_right[1]]]
        self.boxes_listbox.insert(tkinter.END, 'Box #{} - {}'.format(self.rect_count, self.entry.get()))
        self.rect_count += 1

    def take_snapshot(self):
        self.take_snapshot_button['state'] = 'disabled'
        self.abort_button['state'] = 'normal'
        self.next_button['state'] = 'normal'

        self.rects = {}

        self.q.put(False)

    def abort_snapshot(self):
        self.take_snapshot_button['state'] = 'normal'
        self.abort_button['state'] = 'disabled'
        self.next_button['state'] = 'disabled'

        self.rects = {}

        self.q.put(True)

    def next_image(self):
        self.take_snapshot_button['state'] = 'normal'
        self.abort_button['state'] = 'disabled'
        self.next_button['state'] = 'disabled'

        self.q.put(True)



    def update_canvas(self):
        while True:
            if self.q.qsize() > 0:
                val = self.q.get()
            while val:
                if self.q.qsize() > 0:
                    val = self.q.get()
                _, self.frame = self.cap.read()

                self.img = Image.fromarray(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
                self.imgTk = ImageTk.PhotoImage(image=self.img)

                self.canvas.create_image(0, 0, image=self.imgTk, anchor=tkinter.NW)
                self.canvas.image = self.imgTk
