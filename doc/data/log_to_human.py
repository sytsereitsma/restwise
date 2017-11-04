import argparse
import sys
import glob


def split_commands(data):
    split_data = []

    trailer_pos = data.find(b"\r\n")
    while trailer_pos != -1:
        split_at = trailer_pos + 2
        split_data.append(data[:split_at])
        data = data[split_at:]
        trailer_pos = data.find(b"\r\n")

    if data:
        split_data.append(data)

    return split_data


def get_data(line):
    length_start = line.index("Length ")
    data_start = line.index(": ", length_start) + 2
    hash_pos = line.find("#", data_start)

    ascii_hex_data = line[data_start:hash_pos].strip().split(" ")
    data = bytes(map(lambda b: int(b, 16), ascii_hex_data))

    return split_commands(data)


def convert_file(filename):
    command_list = []
    log_file = open(filename, "rt")
    for line in log_file:
        try:
            fmt = ""
            if "IRP_MJ_WRITE" in line:
                fmt = "W {}"
            elif "IRP_MJ_READ" in line:
                fmt = "R   {}"

            if fmt:
                data = get_data(line)
                for d in data:
                    header_index = d.find(b"\05\05\03\03")
                    if header_index != -1:
                        command_list.append(int(d[header_index + 4:header_index + 8], 16))
                    print(fmt.format(d))
        except Exception as e:
            print(e)
            print(line)
    command_list = set(command_list)
    for cmd in command_list:
        print("{:04X}".format(cmd))

def convert(pattern):
    files = glob.glob(pattern)
    for f in files:
        convert_file(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool to convert sysinternals procmon logs to a human readable digest of the PlugWise stick communication")
    parser.add_argument("logfile", help="Name of the portmon logfile to convert (wildcards supported).")
    args = parser.parse_args()

    if not convert(args.logfile):
        sys.exit(-1)
