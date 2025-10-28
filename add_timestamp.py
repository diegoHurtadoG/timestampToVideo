import xml.etree.ElementTree as ET
from moviepy.editor import VideoFileClip
import datetime
from dateutil import parser
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import multiprocessing
from tqdm import tqdm

def add_timestamp_to_video(video_path, xml_path, output_path):
    """
    Adds a running timestamp to a video file, styled to look like a classic video recorder.
    """
    # Parse the XML file to get the creation date
    try:
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
            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)
            current_time = creation_date + datetime.timedelta(seconds=t)
            time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
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

            margin = 100
            x = video.size[0] - text_width - margin
            y = video.size[1] - text_height - margin
            draw.text((x, y), time_str, font=font, fill=(255, 255, 255))

            # Convert the modified PIL image back to a numpy array and return it
            return np.array(img)

        video_with_timestamp = video.fl(draw_timestamp_on_frame)
        video_with_timestamp.write_videofile(
            output_path,
            fps=video.fps,
            codec='libx264',
            threads=2, # Can give each ffmpeg 2 threads now
            preset='medium',
            audio_codec='aac',
            logger=None
        )
        
        video.close()
        video_with_timestamp.close()
        
        print(f"✅ Finished process for: {os.path.basename(video_path)}")

    except Exception as e:
        # If anything goes wrong with this one video, print the error and move on.
        print(f"❌ ERROR processing {os.path.basename(video_path)}: {e}")


if __name__ == "__main__":
    input_dir = "./inputs"
    output_dir = "./outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. First, we gather all the jobs that need to be done.
    jobs = []
    print("🔎 Searching for videos recursively...")
    for current_dir, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if filename.lower().endswith(".mp4"):
                video_path = os.path.join(current_dir, filename)
                
                video_name_base = filename[:-4]
                xml_path = os.path.join(current_dir, f"{video_name_base}M01.XML")

                output_sub_dir = current_dir.replace(input_dir, output_dir, 1)
                
                os.makedirs(output_sub_dir, exist_ok=True)
                
                output_path = os.path.join(output_sub_dir, f"{video_name_base}_timestamp.MP4")

                if os.path.exists(xml_path):
                    jobs.append((video_path, xml_path, output_path))
                else:
                    tqdm.write(f"⚠️  Warning: Skipping '{video_path}' (XML not found).")

    if not jobs:
        print("No video files found to process.")
    else:
        # 2. We determine how many CPU cores to use.
        # Using all available cores for maximum speed.
        # num_processes = multiprocessing.cpu_count()
        num_processes = multiprocessing.cpu_count() // 12
        print(f"\nFound {len(jobs)} videos to process.")
        print(f"Starting a pool of {num_processes} worker processes...")
        
        if num_processes > 1:
            # Use the efficient parallel pool for multiple workers
            with multiprocessing.Pool(processes=num_processes) as pool:
                # tqdm will wrap the pool operation to create a live progress bar
                list(tqdm(pool.starmap(add_timestamp_to_video, jobs), total=len(jobs)))
        else:
            # Use a simple, clean for loop for a single worker
            # tqdm wraps the 'jobs' list to show progress as we iterate through it
            for job_args in tqdm(jobs):
                add_timestamp_to_video(*job_args) # The '*' unpacks the arguments
            
        print("\n🎉 Batch process complete! 🎉")