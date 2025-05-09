#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
from telethon.sync import TelegramClient, errors
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from colorama import Fore, Style, init
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.console import Console

init(autoreset=True)
console = Console()

BANNER = '''
██████╗ ███████╗██████╗  ██████╗ ██████╗ ████████╗
██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
██████╔╝█████╗  ██████╔╝██║   ██║██████╔╝   ██║   
██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██╔══██╗   ██║   
██║  ██║███████╗██║     ╚██████╔╝██║  ██║   ██║   
╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
----------------------------------
Author: MohammadMahdi Hajivand
'''

SESSION = "report_bomber_session"

ATTACK_TYPES = {"1": "report", "2": "ban", "3": "spam"}
REASON_MAP = {
    "1": "spam", "2": "violence", "3": "pornography", "4": "child_abuse",
    "5": "copyright", "6": "fake", "7": "terrorism"
}


def print_menu():
    print(BANNER)
    print(f"{Fore.MAGENTA}1){Style.RESET_ALL} Start Attack (Report/Ban/Spam)")
    print(f"{Fore.MAGENTA}2){Style.RESET_ALL} Help")
    print(f"{Fore.MAGENTA}3){Style.RESET_ALL} Exit\n")

def show_help():
    print(f"""{Fore.GREEN}
[ HELP ]
--------
1. Start Attack:
   - Choose attack type (Report, Ban, Spam)
   - Enter target (numeric ID, @username, or t.me/ link)
   - Set number of attempts
   - For report, select reason
   - Live progress and results shown
   - Results saved to attack_log.txt

2. Help:
   - Shows this help message

3. Exit:
   - Exits the tool

[ IMPORTANT NOTES ]
- You need Telegram API ID and API Hash to use this tool
- Get API ID and Hash from my.telegram.org:
  1. Visit the website
  2. Login with your phone number
  3. Enter Telegram verification code
  4. Click "API development tools"
  5. Create new application and copy API ID & Hash
- Keep these numbers secure and never share them
- For more info, read HELP_FAQ.md
""")

def get_api_credentials():
    print(f"""{Fore.YELLOW}
[ GET API ID & HASH ]
-------------------
1. Go to my.telegram.org
2. Login with your phone number
3. Enter Telegram verification code
4. Click "API development tools"
5. Create new application:
   - App title: Any name (e.g., MyApp)
   - Short name: Any short name (e.g., myapp)
   - Platform: Desktop
   - Description: Any description (e.g., My Telegram App)
6. Click "Create application"
7. Copy API ID and API Hash

Note: Keep these numbers secure and never share them.
{Style.RESET_ALL}""")
    api_id = input("API ID (7-digit number): ").strip()
    api_hash = input("API Hash (32-character string): ").strip()
    return api_id, api_hash

def get_attack_info():
    print(f"{Fore.YELLOW}Select attack type:{Style.RESET_ALL}")
    print("1) Report  2) Ban (in group/channel)  3) Spam")
    attack_choice = input("> ").strip()
    attack_type = ATTACK_TYPES.get(attack_choice, "report")
    if attack_type == "ban":
        print(f"{Fore.YELLOW}Enter group/channel ID or @username:{Style.RESET_ALL}")
        group = input("> ").strip()
        print(f"{Fore.YELLOW}Enter target user ID or @username:{Style.RESET_ALL}")
        user = input("> ").strip()
        print(f"{Fore.YELLOW}How many times? (e.g., 1){Style.RESET_ALL}")
        try:
            count = int(input("> ").strip())
        except:
            count = 1
        return attack_type, (group, user), count, None
    else:
        print(f"{Fore.YELLOW}Enter target (numeric ID, @username, or t.me/ link):{Style.RESET_ALL}")
        target = input("> ").strip()
        print(f"{Fore.YELLOW}How many times? (e.g., 10){Style.RESET_ALL}")
        try:
            count = int(input("> ").strip())
        except:
            count = 10
        reason = "spam"
        if attack_type == "report":
            print(f"{Fore.YELLOW}Select report reason:{Style.RESET_ALL}")
            print("1) spam  2) violence  3) pornography  4) child abuse  5) copyright  6) fake  7) terrorism")
            reason_choice = input("> ").strip()
            reason = REASON_MAP.get(reason_choice, "spam")
        return attack_type, target, count, reason

