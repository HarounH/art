# art


# Cloth blowing in wind
install requirements.txt
then:
```
python -m cloth.main -l 0.5 0.5 0.5
```

The command line by default saves frame_{i}.jpg in output. Contatenate them into a video using [ffmpeg](https://ffmpeg.org/):

```
./ffmpeg/bin/ffmpeg -i cloth/output/frame_%d.jpg -c:v libx264 -r 30 cloth/output/output.mp4
```
