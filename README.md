# HardSubExtract

HardSubExtract (or Hardcoded Subtitle Extractor) is a command line interface (CLI) utility using Python and PaddleOCR to extract hardcoded subtitles from a video file. Support for most major video file containers/codecs and languages.

## Prerequisites

- Python
- PaddleOCR

## Installation

Install the necessary dependencies

```
 pip install paddlepaddle paddleocr opencv-python numpy matplotlib tkinter pillow
```

Install HardSubExtract

```
pip install git+https://github.com/cavalia88/HardSubExtract.git
```

## General Usage

- Use the Video_Frame_Scroller to open the video with the hardcoded subtitles and draw the boundary box over the subtitles to determine the relevant dimensions. Refer to section below on Video Frame Scroller.
- Run the CLI command line to extract the hardcoded subtitles.
- A window will open up with 6 sample frames from the video to show where the bounding box covers.

  ![](https://holocron.so/uploads/a550e662-frame-preview-small.jpg.jpeg)

- Close the window and user will be prompted if you want to proceed. If user is satisfied with the coverage of the bounding box over the hardcoded subtitles, input "yes" or "y" to proceed with image OCR processing.
- Program will run and once completed, a new srt file will be created in the designated path.

## Sample CLI Commands

- Extract English subtitles from sample.mkv. Subtitle file will follow the name of video file, sample.srt

  ```
  python HardSubExtract.py sample.mkv --lang en 
  ```

- Extract English subtitles from sample.mkv with a sampling rate of 1 frame per second. Subtitle file will follow the name of video file, sample.srt

  ```
  python HardSubExtract.py sample.mkv --lang en --fps 1
  ```

- Extract Chinese subtitles from sample.mp4 with a sampling rate of 12 frames per second. Subtitle file to be named sample_chinese.srt

  ```
  python HardSubExtract.py sample.mp4 sample_chinese.srt --lang ch --fps 12
  ```

- Extract  Japanese subtitles from video.mp4 with a sampling rate of 5 frames per second and user specified bounding box dimensions. Subtitle file to be named video.srt

  ```
  python HardSubExtract.py video.mp4 --lang japan --fps 5 --top_percent 83 --bottom_percent 99 --left_percent 20 --right_percent 80
  ```

- Extract Japanese subtitles from video.mp4 with a sampling rate of 5 frames per second and user specified (i) bounding box dimensions and (ii) start and end times. First 60 seconds of the video clip will be processed for subtitles, and the subtitle file to be named video.srt.

  ```
  python HardSubExtract.py video.mp4 --lang japan --fps 5 --start_time 0 --end_time 60 --top_percent 83 --bottom_percent 99 --left_percent 20 --right_percent 80
  ```

## Video Frame Scroller

- To facilitate the determination of the bounding box dimensions, I have created a separate program, Video Frame Scroller. This will allow users to scroll through the different frames of a video clip and draw out a bounding box over the hardcoded subtitles (with a mouse).

  ![](https://holocron.so/uploads/58b92254-vfs-1-small.jpg.jpeg)


- Once the bounding box is drawn, the corresponding values for the bounding box will be displayed on the upper left corner of the frame. Users can use these values as input for top_percent, bottom_percent, left_percent and right_percent for the main HardSubExtract program.

  ![](https://holocron.so/uploads/58ad0dfc-vfs-2-small.jpg.jpeg)


- To run the Video Frame Scroller:

  ```
  python Video_Frame_Scroller.py
  ```

## Parameters

| Parameters           | Details                                                                                                                                                                                                                                                                                                                                                                                                                               | Default Values                                                                                                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| video_path           | The full path and name of the video file.                                                                                                                                                                                                                                                                                                                                                                                             | Minimum required is the video file name (e.g. sample.mp4). If path is not provided, it will be taken to be the path where the python executable file is.                           |
| output_path          | The full path and name of the srt file that the subtitles should be output to.                                                                                                                                                                                                                                                                                                                                                        | If not provided, subtitles will follow the name of the video file (e.g. sample.mp4 will product sample.srt) and will be created in the folder where the python executable file is. |
| lang                 | The language code of the hardcoded subtitles in the video. Refer to list below for language codes.                                                                                                                                                                                                                                                                                                                                    | en                                                                                                                                                                                 |
| fps                  | Frames extracted per second. The sampling rate that frames are extracted from the video for checking for subtitles with OCR. The higher the fps, the more accurate the timing of the subtitle, but at the cost of longer processing times.                                                                                                                                                                                            | 5                                                                                                                                                                                  |
| start_time           | The point in time of the video clip to start extracting subtitles (in seconds).                                                                                                                                                                                                                                                                                                                                                       | 0                                                                                                                                                                                  |
| end_time             | The point in time of the video clip to stop extracting subtitles (in seconds).                                                                                                                                                                                                                                                                                                                                                        | None (i.e. unless specified by user, default is the end time of the entire video clip).                                                                                            |
| top_percent          | The top boundary of the bounding box by which OCR will be processed for each frame. Top of the video frame is 0% and bottom of the video frame is 100%.                                                                                                                                                                                                                                                                               | 66                                                                                                                                                                                 |
| bottom_percent       | The bottom boundary of the bounding box by which OCR will be processed for each frame. Top of the video frame is 0% and bottom of the video frame is 100%.                                                                                                                                                                                                                                                                            | 95                                                                                                                                                                                 |
| left_percent         | The left boundary of the bounding box by which OCR will be processed for each frame. Left edge of the video frame is 0% and right edge the video frame is 100%.                                                                                                                                                                                                                                                                       | 10                                                                                                                                                                                 |
| right_percent        | The right boundary of the bounding box by which OCR will be processed for each frame. Left edge of the video frame is 0% and right edge the video frame is 100%.                                                                                                                                                                                                                                                                      | 90                                                                                                                                                                                 |
| skip_sample_frames   | To skip the generation of the sample frames and user prompt (to proceed with subtitle extraction). Subtitle extraction will commence immediately if this flag is included.                                                                                                                                                                                                                                                            | Include this flag to skip both sample frame generation and user prompt.                                                                                                            |
| similarity_threshold | Based on the Jaccard similarity coefficient, a common measure of similarity between two sets. This is the threshold factor for combining subtitles extracted from similar frames in the video to form the srt file. Ranges from values of 0 to 1.  The higher the value set, the more similar two adjacents subtitles have to be for them to be combined. Higher values result in more subtitles with minor differences between them. | 0.8                                                                                                                                                                                |
| time_threshold       | This is the time threshold (in seconds) for combining subtitles extracted from similar frames in the video to form the srt file.The time gap between subtitles has to be less time threshold to be considered for combination.                                                                                                                                                                                                        | 1.0                                                                                                                                                                                |

## Language Codes

- English - en
- French - fr
- German - german
- Japanese - japan
- Korean - korean
- Chinese - ch
- Chinese Traditional - ch_tra
- Italian - it
- Spanish - es
- Portuguese - pt
- Malay - ms
- Codes for other supported languages can be found on the PaddleOCR github page

## Notes

- This program is quite CPU intensive so it may take some time to extract the subtitles from a video
- PaddleOCR supports GPU acceleration with Nvidia GPUs. However, as I do not have a Nvidia GPU, this is a pure CPU implementation
- To speed up processing speed, you can try to reduce the fps (between 1-5 fps) and/or minimize the bounding box size so the OCR has to process less of each frame. Another possiblity is to resize the original video to a lower resolution (using some GPU enabled media encoder) before attempting to extract subtitles.

