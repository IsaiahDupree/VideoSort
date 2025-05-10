# Video Sorter

A lightweight Python script for quickly sorting video files from a source directory to a destination directory. Videos are played with sound using VLC.

## Setup

1. **Prerequisites**
   - Install VLC Media Player: [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)
   - Install python-vlc package:

   ```bash
   pip install python-vlc
   ```

2. **Directory Configuration**
   - Source Directory: `E:\backup_2\Videos`
   - Destination Directory: `E:\backup_2\SocialMediaContent`

## Usage

Run the script with the following command:

```bash
python video_sorter.py --src "E:\backup_2\Videos" --dst "E:\backup_2\SocialMediaContent"
```

To reset the list of skipped videos and start fresh:

```bash
python video_sorter.py --src "E:\backup_2\Videos" --dst "E:\backup_2\SocialMediaContent" --reset
```

To process videos in random order instead of alphabetically:

```bash
python video_sorter.py --src "E:\backup_2\Videos" --dst "E:\backup_2\SocialMediaContent" --random
```

To use a specific random seed for reproducible shuffling:

```bash
python video_sorter.py --src "E:\backup_2\Videos" --dst "E:\backup_2\SocialMediaContent" --random --seed 42
```

## How It Works

1. The script will loop through every video file in the source folder
2. Each video will be played with sound using VLC
3. **While the video is playing**, type one of these keys in the terminal and press Enter:
   - **y** → move the file to the destination folder and continue to next video
   - **n** → leave it where it is and continue to next video
   - **q** → quit the program early
4. If the video finishes before you make a choice, you'll be prompted to choose

## Notes

- **Supported File Types**: .mp4, .mov, .mkv, .avi
- **Full Playback**: Videos play with proper aspect ratio and sound
- **Playback Control**: Type 'y', 'n', or 'q' in the terminal while the video is playing to make your decision
- **Skipped Videos Tracking**: Videos you skip ('n') are remembered and won't be shown again in future runs
- **Random Selection**: Option to process videos in random order for variety
- **Large Files**: Videos will play until stopped or until the end is reached
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Dependencies**: Requires VLC Media Player and python-vlc

## Quick Reference

```text
[y] - Move video to E:\backup_2\SocialMediaContent
[n] - Keep video in E:\backup_2\Videos and add to skipped list
[q] - Quit the program
--reset - Command line flag to clear the skipped videos history
--random - Process videos in random order instead of alphabetically
--seed N - Use specific random seed N for reproducible shuffling
```

## How Skipped Videos Tracking Works

- When you choose 'n' for a video, its filename is saved to a persistent list
- This list is stored in `~/.video_sorter/` as a JSON file unique to each source directory
- The next time you run the script with the same source directory, previously skipped videos won't be shown
- If all videos have been skipped, you'll be prompted to reset the list
- You can manually reset the list with the `--reset` flag
