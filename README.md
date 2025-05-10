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
- **Large Files**: Videos will play until stopped or until the end is reached
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Dependencies**: Requires VLC Media Player and python-vlc

## Quick Reference

```text
[y] - Move video to E:\backup_2\SocialMediaContent
[n] - Keep video in E:\backup_2\Videos and continue
[q] - Quit the program
```
