import xml.etree.ElementTree as ET
from moviepy.editor import VideoFileClip
import datetime
from dateutil import parser
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def add_timestamp_to_video(video_path, xml_path, output_path):
    """
    Adds a running timestamp to a video file, styled to look like a classic video recorder.
    """
    # Parse the XML file to get the creation date
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    namespace = {"ns": "urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00"}
    creation_date_str = root.find("ns:CreationDate", namespace).get("value")
    creation_date = parser.isoparse(creation_date_str)
    
    # Load the video clip
    video = VideoFileClip(video_path)

    # This function will process each frame of the video.
    def draw_timestamp_on_frame(get_frame, t):
        # Get the original video frame at time t
        frame = get_frame(t)
        
        # Convert the numpy array frame to a PIL Image to draw on it
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img)

        # --- CHANGE #1: Timestamp format without milliseconds ---
        current_time = creation_date + datetime.timedelta(seconds=t)
        time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # --- CHANGE #2: Bigger, monospaced font for a VCR look ---
        try:
            # Using a bold, monospaced font is great for this style. Increase 70 to make it bigger.
            font = ImageFont.truetype("./DejaVuSansMono-Bold.ttf", 110) 
        except IOError:
            # Fallback to a default monospaced font if the above isn't found
            font = ImageFont.load_default()

        # Get text size to calculate position
        bbox = draw.textbbox((0, 0), time_str, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # --- CHANGE #3: Position the text in the bottom-right corner ---
        margin = 100
        x = video.size[0] - text_width - margin
        y = video.size[1] - text_height - margin

        # Draw the text directly on the frame image.
        draw.text((x, y), time_str, font=font, fill=(255, 255, 255))

        # Convert the modified PIL image back to a numpy array and return it
        return np.array(img)

    # Apply the frame-processing function to the video.
    video_with_timestamp = video.fl(draw_timestamp_on_frame)
    
    # Write the result to a file
    video_with_timestamp.write_videofile(
        output_path,
        fps=video.fps,
        codec='libx264',
        threads=4,
        preset='medium',
        audio_codec='aac'
    )


if __name__ == "__main__":
    # Define the input and output directories
    input_dir = "inputs"
    output_dir = "outputs"
    
    # Create the output directory if it doesn't already exist
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting batch process...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Get a list of all files in the input directory
    files_in_input = os.listdir(input_dir)
    
    # Loop through every file
    for filename in files_in_input:
        # Check if the file is an MP4 video
        if filename.lower().endswith(".mp4"):
            # Construct the full paths for the video and XML files
            video_name_base = filename[:-4] # Removes the .mp4 extension
            
            video_path = os.path.join(input_dir, filename)
            xml_path = os.path.join(input_dir, f"{video_name_base}M01.XML")
            output_path = os.path.join(output_dir, f"{video_name_base}_timestamp.MP4")
            
            # IMPORTANT: Check if the matching XML file actually exists
            if not os.path.exists(xml_path):
                print(f"⚠️  Warning: Skipping '{video_path}' because its XML file was not found.")
                continue # Skip to the next file in the loop

            print(f"Processing '{filename}'...")
            
            # Call the function to process this video
            add_timestamp_to_video(video_path, xml_path, output_path)
            
            print(f"✅  Finished: Saved to '{output_path}'")
            
    print("\nBatch process complete!")