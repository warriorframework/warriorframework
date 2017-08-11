from utils.date_time_stamp_utils import get_current_timestamp


class ErrorLog:

    def __init__(self, log_file):
        self.log_file = log_file
        self.pending_logs = ""

    def write_log(self, logs):
        self.flush()
        print logs
        logs = "{2}-- {0} --{2} {1}".format(get_current_timestamp(), logs, "\n")
        with open(self.log_file, "w") as f:
            f.write(logs)

    def append_log(self, logs):
        print logs
        self.pending_logs += "{2}-- {0} --{2} {1}".format(get_current_timestamp(), logs, "\n")

    def flush(self):
        with open(self.log_file, "w") as f:
            f.write(self.pending_logs)
        self.pending_logs = ""
