# video_sorter.py
import argparse, shutil, sys, pathlib, time, threading, queue
import vlc

def release_vlc_resources():
    """Force release of VLC resources and file handles"""
    import gc
    gc.collect()
    time.sleep(2.0)

def play_video_and_get_choice(path: pathlib.Path) -> str:
    # Create a VLC instance with separate process
    instance = vlc.Instance('--no-xlib')
    # Create a media player
    player = instance.media_player_new()
    # Set media
    media = instance.media_new(str(path))
    player.set_media(media)
    
    # Play the video
    player.play()
    
    # Wait for media to start playing
    time.sleep(1)
    duration = player.get_length() / 1000  # Convert to seconds
    if duration > 0:
        print(f"Video duration: {duration:.1f} seconds")
    
    # Queue for communication between threads
    result_queue = queue.Queue()
    
    # Function to get input from user in a separate thread
    def input_thread():
        print("\nPlaying video... Press 'y' to keep, 'n' to skip, or 'q' to quit.")
        while True:
            try:
                choice = input().strip().lower()
                if choice in ['y', 'n', 'q']:
                    result_queue.put(choice)
                    break
                else:
                    print("Please type y, n, or q.")
            except EOFError:
                # Handle EOF error (e.g., when input is redirected)
                time.sleep(0.5)
    
    # Start the input thread
    input_thread = threading.Thread(target=input_thread)
    input_thread.daemon = True
    input_thread.start()
    
    # Wait for either the video to finish or user input
    choice = None
    try:
        while player.is_playing() and result_queue.empty():
            time.sleep(0.1)
        
        # If we got here because of user input, get the choice
        if not result_queue.empty():
            choice = result_queue.get()
    finally:
        # Stop and release the player
        player.stop()
        # Release media
        media = None
        player = None
        instance = None
        # Force release of resources
        release_vlc_resources()
        
        # If video finished without user input, ask for decision
        if choice is None:
            print("\nVideo finished. Please make a choice:")
            while True:
                choice = input("[y] move  [n] skip  [q] quit : ").strip().lower()
                if choice in ['y', 'n', 'q']:
                    break
                else:
                    print("Please type y, n, or q.")
    
    return choice

def main(src_dir: pathlib.Path, dst_dir: pathlib.Path) -> None:
    videos = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi"})
    if not videos:
        print("No video files found."); return
    dst_dir.mkdir(parents=True, exist_ok=True)

    for vid in videos:
        print(f"\n▶️  {vid.name}")
        choice = play_video_and_get_choice(vid)
        
        if choice == "y":
            # Make multiple attempts to move the file
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Try to move the file
                    shutil.move(str(vid), dst_dir / vid.name)
                    print(f"→ moved to {dst_dir}")
                    break
                except PermissionError:
                    if attempt < max_attempts - 1:
                        # If file is still in use, try again with a longer delay
                        print(f"File is still in use. Attempt {attempt+1}/{max_attempts}. Waiting longer...")
                        # Force another release of resources
                        release_vlc_resources()
                    else:
                        print(f"Could not move file after {max_attempts} attempts.")
                        print("You may need to move this file manually.")
                except Exception as e:
                    print(f"Error moving file: {e}")
                    print("You may need to move this file manually.")
                    break
        elif choice == "n":
            print("→ left in place")
        elif choice == "q":
            print("Exiting…")
            sys.exit(0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Manual video sorter (y/n to move files).")
    ap.add_argument("--src", required=True, help="Source folder containing videos")
    ap.add_argument("--dst", required=True, help="Destination folder for accepted videos")
    args = ap.parse_args()
    main(pathlib.Path(args.src).expanduser(), pathlib.Path(args.dst).expanduser())
