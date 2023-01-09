# art


# Cloth blowing in wind

## Instructions:

install requirements.txt


https://user-images.githubusercontent.com/7512243/211228929-7f8ff7ad-5752-463b-a3b0-91b8ffa3ef45.mp4


then:
```
python -m cloth.main -l 0.5 0.5 0.5
```

NOTE: The command line by default saves frame_{i}.jpg in output. Contatenate them into a video using [ffmpeg](https://ffmpeg.org/):
```
./ffmpeg/bin/ffmpeg -i cloth/output/frame_%d.jpg -c:v libx264 -r 30 cloth/output/output.mp4
```
