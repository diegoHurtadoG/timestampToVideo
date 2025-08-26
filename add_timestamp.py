import xml.etree.ElementTree as ET
from moviepy.editor import VideoFileClip
import datetime
from dateutil import parser
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def add_timestamp_to_video(video_path, xml_path, output_path):
    """
    Adds a running timestamp to a video file by modifying each frame directly.
    """
    # --- This part remains the same ---
    # Parse the XML file to get the creation date
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    namespace = {"ns": "urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00"}
    creation_date_str = root.find("ns:CreationDate", namespace).get("value")
    creation_date = parser.isoparse(creation_date_str)
    
    # Load the video clip
    video = VideoFileClip(video_path)

    # --- Major Change Here ---
    # We define a function that will process each frame of the video.
    # The function receives get_frame (gf) and the current time (t).
    def draw_timestamp_on_frame(get_frame, t):
        # Get the original video frame at time t
        frame = get_frame(t)
        
        # Convert the numpy array frame to a PIL Image to draw on it
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img)

        # Generate the timestamp text, including milliseconds for precision
        current_time = creation_date + datetime.timedelta(seconds=t)
        # The .%f adds microseconds, we slice it to get milliseconds
        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Choose a font and size
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        # Get text size to calculate position
        bbox = draw.textbbox((0, 0), time_str, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position the text at the bottom center
        x = (video.size[0] - text_width) / 2
        y = video.size[1] - text_height - 20 # Added a little more padding from bottom

        # Draw the text directly on the frame image.
        # The fill color is now RGB (255, 255, 255) since the image has no alpha channel.
        draw.text((x, y), time_str, font=font, fill=(255, 255, 255))

        # Convert the modified PIL image back to a numpy array and return it
        return np.array(img)

    # Apply the frame-processing function to the video.
    # .fl() creates a new clip where each frame is the result of our function.
    video_with_timestamp = video.fl(draw_timestamp_on_frame)
    
    # Write the result to a file (same as before)
    video_with_timestamp.write_videofile(
        output_path,
        fps=video.fps,
        codec='libx264',
        threads=4,
        preset='medium',
        audio_codec='aac'
    )

if __name__ == "__main__":
    video_file = "/home/diego/video_timestamp/C0002.MP4"
    xml_file = "/home/diego/video_timestamp/C0002M01.XML"
    output_file = "/home/diego/video_timestamp/C0002_with_timestamp.MP4"
    
    add_timestamp_to_video(video_file, xml_file, output_file)
    print(f"Video saved to {output_file}")