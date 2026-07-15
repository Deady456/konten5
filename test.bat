@echo off
set "VF=drawtext=fontfile='assets/fonts/Anton-Regular.ttf':text='INI ADALAH TEKS HOOK 3 DETIK PERTAMA!':fontsize=80:fontcolor=white:borderw=4:bordercolor=black:x=(w-tw)/2:y=(h-th)/2:enable='between(t\,0\,3)',subtitles='output/test_captions.ass':fontsdir='assets/fonts'"
ffmpeg -y -f lavfi -i color=c=blue:s=1080x1920:r=30:d=10 -f lavfi -i anullsrc=r=44100:cl=stereo -vf "%VF%" -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 128k -shortest -pix_fmt yuv420p output/test_hook.mp4
