# Version 1.0 - 01Sep24

import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def open_video():
    global cap, total_frames, frame_width, frame_height, original_width, original_height
    filepath = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.ts")])
    if filepath:
        cap = cv2.VideoCapture(filepath)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_width = min(original_width, 1280)
        frame_height = int(original_height * (frame_width / original_width))
        scale.config(to=total_frames-1)
        show_frame(0)

def show_frame(frame_number):
    global cap, canvas, img_label, frame, bbox, dragging, frame_width, frame_height, original_width, original_height
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resize the frame if its width is greater than 1280 pixels
        if original_width > 1280:
            frame = cv2.resize(frame, (frame_width, frame_height))
        draw_frame = frame.copy()
        if bbox:
            cv2.rectangle(draw_frame, bbox[0], bbox[1], (255, 0, 0), 2)
            # Calculate ROI percentages based on original dimensions
            left_percent = bbox[0][0] / frame_width * 100
            top_percent = bbox[0][1] / frame_height * 100
            right_percent = bbox[1][0] / frame_width * 100
            bottom_percent = bbox[1][1] / frame_height * 100
            # Overlay ROI percentages at the top right corner
            text = f"Top: {top_percent:.1f}% Bottom: {bottom_percent:.1f}% Left: {left_percent:.1f}% Right: {right_percent:.1f}%"
            cv2.putText(draw_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        img = Image.fromarray(draw_frame)
        imgtk = ImageTk.PhotoImage(image=img)
        img_label.config(image=imgtk)
        img_label.image = imgtk

def resize_frame(event):
    show_frame(int(scale.get()))

def on_scroll(value):
    frame_number = int(value)
    show_frame(frame_number)

def start_draw(event):
    global start_x, start_y, bbox, dragging
    start_x, start_y = event.x, event.y
    dragging = True
    bbox = [(start_x, start_y), (start_x, start_y)]  # Start with a point
    show_frame(int(scale.get()))

def update_draw(event):
    global bbox
    if dragging:
        end_x, end_y = event.x, event.y
        bbox = [(start_x, start_y), (end_x, end_y)]
        show_frame(int(scale.get()))

def end_draw(event):
    global dragging
    dragging = False
    update_draw(event)  # Finalize the box

def clear_bbox(event):
    global bbox, dragging
    bbox = None
    dragging = False
    show_frame(int(scale.get()))

# Setup GUI
root = tk.Tk()
root.title("Video Frame Scroller")
root.resizable(False, False)  # Prevent window from being resized

# Video display area
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()
img_label = tk.Label(canvas)
img_label.pack()

# Scroll bar for frame navigation
scale = tk.Scale(root, from_=0, to=0, orient=tk.HORIZONTAL, length=800, command=on_scroll)
scale.pack()

# Open video button
open_button = tk.Button(root, text="Open Video", command=open_video)
open_button.pack()

# Initialize variables
cap = None
frame = None
bbox = None
start_x = start_y = 0
dragging = False
frame_width = frame_height = 0
original_width = original_height = 0

# Bind mouse events to canvas
img_label.bind("<Button-1>", start_draw)
img_label.bind("<B1-Motion>", update_draw)
img_label.bind("<ButtonRelease-1>", end_draw)
img_label.bind("<Button-3>", clear_bbox)  # Right-click to clear the bounding box

root.mainloop()
