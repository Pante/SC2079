from stream_listener import StreamListener

# result handler.
def handle_result(res, frame):
    if res is None:
        return
    print("CONFIDENCE LEVEL: ", res.boxes[0].conf.item())
    print("CLASS: ", res.names[int(res.boxes[0].cls[0].item())])


# disconnect handler.
def handle_disconnect():
    print("disconnected.")


# sample use of this class.
def stream_listener_test():
    # load the StreamListener class with the weights file.
    listener = StreamListener('../../v13_trial3.pt')

    # pass in the handlers and start stream reading.
    listener.start_stream_read(handle_result, handle_disconnect, conf_threshold=0.65, show_video=True)

    # release resources on disconnect.
    listener.close()

stream_listener_test() # comment this out when actually using!