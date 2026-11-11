import json
import os
import sys
import re
from collections import Counter
from datetime import datetime
import argparse


REPORT_HDR = """
    ==============================================================================
    ==============================================================================
    =============================  LOGS REPORT  ==================================
    ==============================================================================
    ==============================================================================\n
    """

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "  # YYYY-MM-DD HH:MM:SS
    r"(?P<loglevel>INFO|WARNING|CRITICAL|ERROR|DEBUG) "      # Allowed levels
    r"(?P<message>.+)$"                                      # The rest of the line
)

def parse_line(line: str) -> dict[str, str] | None:
    """
    Validates a log line shape. Returns a dict object if valid, 
    otherwise returns None.
    """

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None
    
    parse_result = match.groupdict()
    result_datetime = parse_datetime(parse_result["timestamp"])
    if result_datetime is None:
        return None
    else:
        parse_result["timestamp"] = result_datetime
    
    return parse_result



def parse_datetime(dte: str) -> datetime | None:
    try:
        return datetime.strptime(dte, DATE_FORMAT)
    except ValueError:
        return None


def process_log_file(logfile_path: str) -> dict:
    """Opens a log file, parses it line-by-line, and processes the results."""
    results = {"logs": [], "garbage": []}


    with open(logfile_path, "r", encoding="utf-8") as file:
        for line in file:

            log_data = parse_line(line)

            if log_data is not None:
                results["logs"].append(log_data)
            else:
                results["garbage"].append(line)

    return results

def generate_report(result_data):
    """ generates a report to display the error logs """

    logs_count = {}
    msgs_count = []


    if len(result_data["logs"]) == 0:
        if len(result_data["garbage"]) == 0:
            return f"{REPORT_HDR}Nothing to report! Go about your business..."        
        else:
            return f"{REPORT_HDR}Looks like {len(result_data["garbage"])} lines pure garbage! Might wanan check what's gooing on..."

    log_count = Counter(log["loglevel"] for log in result_data["logs"])
    message_counts = Counter(log["message"] for log in result_data["logs"])
    top_5 = message_counts.most_common(5)

    top_msgs = [
        {"message": msg, "count": count} 
        for msg, count in top_5
    ]

    log_level_count_str = ""
    for level, count in logs_count.items():
        log_level_count_str += f"""         {level} : {count}\n""" 

    top_msg_count_str = ""
    for item in top_msgs:
        top_msg_count_str += f"""       {item["message"]} : {item["count"]}\n"""


    first_timestamp = min(log["timestamp"] for log in result_data["logs"])
    last_timestamp = max(log["timestamp"] for log in result_data["logs"])
    
    return f"""
    {REPORT_HDR}
    First Timestamp: {first_timestamp}
    Last Timestamp: {last_timestamp}\n
    Skipped/Malformed Lines Total: {len(result_data["garbage"])}
    Log Level Counts: \n{log_level_count_str}
    Top 5 Message: \n{top_msg_count_str}

    """


def print_result(output_file, report_data):

    if output_file == "" or output_file is None:
        print(report_data)
    else:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(report_data)
            print(f"report written to {output_file}")


def main():
        
    parser = argparse.ArgumentParser(description="Parse and summarize log file")
    parser.add_argument("-l", "--log", type=str, help="Log filename")
    parser.add_argument("-o", "--out", help="Output filename")

    args = parser.parse_args()
    logfile_path = args.log
    output_file = args.out

    if logfile_path == ""or logfile_path is None:
        sys.exit(1)
    else:
        try:
            result = process_log_file(logfile_path)
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except PermissionError as e:
            print(e)
            sys.exit(1)

        report = generate_report(result)
        print_result(output_file, report)

if __name__ == "__main__":
     main()  #run the main function