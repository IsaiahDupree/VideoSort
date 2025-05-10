# video_sorter.py
import argparse, shutil, sys, pathlib, time, threading, queue, json, os
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

def load_skipped_videos(src_dir: pathlib.Path) -> set:
    """Load the list of previously skipped videos for this source directory"""
    # Create a unique history file name based on the source directory path
    history_dir = pathlib.Path(os.path.expanduser("~")) / ".video_sorter"
    history_dir.mkdir(exist_ok=True)
    
    # Create a hash of the source directory path to use as the filename
    src_hash = str(hash(str(src_dir.absolute())))
    history_file = history_dir / f"skipped_{src_hash}.json"
    
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not read history file. Starting with empty history.")
    
    return set()

def save_skipped_videos(src_dir: pathlib.Path, skipped_videos: set) -> None:
    """Save the list of skipped videos for this source directory"""
    history_dir = pathlib.Path(os.path.expanduser("~")) / ".video_sorter"
    history_dir.mkdir(exist_ok=True)
    
    src_hash = str(hash(str(src_dir.absolute())))
    history_file = history_dir / f"skipped_{src_hash}.json"
    
    try:
        with open(history_file, 'w') as f:
            json.dump(list(skipped_videos), f)
    except IOError:
        print("Warning: Could not save history file.")

def main(src_dir: pathlib.Path, dst_dir: pathlib.Path) -> None:
    # Load previously skipped videos
    skipped_videos = load_skipped_videos(src_dir)
    print(f"Loaded {len(skipped_videos)} previously skipped videos.")
    
    # Get all videos and filter out previously skipped ones
    all_videos = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi"})
    videos = [v for v in all_videos if v.name not in skipped_videos]
    
    if not all_videos:
        print("No video files found."); return
    
    if not videos:
        print(f"All {len(all_videos)} videos have been previously skipped.")
        if input("Do you want to reset the skipped videos list? (y/n): ").lower() == 'y':
            skipped_videos.clear()
            save_skipped_videos(src_dir, skipped_videos)
            videos = all_videos
            print("Skipped videos list has been reset.")
        else:
            return
    
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
            # Add to skipped videos list
            skipped_videos.add(vid.name)
            save_skipped_videos(src_dir, skipped_videos)
        elif choice == "q":
            print("Exiting…")
            # Save skipped videos before exiting
            save_skipped_videos(src_dir, skipped_videos)
            sys.exit(0)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Manual video sorter (y/n to move files).")
    ap.add_argument("--src", required=True, help="Source folder containing videos")
    ap.add_argument("--dst", required=True, help="Destination folder for accepted videos")
    ap.add_argument("--reset", action="store_true", help="Reset the skipped videos list")
    args = ap.parse_args()
    
    src_path = pathlib.Path(args.src).expanduser()
    dst_path = pathlib.Path(args.dst).expanduser()
    
    # Reset skipped videos if requested
    if args.reset:
        history_dir = pathlib.Path(os.path.expanduser("~")) / ".video_sorter"
        src_hash = str(hash(str(src_path.absolute())))
        history_file = history_dir / f"skipped_{src_hash}.json"
        if history_file.exists():
            history_file.unlink()
            print("Skipped videos list has been reset.")
    
    main(src_path, dst_path)
