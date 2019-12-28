import sys
import vlc
import keyboard
vlcInstance = vlc.Instance()
URI = "scitunnel.mp4"
player = vlcInstance.media_player_new(URI)
player.set_fullscreen(True)
player.play()
puzzleProgress = 0
while True:
    if(player.get_time()>2.5*1000 and puzzleProgress < 1):
        player.pause()
        while(True):
            if(keyboard.is_pressed('r')):
                player.pause()
                puzzleProgress += 1
                break
            elif(keyboard.is_pressed('w')):
                player.set_time(1)
                player.pause()
                puzzleProgress = 0
                break
    elif(player.get_time()>5*1000 and puzzleProgress < 2):
        player.pause()
        while(True):
            if(keyboard.is_pressed('r')):
                player.pause()
                puzzleProgress += 1
                break
            elif(keyboard.is_pressed('w')):
                player.set_time(1)
                player.pause()
                puzzleProgress = 0
                break
    elif(player.get_time()>7.5*1000 and puzzleProgress < 3):
        player.pause()
        while(True):
            if(keyboard.is_pressed('r')):
                player.pause()
                puzzleProgress += 1
                break
            elif(keyboard.is_pressed('w')):
                player.set_time(1)
                player.pause()
                puzzleProgress = 0
                break
    elif(player.get_time()>10*1000 and puzzleProgress < 4):
        player.pause()
        while(True):
            if(keyboard.is_pressed('r')):
                player.pause()
                puzzleProgress += 1
                break
            elif(keyboard.is_pressed('w')):
                player.set_time(1)
                player.pause()
                puzzleProgress = 0
                break