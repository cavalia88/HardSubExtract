# Version 1.0 - 01Sep24

import cv2
import numpy as np
from paddleocr import PaddleOCR
import time
import random
import matplotlib.pyplot as plt
import os
import argparse

    
def extract_subtitles(video_path, output_path, lang='en', fps=5, start_time=1, end_time=None, 
                      top_percent=66, bottom_percent=95, left_percent=10, right_percent=90):
    
    # If output_path is not provided, use the video file name with .srt extension
    if output_path is None:
        output_path = os.path.splitext(video_path)[0] + '.srt'
        
    # Set split_words based on language
    split_words = lang not in ['japan', 'korean', 'ch', 'chinese_cht']
    print(f"Using language: {lang}, Word spacing: {split_words}")

    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang=lang)
    
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    # Get video properties
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = video.get(cv2.CAP_PROP_FPS)
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Set end time if not specified
    if end_time is None:
        end_time = total_frames / video_fps

    # Calculate region of interest
    top = int(frame_height * top_percent / 100)
    bottom = int(frame_height * bottom_percent / 100)
    left = int(frame_width * left_percent / 100)
    right = int(frame_width * right_percent / 100)
    
    subtitles = []
    processed_frames = 0
    
    start_process_time = time.time()
    
    # Set the starting position of the video
    video.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
    
    # Calculate frame interval based on fps
    frame_interval = int(video_fps / fps)
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        current_time = video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if current_time >= end_time:
            break

        # Process frames based on the calculated interval
        if processed_frames % frame_interval == 0:
            # Crop the frame to the specified region
            roi = frame[top:bottom, left:right]
            
            try:
                # Perform OCR on the region of interest
                result = ocr.ocr(roi, cls=True)
                
                if result and isinstance(result[0], list):
                    text = ' '.join([line[1][0] for line in result[0] if isinstance(line, list) and len(line) > 1])
                    if text:
                        subtitle_start_time = current_time
                        subtitle_end_time = subtitle_start_time + (frame_interval / video_fps)
                        subtitles.append((subtitle_start_time, subtitle_end_time, text))
            except Exception as e:
                print(f"Error processing frame at {current_time:.2f} seconds: {str(e)}")
        
        processed_frames += 1
        if processed_frames % 100 == 0:
            print(f"Processed {processed_frames} frames, current time: {current_time:.2f} seconds")
    
    video.release()
    
    # Merge similar subtitles
    merged_subtitles = merge_similar_subtitles(subtitles, split_words, time_threshold=args.time_threshold, similarity_threshold=args.similarity_threshold)
    
    # Write subtitles to SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, (start, end, text) in enumerate(merged_subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")
    
    end_process_time = time.time()
    total_process_time = end_process_time - start_process_time
    processed_video_duration = end_time - start_time
    
    print(f"\nProcessing Statistics:")
    print(f"Total processing time: {total_process_time:.2f} seconds")
    print(f"Video duration processed: {processed_video_duration:.2f} seconds")
    print(f"Processing speed: {processed_video_duration/total_process_time:.2f}x real-time")
    print(f"Time to process 1 minute of video: {(total_process_time/processed_video_duration)*60:.2f} seconds")

def format_time(seconds):
    millisec = int((seconds - int(seconds)) * 1000)
    return f"{time.strftime('%H:%M:%S', time.gmtime(seconds))},{millisec:03d}"

def display_combined_frames(frames_with_boxes):
    # Stack the frames in a 3x2 grid (3 across, 2 down)
    row1 = np.hstack(frames_with_boxes[:3])  # First 3 images
    row2 = np.hstack(frames_with_boxes[3:])  # Last 3 images
    combined_image = np.vstack([row1, row2])  # Stack the two rows vertically
    
    # Resize the image to fit the screen
    screen_height, screen_width = 1080, 1920  # Adjust these to your screen resolution
    scale = min(screen_width / combined_image.shape[1], screen_height / combined_image.shape[0])
    resized_image = cv2.resize(combined_image, (0, 0), fx=scale, fy=scale)

    # Display the combined image
    cv2.imshow("Preview Frames", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def extract_sample_frames(video_path, num_samples, top_percent, bottom_percent, left_percent, right_percent):
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate region of interest
    top = int(frame_height * top_percent / 100)
    bottom = int(frame_height * bottom_percent / 100)
    left = int(frame_width * left_percent / 100)
    right = int(frame_width * right_percent / 100)

    sample_frames = []
    for i in range(num_samples):
        random_frame = random.randint(0, total_frames - 1)
        video.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
        ret, frame = video.read()
        if ret:
            # Draw thick red rectangle on the frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 10)
            sample_frames.append(frame)

    video.release()
    return sample_frames

def merge_similar_subtitles(subtitles, split_words, time_threshold, similarity_threshold):
    merged = []
    i = 0
    while i < len(subtitles):
        current = subtitles[i]
        j = i + 1
        merged_text = current[2]
        end_time = current[1]
        
        while j < len(subtitles):
            next_sub = subtitles[j]
            if next_sub[0] - end_time > time_threshold:
                break
            
            # Check similarity
            if split_words:
                current_words = set(current[2].split())
                next_words = set(next_sub[2].split())
            else:
                current_words = set(current[2])
                next_words = set(next_sub[2])
            
            similarity = len(current_words.intersection(next_words)) / len(current_words.union(next_words))
                       
            if similarity >= similarity_threshold:
                merged_text = next_sub[2]  # Replace merged_text with next subtitle's text
                end_time = next_sub[1]
                j += 1
            else:
                break
        
        merged.append((current[0], end_time, merged_text))
        i = j
    
    return merged

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract subtitles from a video file.")
    parser.add_argument("video_path", help="Path to the input video file")
    parser.add_argument("output_path", nargs='?', default=None, help="Path for the output SRT file (optional)")
    parser.add_argument("--lang", default="en", help="Language code (e.g., 'en' for English, 'ch' for Chinese)")
    parser.add_argument("--fps", type=float, default=5, help="Processing frame rate")
    parser.add_argument("--start_time", type=float, default=0, help="Start time in seconds")
    parser.add_argument("--end_time", type=float, help="End time in seconds")
    parser.add_argument("--top_percent", type=float, default=66, help="Top boundary (percentage of frame height)")
    parser.add_argument("--bottom_percent", type=float, default=95, help="Bottom boundary (percentage of frame height)")
    parser.add_argument("--left_percent", type=float, default=10, help="Left boundary (percentage of frame width)")
    parser.add_argument("--right_percent", type=float, default=90, help="Right boundary (percentage of frame width)")
    parser.add_argument("--skip_sample_frames", action="store_true", help="Skip extracting and displaying sample frames (also skips user prompt)")
    parser.add_argument("--similarity_threshold", type=float, default=0.8, help="Similarity threshold for merging subtitles")
    parser.add_argument("--time_threshold", type=float, default=1.0, help="Time threshold for merging subtitles")
    
    args = parser.parse_args()

    if not args.skip_sample_frames:
        sample_frames = extract_sample_frames(args.video_path, 6, args.top_percent, args.bottom_percent, args.left_percent, args.right_percent)
        display_combined_frames(sample_frames)
        
        proceed = input("Do you want to proceed with processing? (yes/no): ").lower()
        if proceed not in ['yes', 'y']:
            print("Processing cancelled by user.")
            exit()
    
    # Call extract_subtitles with the parsed arguments
    extract_subtitles(args.video_path, args.output_path, args.lang, args.fps, args.start_time, args.end_time,
                      args.top_percent, args.bottom_percent, args.left_percent, args.right_percent)
    print("Subtitle extraction complete.")
