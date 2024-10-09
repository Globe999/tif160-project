import cv2
import os

def extract_frames(video_path, output_folder, target_fps):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Load the video file
    video_capture = cv2.VideoCapture(video_path)
    
    # Check if the video opened successfully
    if not video_capture.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get original FPS of the video
    original_fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps // target_fps)  # How many frames to skip

    frame_count = 0
    saved_frame_count = 106
    success, frame = video_capture.read()
    
    while success:
        # Save every 'frame_interval' frame
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:05d}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Saving frame {saved_frame_count} to {frame_filename}")
            saved_frame_count += 1
        
        # Read the next frame from the video
        success, frame = video_capture.read()
        frame_count += 1
    
    # Release the video capture object
    video_capture.release()
    print(f"All frames saved in {output_folder}")

if __name__ == "__main__":
    # Use raw string or double backslashes to avoid unicode escape issues
    video_file = r'C:\Users\oskar\OneDrive\Dokument\repo\tif160-project\2024-10-09-10-51-06.mp4'
    output_dir = 'frames_output'  # Folder to save the frames
    target_fps = 5  # Set the desired FPS (lower than the original FPS)
    
    extract_frames(video_file, output_dir, target_fps)
