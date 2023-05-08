xrandr --newmode "1800x1169_60.00"  176.25  1800 1920 2112 2424  1169 1172 1182 1212 -hsync +vsync

xrandr --addmode Virtual-1 "1800x1169_60.00"

xrandr --output Virtual-1 --mode "1800x1169_60.00"

setxkbmap -layout fr -variant mac