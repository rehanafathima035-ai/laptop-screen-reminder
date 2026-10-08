# 🐸Water Reminder

A lightweight Windows desktop reminder that brings an animation onto your screen when it's time to drink water.

## 🎬 Demo

![Water Reminder Demo](walk_animation_source.gif)

An animation walks onto the screen from the **left**, displays the water reminder, and then walks off toward the **right**.

## ✨ Features

* 🐸 Animated character
* 🚶 Walks onto the screen from the left and exits to the right
* 💧 Built-in water reminder bubble
* ⏱️ Configurable reminder interval
* 🖱️ Right-click to dismiss or quit
* ⌨️ Press `Escape` to quit
* 🪟 Runs as a lightweight Windows desktop reminder
* 🚀 Optional automatic startup with Windows

## ⚙️ How It Works

The application uses the transparent `walk_animation_source.gif` and controls its frame timing and movement across the monitor.

The reminder animation:

```text
Screen
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   → 🐸 Character walks in → 💧 "Time to drink some water!" →      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                              → Character walks out
```

## 🚀 Run the Reminder

Make sure Python is installed, then run:

```powershell
python pond-water-reminder.py
```

The application detaches from PowerShell, so the terminal remains usable.

## ⏱️ Configure the Reminder

The reminder interval and message can be changed in:

```text
settings.json
```

Example:

```json
{
  "interval_minutes": 60,
  "message": "Time to drink some water!",
  "image": "walk_animation_source.gif"
}
```

## 🖥️ Start Automatically with Windows

Run:

```powershell
.\enable-startup.ps1
```

This creates or refreshes the Windows startup shortcut.

To disable automatic startup:

1. Press `Win + R`
2. Enter `shell:startup`
3. Press `Enter`
4. Delete the **Water Reminder** shortcut

## 📁 Project Structure

```text
reminder/
├── pond-water-reminder.py
├── pond.py
├── pond.jpg
├── settings.json
├── walk_animation_source.gif
├── walk_animation_source.gif
├── walk_frames/
├── enable-startup.ps1
├── README.md
└── .gitignore
```

## 🛠️ Requirements

* Windows
* Python 3.x
* Python virtual environment recommended

## 🎯 Purpose

This project is a small desktop productivity/reminder application designed to make regular water breaks more noticeable and fun.
