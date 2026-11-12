import json
import sys
import re
from collections import Counter
from datetime import datetime
import argparse
from pathlib import Path
from dataclasses import dataclass
import textwrap

@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    loglevel: str
    message: str

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

def parse_line(line: str) -> LogEntry | None:
    """
    Validates a log line shape. Returns a LogEntry object if valid, 
    otherwise returns None.
    """

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None
    
    parse_result = match.groupdict()
    result_datetime = parse_datetime(parse_result["timestamp"])
    if result_datetime is None:
        return None
    
    parsed_result = LogEntry(timestamp=result_datetime, loglevel=parse_result["loglevel"], message=parse_result["message"])
    return parsed_result


def parse_datetime(dte: str) -> datetime | None:
    """ 
    Basically just validates a string that should be a datetme
    """

    try:
        return datetime.strptime(dte, DATE_FORMAT)
    except ValueError:
        return None


def process_log_file(logfile_path: str) -> dict:
    """
    Opens a log file, parses it line-by-line, and processes the results.
    """
    results = {"logs": [], "garbage": []}


    with open(logfile_path, "r", encoding="utf-8") as file:
        for line in file:

            log_data = parse_line(line)

            if log_data is not None:
                results["logs"].append(log_data)
            else:
                results["garbage"].append(line)

    return results


def build_summary(result_data) -> dict | None:
    """
    Builds the dict object that is either printed out or
    used to build the text-based report
    """

    if len(result_data["logs"]) == 0:
        return None


    log_levels_counter = Counter(log.loglevel for log in result_data["logs"])
    message_counts = Counter(log.message for log in result_data["logs"])
    top_5 = message_counts.most_common(5)

    top_msgs = [
        {"message": msg, "count": count} 
        for msg, count in top_5
    ]

    log_levels = dict(log_levels_counter)

    first_timestamp = min(log.timestamp for log in result_data["logs"])
    last_timestamp = max(log.timestamp for log in result_data["logs"])

    result = {
        "total_valid": len(result_data["logs"]),
        "skipped": len(result_data["garbage"]),
        "log_levels": log_levels,
        "first_timestamp": first_timestamp.strftime(DATE_FORMAT),
        "last_timestamp": last_timestamp.strftime(DATE_FORMAT),
        "top_messages": top_msgs
    }
    
    return result


def generate_report(result_data: dict) -> dict | None:
    """
    Returns a dictionary object with both the result_data that
    was passed in as well as a text-friendly summary, either of
    which can be displayed/printed.
    """

    summary = build_summary(result_data)

    if summary is None:
        return

    log_level_count_str = ""
    for level, count in summary["log_levels"].items():
        log_level_count_str += f"""
        {level} : {count}""" 


    top_msg_count_str = ""
    for item in summary["top_messages"]:
        top_msg_count_str += f"""
        {item["message"]} : {item["count"]}"""

    report_text = f"""
    {REPORT_HDR}
    First Timestamp: {summary["first_timestamp"]}
    Last Timestamp: {summary["last_timestamp"]}
    Valid Lines: {summary["total_valid"]}
    Skipped Lines: {summary["skipped"]}\n
    Log Level Counts: {log_level_count_str}\n
    Top 5 Message: {top_msg_count_str}
    """

    report_data = {
        "text": textwrap.dedent(report_text),
        "json": summary
    }

    return report_data


def write_report(output_file: str, report_data: dict) -> None:
    """
    Writes the report out to a .json or .txt file, depending upon
    the name provided to output_file.  Any other file foramt is ignored
    """

    if Path(output_file).suffix == ".txt":      
        data_to_use = report_data["text"]
    else:
        data_to_use = json.dumps(report_data["json"])

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(data_to_use) 

    print(f"report written to {output_file}")

def main():
    """
    Main body of the script - everything starts here
    """

    parser = argparse.ArgumentParser(description="Parse and summarize log file")
    parser.add_argument("-l", "--log", required=True, type=str, help="Log filename")
    parser.add_argument("-o", "--out", help="Output filename (use .txt for plain text or .json for JSON-formamtted summary)")

    args = parser.parse_args()
    logfile_path = args.log
    output_file = args.out

    try:
        log_data = process_log_file(logfile_path)
    except (FileNotFoundError, PermissionError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    
    report = generate_report(log_data)
    
    if report is None:
        print(f"{logfile_path} is corrupted or has no valid data to report - exiting...", file=sys.stderr)
    else:
        print(report["text"])

        if output_file is not None and output_file != "":

            file_suffix = Path(output_file).suffix

            if file_suffix != ".txt" and file_suffix != ".json":
                print("Invalid file format - choose either .txt or .json", file=sys.stderr)
            else:
                write_report(output_file, report)
            

if __name__ == "__main__":
     main()  #run the main function