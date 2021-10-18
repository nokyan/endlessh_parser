import ipinfo
import numpy as np
import re
from rich.console import Console
from rich.table import Column, Table
import sys
import time


IPINFO_TOKEN = "YOUR_TOKEN"


def parse_line(line: str):
    regex = r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}Z CLOSE host=([a-zA-Z0-9]{0,4}:[a-zA-Z0-9]{0,4}:[a-zA-Z0-9]{0,4}:[a-zA-Z0-9]{0,4}(:|.)[a-zA-Z0-9]{0,4}(:|.)[a-zA-Z0-9]{0,4}(:|.)[a-zA-Z0-9]{0,4}) port=[0-9]{1,5} fd=[0-9]{1,4} time=([0-9]{1,7}.[0-9]{1,3}) bytes=([0-9]{1,6})'
    search = re.search(regex, line, re.IGNORECASE)
    ip = search.group(1)
    time = float(search.group(5))
    sent_bytes = int(search.group(6))
    
    return (ip, time, sent_bytes)


def main(filename: str):
    print("reading")
    with open(filename, "r") as f:
        lines = f.readlines()
        
    handler = ipinfo.getHandler(IPINFO_TOKEN)
    times = []
    sent_bytes = []
    countries = {}
    ip_batch = []
    
    # prep countries counter
    for c in handler.countries.keys():
        countries[c] = 0
        
    print("parsing")
    for l in lines:
        if "CLOSE host=" in l:
            result = parse_line(l)
            ip_batch.append(result[0].replace("::ffff:", "") + "/country")
            times.append(result[1])
            sent_bytes.append(result[2])
    
    print("getting countries")
    batch_result = handler.getBatchDetails(ip_batch)
    for i in ip_batch:
        result = batch_result[i]
        if isinstance(result, str):
            countries[result] = countries[result] + 1
    
    ordered_countries = sorted(countries.items(), key=lambda x:x[1], reverse=True)
    
    time_format_string = '%H:%M:%S'
    
    max_time = time.strftime(time_format_string, time.gmtime(max(times)))
    min_time = time.strftime(time_format_string, time.gmtime(min(times)))
    median_time = time.strftime(time_format_string, time.gmtime(np.median(times)))
    mean_time = time.strftime(time_format_string, time.gmtime(np.mean(times)))
    std_time = time.strftime(time_format_string, time.gmtime(np.std(times)))
    
    max_bytes = max(sent_bytes)
    min_bytes = min(sent_bytes)
    median_bytes = np.median(sent_bytes)
    mean_bytes = np.mean(sent_bytes)
    std_bytes = np.std(sent_bytes)
    
    console = Console()

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("Top 5 Countries")
    table.add_column("Wasted Time Stats")
    table.add_column("Sent Bytes Stats")
    
    table.add_row(f"{handler.countries[ordered_countries[0][0]]}: [bold]{ordered_countries[0][1]}[/bold]",
                  f"↑ [bold]{max_time}[/bold]",
                  f"↑ [bold]{max_bytes}[/bold]")
    table.add_row(f"{handler.countries[ordered_countries[1][0]]}: [bold]{ordered_countries[1][1]}[/bold]",
                  f"M [bold]{median_time}[/bold]",
                  f"M [bold]{median_bytes:.2f}[/bold]")
    table.add_row(f"{handler.countries[ordered_countries[2][0]]}: [bold]{ordered_countries[2][1]}[/bold]",
                  f"x̄ [bold]{mean_time}[/bold]",
                  f"x̄ [bold]{mean_bytes:.2f}[/bold]")
    table.add_row(f"{handler.countries[ordered_countries[3][0]]}: [bold]{ordered_countries[3][1]}[/bold]",
                  f"σ [bold]{std_time}[/bold]",
                  f"σ [bold]{std_bytes:.2f}[/bold]")
    table.add_row(f"{handler.countries[ordered_countries[4][0]]}: [bold]{ordered_countries[4][1]}[/bold]",
                  f"↓ [bold]{min_time}[/bold]",
                  f"↓ [bold]{min_bytes}[/bold]")
    
    console.print(table)


if __name__ == "__main__":
    main(sys.argv[1])
