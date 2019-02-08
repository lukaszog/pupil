import av

def encode(frame):
    try:
        pkt = ovstream.encode(frame)
    except Exception:
        return False
    if pkt is not None:
        try:
            output.mux(pkt)
        except Exception:
            print('mux failed: ' + str(pkt))
    return True

input_file = 'http://192.168.8.105:8081/'
container = av.open(input_file)
video_st = container.streams.video[0]
output = av.open('archive.mp4', 'w')
ovstream = output.add_stream('libx264', video_st.rate)
ovstream.pix_fmt = 'yuv720p'
ovstream.width = video_st.width
ovstream.height = video_st.height

counter = 0
for packet in container.demux((video_st,)):
    for frame in packet.decode():
        new_frame = av.VideoFrame(width=frame.width, height=frame.height, format=frame.format.name)
        for i in range(len(frame.planes)):
            new_frame.planes[i].update(frame.planes[i])
        encode(new_frame)
        counter += 1
        print("Frames encoded:", counter)
    if counter > 200:
        break

while True:
    if not encode(None):
        break
output.close()