def log_to_file(message):
    with open("attack_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

def attack(client, attack_type, target, count, reason):
    success = 0
    fail = 0
    results = []
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        if attack_type == "ban":
            group, user = target
            task = progress.add_task(f"[cyan]Banning {user} in {group}", total=count)
            for i in range(count):
                try:
                    group_entity = client.get_entity(group)
                    user_entity = client.get_entity(user)
                    rights = ChatBannedRights(until_date=None, view_messages=True)
                    client(EditBannedRequest(group_entity, user_entity, rights))
                    success += 1
                    msg = f"{Fore.GREEN}Ban {i+1}/{count} succeeded!{Style.RESET_ALL}"
                    progress.console.print(msg)
                    log_to_file(f"SUCCESS: ban {i+1}/{count} for {user} in {group}")
                    results.append((i+1, "Success"))
                except Exception as e:
                    fail += 1
                    msg = f"{Fore.RED}Ban {i+1}/{count} failed: {e}{Style.RESET_ALL}"
                    progress.console.print(msg)
                    log_to_file(f"FAIL: ban {i+1}/{count} for {user} in {group} | {e}")
                    results.append((i+1, "Fail"))
                progress.update(task, advance=1)
                time.sleep(1)
        else:
            task = progress.add_task(f"[cyan]{attack_type.title()}ing {target}", total=count)
            for i in range(count):
                try:
                    entity = client.get_entity(target)
                    if attack_type == "report":
                        client(ReportRequest(
                            peer=entity,
                            id=[],
                            reason=reason,
                            message="Reported by Telegram Report Bomber"
                        ))
                    elif attack_type == "spam":
                        client.send_message(entity, "Spam message from Telegram Report Bomber")
                    success += 1
                    msg = f"{Fore.GREEN}{attack_type.title()} {i+1}/{count} succeeded!{Style.RESET_ALL}"
                    progress.console.print(msg)
                    log_to_file(f"SUCCESS: {attack_type} {i+1}/{count} for {target}")
                    results.append((i+1, "Success"))
                except Exception as e:
                    fail += 1
                    msg = f"{Fore.RED}{attack_type.title()} {i+1}/{count} failed: {e}{Style.RESET_ALL}"
                    progress.console.print(msg)
                    log_to_file(f"FAIL: {attack_type} {i+1}/{count} for {target} | {e}")
                    results.append((i+1, "Fail"))
                progress.update(task, advance=1)
                time.sleep(1)
    print(f"\n{Fore.GREEN}Total Success: {success}{Style.RESET_ALL} | {Fore.RED}Total Fail: {fail}{Style.RESET_ALL}")
    # Show live table of results
    table = Table(title="Attack Results", show_lines=True)
    table.add_column("#", justify="center")
    table.add_column("Status", justify="center")
    for idx, status in results:
        color = "green" if status == "Success" else "red"
        table.add_row(str(idx), f"[{color}]{status}[/{color}]")
    console.print(table)

def main():
    while True:
        print_menu()
        choice = input(f"{Fore.YELLOW}Enter your choice:{Style.RESET_ALL} ").strip()
        if choice == "1":
            api_id, api_hash = get_api_credentials()
            try:
                with TelegramClient(SESSION, api_id, api_hash) as client:
                    if not client.is_user_authorized():
                        print(f"{Fore.YELLOW}You are not logged in. Please login to your Telegram account using Telethon first!{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Run this script once and follow the login instructions. After that, you won't need to login again unless you delete the session file.{Style.RESET_ALL}")
                        client.start()
                    attack_type, target, count, reason = get_attack_info()
                    attack(client, attack_type, target, count, reason)
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        elif choice == "2":
            show_help()
        elif choice == "3":
            print(f"{Fore.CYAN}Exiting. Good luck!{Style.RESET_ALL}")
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid option! Please try again.{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main() 