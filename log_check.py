"""Count log levels in a log file and warn if there are too many errors.

Usage: python3 log_check.py app.log [error_threshold]
Expected line format: 2026-10-29 10:15:02 ERROR Database timeout
"""
import logging
import re
import sys
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("log_check.log"), logging.StreamHandler()],
)

LEVEL_PATTERN = re.compile(r"\b(INFO|WARNING|ERROR)\b")


def count_levels(path):
    counts = Counter()
    errors = Counter()  # most common error messages
    with open(path, encoding="utf-8") as f:
        for line in f:
            match = LEVEL_PATTERN.search(line)
            if not match:
                continue
            level = match.group(1)
            counts[level] += 1
            if level == "ERROR":
                errors[line.split("ERROR", 1)[1].strip()] += 1
    return counts, errors


def main():
    if len(sys.argv) < 2:
        logging.error("Usage: python3 log_check.py <logfile> [error_threshold]")
        return 2
    path = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        counts, errors = count_levels(path)
    except FileNotFoundError:
        logging.error("File not found: %s", path)
        return 2

    logging.info("Counts: %s", dict(counts))
    for message, n in errors.most_common(3):
        logging.info("Top error (%d times): %s", n, message)

    if counts["ERROR"] > threshold:
        logging.warning("ERROR count %d exceeds threshold %d", counts["ERROR"], threshold)
        return 1  # non-zero exit code so cron or other tools can detect a problem
    return 0


if __name__ == "__main__":
    sys.exit(main())
