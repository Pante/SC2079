from stream_server import StreamServer

# sample use of this class.
def stream_server_test():
    server = StreamServer()
    server.start(
        resolution=(640, 480),
        framerate=20,
        quality=69,
        is_outdoors=True
    )

stream_server_test()