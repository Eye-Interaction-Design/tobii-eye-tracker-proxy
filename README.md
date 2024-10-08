# TobiiEyeTracker-macOS

This repository allows you to use Tobii Eye Tracker on macOS!

## Prerequisites

- Mac
- [Talon](https://talonvoice.com/)
- [Tobii Eye Tracker](https://talon.wiki/quickstart/hardware/#eye-trackers)

## Installation

1. Download and install [Talon](https://talonvoice.com/).
2. Run the Talon app.
3. Go to the Talon Home directory. This is `~/.talon` on macOS. (Talon has a menu in your system tray near the clock, you can use Scripting -> Open ~/.talon as a shortcut open Talon Home).

   ```bash
   cd ~/.talon/user
   ```

4. Clone [talonhub/community](https://github.com/talonhub/community) into your `~/.talon/user` directory.

   ```bash
   git clone https://github.com/talonhub/community community
   ```

5. Clone this repository into your `~/.talon/user/` directory.

   ```bash
   git clone https://github.com/Eye-Interaction-Design/TobiiEyeTracker-macOS TobiiEyeTracker-macOS
   ```

6. Calibrate your Tobii Eye Tracker. Go to Eye Tracking -> Calibrate in the menu.
7. Go to Scripting -> View Log in the menu for debug output.
8. Press `Ctrl + 1` to send the current gaze coordinates via socket.
9. To stop transmission, press `Ctrl + 2`.
