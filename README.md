# New Pimp My Lock

This project is a Python adaptation of the [Pimp My Lock](https://github.com/jerem-ma/pimp_my_lock) project. It allows you to set a custom wallpaper on your lock screen, with additional features, mainly designed for students at 42 School.

## Features

- Displays how long your screen has been locked.
- Easily add new wallpapers by modifying the `config.json` file.
- Available options:
  - `--list`: Displays all available wallpapers.
  - `--media <path>`: Launches a media file not in the list.
  - `--msg <text>`: Adds a custom message on the lock screen.

## Requirements

### Linux Dependencies:
Make sure you have the following dependencies installed on your system:

- `ft_lock`
- `mpv`
- `xwininfo`
- `grep`
- `awk`
- `wmctrl`
- `xdotool`

### Python Dependencies:
Ensure the following Python libraries are installed:

- `PIL` (Pillow)
- `opencv-python`
- `json`
- `tempfile`
- `subprocess`
- `shutil`
- `time`

You can install the necessary Python dependencies using:

```bash
pip install Pillow opencv-python
```

### Installing Missing Linux Packages:
If you encounter missing Linux packages, you can use the following project to install them locally: [apt_install_locally](https://github.com/leofarhi/apt_install_locally)

## How to Run

1. Clone the repository:

```bash
git clone https://github.com/leofarhi/pimp_my_lock.git
cd pimp_my_lock
```

2. Ensure the necessary dependencies are installed as mentioned above.

3. Run the program:

```bash
python3 pimp_my_lock.py
```

4. To list available wallpapers:

```bash
python3 pimp_my_lock.py --list
```

5. To use a custom wallpaper or media file:

```bash
python3 pimp_my_lock.py --media /path/to/media.mp4
```

6. To add a custom message to the lock screen:

```bash
python3 pimp_my_lock.py --msg "Your custom message"
```

## Configuration

Wallpapers are listed in the `config.json` file. You can modify this file to add or remove wallpapers.

Example of `config.json`:

```json
{
  "wallpapers": {
    "wallpaper1": "path/to/wallpaper1.jpg",
    "wallpaper2": "path/to/wallpaper2.png"
  },
  ...
}
```

## Don't Forget to Install Font

For the best experience, you need to install the font used for the lock screen. The current font is `ZeldaBotw.otf`. To install it:

1. Double-click on the `ZeldaBotw.otf` file to open it.
2. Click "Install" to add it to your system's font library.

You can replace this font with any font of your choice by updating the `config.json` file with the path to your preferred `.otf` or `.ttf` font.

Example:

```json
{
  ...
  "font": "path/to/your/font.ttf"
}
```

## Troubleshooting

- Ensure you have the required permissions to set a lock screen wallpaper.
- If you encounter any errors related to missing files or permissions, make sure the necessary dependencies are installed and accessible.
  
