import threading


class EmailThreading(threading.Thread):
    """
    sending email with thread
    """

    def __init__(self, email_object):
        threading.Thread.__init__(self)
        self.email_object = email_object

    def run(self):
        self.email_object.send()
