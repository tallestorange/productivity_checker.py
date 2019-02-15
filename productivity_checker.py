import subprocess
import csv
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("csv_filename", help="output csv's directory&filename")
parser.add_argument("dir", help="target project's .git folder")
parser.add_argument("--since", help="example format-> 2019-01-01")
parser.add_argument("--name", help="")
parser.add_argument("--until", help="example format-> 2019-01-02")

class Productivity_Checker(object):
    def __init__(self, args):
        self.filename = args.csv_filename
        self.directory = args.dir
        self.username = args.name
        self.since = args.since
        self.until = args.until

    def make_cmd_string(self, since=None, until=None):
        args = [
            "git",
            "--git-dir",
            self.directory,
            "log",
            "--numstat",
            "--pretty=\"%H\""
        ]

        if since:
            args += ["--since=" + since]
        if until:
            args += ["--until=" + until]
        if self.username:
            args += ["--author" + self.username]

        args_awk = [
            "|",
            "awk",
            "'NF==3 {plus+=$1; minus+=$2} END {printf(\"%d %d\\n\", plus, minus)}'"]

        command = " ".join(args+args_awk)
        return command

    def output_productivity_stdout(self, since=None, until=None):
        proc = subprocess.Popen(
            self.make_cmd_string(since=since, until=until),
            shell = True,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )

        stdout_data, _ = proc.communicate()
        plus, minus = stdout_data.strip().split() #map(int, stdout_data.strip().split())
        return plus, minus

    def output_datetime(self):
        since_datetime, until_datetime = None, None
        try:
            if self.since and self.until:
                until_datetime = datetime.strptime(self.until, "%Y-%m-%d")
                since_datetime = datetime.strptime(self.since, "%Y-%m-%d")
            elif self.since:
                until_datetime = datetime.now()
                since_datetime = datetime.strptime(self.since, "%Y-%m-%d")
            elif self.until:
                until_datetime = datetime.strptime(self.until, "%Y-%m-%d")
                since_datetime = until_datetime - timedelta(months=1)
        except:
            pass
        return since_datetime, until_datetime
    
    def output_csv(self):
        since_datetime, until_datetime = self.output_datetime()
        if not (since_datetime and until_datetime):
            print("Date Format Error")
            return

        days = (until_datetime-since_datetime).days

        with open(self.filename, "w") as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(["Date", "Increase", "Decrease"])

            for i in range(days+1):
                day_since = (since_datetime + timedelta(days=i)).strftime("%Y-%m-%d")
                day_until = (since_datetime + timedelta(days=i+1)).strftime("%Y-%m-%d")
                increase_code, decrease_code = self.output_productivity_stdout(
                    since=day_since,
                    until=day_until)
                writer.writerow([day_until, increase_code, decrease_code])

if __name__ == "__main__":
    args = parser.parse_args()
    session = Productivity_Checker(args)
    session.output_csv()