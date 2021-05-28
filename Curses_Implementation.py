import curses
from itertools import cycle
import psutil
import pandas as pd
from datetime import datetime
from termcolor import colored
import GetInfo
import Notify
import time
import os


def print_header():
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()

    stdscr.keypad(True)
    (y, x) = stdscr.getmaxyx()
    curses.start_color()
    stdscr.addstr(0,0,"╔" + ("═"*(x-2)) + "╗║")
    curses.init_pair(1,curses.COLOR_CYAN, curses.COLOR_BLACK) 
    stdscr.addstr(1,(x//2)-11,"[= RESOURCE MONITOR =]", curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(1,x-1,"║")
    stdscr.addstr(2,0,"╚" + ("═"*(x-2)) + "╝")
    stdscr.refresh()


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

def kill_process(process, duration):
    stdscr = curses.initscr()
    stdscr.clear()
    while(duration > 0):
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        y, x = stdscr.getmaxyx()
        s = f"Will close {process} in {duration} seconds"
        x = (x//2) - (len(s)//2)
        y = y//2
        stdscr.addstr(y, x, s, curses.color_pair(4))
        duration-=1
        time.sleep(1)
        stdscr.clear()

        if(duration == 60):
            Notify.Notify("Attention", "Closing the {process} in a minute", 5)
            duration -=5
    for proc in psutil.process_iter():
        if proc.name() == process:
            proc.kill()

def draw_graph():

    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    stdscr.addstr(25, 0, "\n╔"+"═"*117+"╗\n║")
    # Print CPU Graph
    df = construct_dataframe(processes)
    cpu_usage = df['cpu_usage'].sum()
    if(cpu_usage>100): cpu_usage=100
    if(cpu_usage<1): cpu_usage=1
    text = "CPU Usage\t"+"█"*int(cpu_usage) + int(100-cpu_usage+2)*" "
    stdscr.addstr(27,1,text, curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(27,118,"║")

    #Print Memory graph
    RAM = round(psutil.virtual_memory().total / (1024.0 **2))
    def get_number(x):
        if('MB' in x): return float(x[:-2])
        else: return float(x[:-2])/1024
    RAM_usage = df['memory_usage'].apply(get_number)
    RAM_usage = (RAM_usage.sum())*100
    text = "Memory Usage \t"+"█"*int(RAM_usage/ RAM) + int(100-int(RAM_usage/ RAM)+2)*" "
    stdscr.addstr(28,0,"║")
    stdscr.addstr(28,1,text, curses.color_pair(3)| curses.A_BOLD)
    stdscr.addstr(28,118,"║")
    stdscr.addstr(29,0,"╚"+"═"*117+"╝")
    stdscr.refresh()


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

    # Fix terminal size
    if 'nt' in os.name:
        while(1):
            (width, height) = os.get_terminal_size()
            if(int(height) < 33 or int(width)<120):
                print(colored("Terminal size too small. Resize the terminal", 'red', attrs=['bold']))
            else:
                break
            time.sleep(0.5)
            os.system("cls")
    else:
        while(1):
            height, width = os.popen('stty size', 'r').read().split()
            if(int(height) < 33 or int(width)<120):
                print(colored("Terminal size too small. Resize the terminal", 'red', attrs=['bold']))
            else:
                break
            time.sleep(0.5)
            os.system("clear")
        
    processes = GetInfo.get_processes_info()
    df = construct_dataframe(processes)

    stdscr = curses.initscr()
    curses.start_color()
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_WHITE)

    print_header()
    if n == 0:
        df = df.head(40).to_string().split('\n')
    elif n > 0:
        df = df.head(n).to_string().split('\n')
    ind, xind = stdscr.getmaxyx()
    ind = 4
    for i in df:
        stdscr.addstr(ind, xind//2- len(df[0])//2, i, curses.color_pair(6))
        ind+=1
    stdscr.refresh()
    draw_graph()
    
    current_selection = 1
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    
    while live_update:
        stdscr.nodelay(1)
        processes = GetInfo.get_processes_info()
        df = construct_dataframe(processes)
        key = stdscr.getch()        
        if(key == curses.KEY_DOWN):
            if(current_selection <20):
                current_selection +=1
        if(key == curses.KEY_UP):
            if(current_selection >0):
                current_selection -=1
        time.sleep(.5)
        stdscr.clear()
        print_header()
        if n == 0:
            newdf=df.head(30).to_string().split('\n')
        elif n > 0:
            newdf = df.head(n).to_string().split('\n')
        ind, xind = stdscr.getmaxyx()
        stdscr.addstr(4, xind//2 -len(newdf[0])//2, newdf[0], curses.color_pair(6)|curses.A_BOLD)
        ind = 5
        for i in newdf[1:]:
            if(ind-5 == current_selection):
                stdscr.addstr(ind, xind//2 -len(newdf[0])//2, i, curses.color_pair(7)|curses.A_BOLD) 
                ind+=1   
                continue
            stdscr.addstr(ind, xind//2 -len(newdf[0])//2, i, curses.color_pair(6))
            ind+=1

        stdscr.refresh
        draw_graph()
        
    if(kill):
        kill_process(kill, duration*60)
