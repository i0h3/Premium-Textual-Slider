from textual.color import Color, Lab, rgb_to_lab

ansi_black = rgb_to_lab(Color(0, 0, 0))
ansi_red = rgb_to_lab(Color(205, 0, 0))
ansi_green = rgb_to_lab(Color(0, 205, 0))
ansi_yellow = rgb_to_lab(Color(205, 205, 0))
ansi_blue = rgb_to_lab(Color(0, 0, 238))
ansi_magenta = rgb_to_lab(Color(205, 0, 205))
ansi_cyan = rgb_to_lab(Color(0, 205, 205))
ansi_white = rgb_to_lab(Color(229, 229, 229))

ansi_bright_black = rgb_to_lab(Color(127, 127, 127))
ansi_bright_red = rgb_to_lab(Color(255, 0, 0))
ansi_bright_green = rgb_to_lab(Color(0, 255, 0))
ansi_bright_yellow = rgb_to_lab(Color(255, 255, 0))
ansi_bright_blue = rgb_to_lab(Color(92, 92, 255))
ansi_bright_magenta = rgb_to_lab(Color(255, 0, 255))
ansi_bright_cyan = rgb_to_lab(Color(0, 255, 255))
ansi_bright_white = rgb_to_lab(Color(255, 255, 255))
