
import xml.etree.ElementTree as ET
from moviepy.editor import *
import datetime
from dateutil import parser
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def add_timestamp_to_video(video_path, xml_path, output_path):
    """
    Adds a running timestamp to a video file based on the metadata from an XML file.
    """
    # Parse the XML file to get the creation date
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    namespace = {"ns": "urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00"}
    creation_date_str = root.find("ns:CreationDate", namespace).get("value")
    creation_date = parser.isoparse(creation_date_str)
    
    # Load the video clip
    video = VideoFileClip(video_path)
    fps = video.fps

    def make_frame(t):
        # Create a blank image with an alpha channel
        img = Image.new('RGB', video.size, (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Generate the timestamp text
        current_time = creation_date + datetime.timedelta(seconds=t)
        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # Choose a font and size
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        # Get text size using textbbox
        bbox = draw.textbbox((0, 0), time_str, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position the text at the bottom center
        x = (video.size[0] - text_width) / 2
        y = video.size[1] - text_height - 10

        # Draw the text on the image
        draw.text((x, y), time_str, font=font, fill=(255, 255, 255, 255))

        # Convert the PIL image to a numpy array
        return np.array(img)

    # Create a VideoClip from the make_frame function
    txt_clip = VideoClip(make_frame, duration=video.duration)

    # Overlay the text clip on the video
    video_with_timestamp = CompositeVideoClip([video, txt_clip.set_pos("center")])
    
    # Write the result to a file
    video_with_timestamp.write_videofile(output_path, fps=fps, codec='libx264', threads=4, preset='medium', audio_codec='aac')

if __name__ == "__main__":
    video_file = "/home/diego/video_timestamp/C0002.MP4"
    xml_file = "/home/diego/video_timestamp/C0002M01.XML"
    output_file = "/home/diego/video_timestamp/C0002_with_timestamp.MP4"
    
    add_timestamp_to_video(video_file, xml_file, output_file)
    print(f"Video saved to {output_file}")
