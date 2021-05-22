import psutil
import GetInfo
import pandas as pd
from datetime import datetime
from termcolor import colored
import Notify
import time
import os


def print_header():
    print("╔"+"═"*117,end="╗\n║")
    print(colored("\t\t\t\t\t\t[= RESOURCE MONITOR =]\t\t\t\t\t\t      ", "cyan", attrs=['bold']),end="║\n")
    print("╚"+"═"*117+"╝")

def construct_dataframe(processes):
    df = pd.DataFrame(processes)
    df.set_index('pid', inplace=True)
    df.sort_values(sort_by, inplace=True, ascending=descending)
    df['memory_usage'] = df['memory_usage'].apply(get_size)
    df['write_bytes'] = df['write_bytes'].apply(get_size)
    df['read_bytes'] = df['read_bytes'].apply(get_size)
    df['create_time'] = df['create_time'].apply(datetime.strftime, args=("%Y-%m-%d %H:%M:%S",)) # Correcting formats
    df = df[columns.split(",")]
    return df

def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def kill_process(df, process, duration):
    os.system("cls") if "nt" in os.name else os.system("clear")
    while(duration > 0):
        print(df)
        print(f"Will close {process} in {duration} seconds")
        duration-=1
        time.sleep(1)
        os.system("cls") if "nt" in os.name else os.system("clear")

        if(duration == 60):
            Notify.Notify("Attention", "Closing the {process} in a minute", 5)
            duration -=5
    for proc in psutil.process_iter():
        if proc.name() == process:
            proc.kill()

def draw_graph():

    print("\n╔"+"═"*117,end="╗\n║")
    # Print CPU Graph
    cpu_usage = df['cpu_usage'].sum()
    if(cpu_usage>100): cpu_usage=100
    if(cpu_usage<1): cpu_usage=1
    text = "CPU Usage\t"+"█"*int(cpu_usage) + int(100-cpu_usage+2)*" "
    print(colored(text, "magenta", attrs=['bold']),end=" ║\n║")

    #Print Memory graph
    RAM = round(psutil.virtual_memory().total / (1024.0 **2))
    def get_number(x):
        if('MB' in x): return float(x[:-2])
        else: return float(x[:-2])/1024
    RAM_usage = df['memory_usage'].apply(get_number)
    RAM_usage = (RAM_usage.sum())*100
    text = "Memory Usage \t"+"█"*int(RAM_usage/ RAM) + int(100-int(RAM_usage/ RAM)+2)*" "
    print(colored(text, "green", attrs=['bold']),end="║\n")
    print("╚"+"═"*117+"╝")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--columns", default="name,cpu_usage,memory_usage,read_bytes,write_bytes,status,create_time,n_threads")
    parser.add_argument("-s", "--sort-by", dest="sort_by",default="memory_usage")
    parser.add_argument("--ascending", action="store_true")
    parser.add_argument("-n", default=20)
    parser.add_argument("-u", "--live-update", action="store_true")
    parser.add_argument("--kill", dest="process_to_close")
    parser.add_argument("--after", dest="duration", default=0)

    args = parser.parse_args()
    columns = args.columns
    sort_by = args.sort_by
    descending = args.ascending
    n = int(args.n)
    live_update = args.live_update
    kill = args.process_to_close
    duration = int(args.duration)

    processes = GetInfo.get_processes_info()
    df = construct_dataframe(processes)

    print_header()
    if n == 0:
        print(df.to_string())
    elif n > 0:
        print(df.head(n).to_string())
    draw_graph()

    while live_update:
        processes = GetInfo.get_processes_info()
        df = construct_dataframe(processes)
        os.system("cls") if "nt" in os.name else os.system("clear")
        print_header()
        if n == 0:
            print(colored(df.to_string(), 'red','on_white'))
        elif n > 0:
            print(colored(df.head(n).to_string(), 'red','on_white'))

        draw_graph()
        time.sleep(1)

    if(kill):
        kill_process(df.head(n).to_string(), kill, duration*60)
