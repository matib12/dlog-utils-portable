#!/usr/bin/env python3

import argparse
import csv
import decimal
import sys

from dlog import Dlog


def format_header_info(header: Dlog.Body.Header) -> list:
    """Extract the information from the header in a presentable form.

    Args:
        header: a Dlog header object
    Returns:
        list: header info as formatted strings
    """
    voltage_scale_strings = {1000: "mV", 1: "V"}
    voltage_scale = 1/header.voltage_scale
    if header.voltage_scale in voltage_scale_strings:
        voltage_scale = voltage_scale_strings[header.voltage_scale]

    sample_rate = decimal.Decimal(header.sample_rate)
    delay = decimal.Decimal(header.delay)

    info = [f'log format: {header.dlog_format.name}',
            f'stop reason: {header.stop_reason.name}',
            f'number of samples: {header.num_samples}',
            f'voltage units: {voltage_scale}',
            f'sample rate: {sample_rate.normalize().to_eng_string()} Sa/s',
            f'delay: {delay.normalize().to_eng_string()} s',
            f'number of channels: {header.num_channels}',
            f'channel map: {header.channel_map[:header.num_channels]}']

    return info


def write_csv(data, log_header=None, column_header=None, file=sys.stdout):
    """Write the given data to a CSV file.

    Args:
        data: iterable of samples (in turn, an iterable of channel data points)
        log_header: optional list of log header fields
        log_header: optional list of log header fields
        file: file-like object to write the CSV to
    """
    csv_writer = csv.writer(file)
    if log_header is not None:
        csv_writer.writerow(log_header)
    if column_header is not None:
        csv_writer.writerow(column_header)
    csv_writer.writerows(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', help='input log file')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='omit log file information (on stderr)')
    parser.add_argument('--no-csv-log-header', action='store_true',
                        help='omit log header for CSV output')
    parser.add_argument('--no-csv-column-header', action='store_true',
                        help='omit column header for CSV output')
    args = parser.parse_args()

    dlog = Dlog.from_file(args.inputfile)
    header = dlog.body.header

    if not args.quiet:
        print('\n'.join(['Header Information'] + format_header_info(header)),
              file=sys.stderr)

    timestamped_data = ([i/header.sample_rate, *s.channel]
                        for i, s in enumerate(dlog.body.data.samples))

    log_header = column_header = None
    if not args.no_csv_log_header:
        # extract the header fields (all public attributes)
        log_header = [f'{f}={v}' for f, v in vars(header).items() if not
                      f.startswith('_')]
    if not args.no_csv_column_header:
        column_header = ['Time'] + ['Channel ' + str(c) for c in
                                    header.channel_map[:header.num_channels]]

    write_csv(timestamped_data, log_header, column_header)


if __name__ == "__main__":
    main()
