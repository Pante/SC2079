from stream_server import StreamServer

# sample use of this class.
def stream_server_test():
    server = StreamServer()
    server.start(
        resolution=(640, 480),
        framerate=20,
        quality=60,
        # brightness=70,
        contrast=0,
        exposure_compensation=25
    )

stream_server_test()