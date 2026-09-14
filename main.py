import ipaddress
import socket
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[38;5;196m"
GREEN = "\033[38;5;46m"
YELLOW = "\033[38;5;226m"
CYAN = "\033[38;5;51m"
BLUE = "\033[38;5;39m"
PURPLE = "\033[38;5;135m"
GRAY = "\033[38;5;244m"
WHITE = "\033[38;5;231m"

LOGO = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢠⢕⣬⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠰⣢⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡐⣨⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠠⣱⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⣿⣟⢋⣴⣿⣿⣿⣿⣿⣿⡿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣰⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⢏⢲⠋⡜⢿⣿⣿⡿⠟⣫⣾⠟⣩⣾⡿⣫⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠐⣺⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⣮⣟⡢⣧⡿⣻⣿⣖⢫⡿⢋⣼⡿⢫⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠋⢀⢣⠏⠛⢻⣮⡓⡄⠹⣿⣯⣡⣿⡟⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢂⡽⠛⡱⣿⣿⣿⣿⣿⣿⣿⣿⠟⠠⠀⢀⣹⡮⡥⡋⢛⣿⣈⢤⠋⣿⣿⠏⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠶⢋⠐⣸⣳⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠠⢀⠱⢧⣧⢀⠃⠜⣷⣏⢀⣽⠏⢰⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡢⠋⡌⠀⢲⢣⣿⣿⣿⣿⣿⣿⡿⠁⠀⠀⠀⠁⠒⣄⠀⠑⢣⡬⠤⢻⠈⡄⡿⠀⣿⢳⣿⣿⣿⢟⢼⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣰⠞⠁⢠⠀⠄⡏⣾⣿⣿⣿⣿⣿⣿⠡⡀⠀⠀⠀⠀⠀⠐⢌⠀⠀⠙⢂⠘⠃⠀⡇⢸⠃⣼⢻⣿⡟⢁⢾⡿⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣐⢾⡏⠀⠀⢸⠀⢸⣱⣿⣿⣿⣿⣿⣿⡇⢠⠳⠀⠀⠀⠀⠀⠀⠀⠪⠔⡀⠀⠀⠀⠀⠁⢻⠀⡿⣽⡏⡐⣳⣼⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣐⠎⣾⠀⠀⠀⢸⠀⢸⣽⣿⣿⣿⣿⣿⣿⠃⡌⢠⡇⠀⠀⠀⠀⠀⠀⠀⠁⠉⠲⠡⡀⠀⠀⠀⠂⠡⠸⡏⠀⠌⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡞⢀⡇⠀⠀⠀⢈⢠⣿⣿⣿⣿⣿⣿⣿⣿⢱⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⡄⠀⠀⠀⠀⠄⢤⢵⣪⢔⡈⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃⠠⡇⠀⠀⠀⢠⡞⣼⣿⣿⣿⣿⣿⣿⣿⡸⠀⢡⢆⠀⠀⠀⠠⡀⠀⠀⠀⠀⠀⠀⠁⣔⠀⠀⠀⠈⡉⠉⠛⣷⣮⡑⢜⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣻⠀⠐⡇⠀⠀⢄⡟⢰⣿⣿⣿⣿⣿⣿⣿⡿⠁⠀⠸⢈⢦⡀⠀⠀⠇⡀⠀⠀⠀⠀⠀⠀⠑⠢⢀⠀⠐⣈⡦⡍⢂⢍⢷⣄⡿⣿⠺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠀⠈⣷⠀⣬⠏⣀⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⢀⠇⠘⡔⢣⠀⠈⠀⠈⠀⠀⠀⠀⠀⠀⠈⠀⠓⡀⠀⡐⡌⡑⡢⠐⢨⣻⣷⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⣷⠃⡀⣼⣿⣿⣿⣿⣿⣿⠟⠀⠀⣐⠎⠀⠠⠉⡌⢣⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡔⠌⠘⠣⣝⣮⣉⣀⣿⣽⡄⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⢀⡲⢛⣦⣰⢿⣿⣿⣿⣿⡿⠋⠀⠀⢠⠂⠀⠀⠀⠀⠈⠂⠨⢆⡀⠀⠐⢄⡀⢀⠀⠀⠀⡄⡱⠒⡘⠄⡀⠀⠂⠉⠛⠛⠛⠰⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⢧⡘⢹⠀⢻⢇⣿⣿⣿⣿⠟⠁⠀⠀⠀⢺⡄⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠑⠡⢒⢠⠘⡠⠀⠀⠀⠪⢄⠀⠀⠀⠀⠀⣌⠖⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⡄⢢⠈⣾⣿⣿⡿⡛⠠⠂⠒⠒⠒⠀⠚⠿⠧⠴⠄⢂⣀⡀⢀⠀⠀⠀⠀⡀⠐⣐⠇⠀⠁⠂⠅⢒⡀⢂⠐⠀⡀⣐⣌⠊⣜⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠠⡝⠀⠘⢞⢠⣿⠟⠁⠁⠀⠀⠰⠘⠊⡙⠒⠨⣀⠀⠀⠀⠀⠀⠀⠉⠉⠘⠒⠡⠡⠬⠄⠠⣀⡄⢀⠀⡀⣄⣠⣬⣆⣥⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⠐⡜⠀⠠⣀⠦⠋⠁⠀⠀⠀⠀⠀⠀⠦⠓⠚⠂⠔⡀⠙⢤⣀⡄⢀⠢⣀⣄⣠⣀⣄⣀⣄⣀⣡⣤⠰⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⠀⠀⠀⣼⡠⠕⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠢⡀⠉⠲⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢰⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣗⢿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⢀⢠⠁⠌⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠈⠣⡄⠈⢣⠀⡀⠀⠀⠀⠀⠀⠀⠀⠆⠘⠀⠀⠉⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣹⠃⡄⠔⢄⠈⠁⠙⢿⣿⣿⣿
⠀⠀⠀⠄⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢐⣴⣾⣶⠒⢤⣀⡄⠀⠈⢇⠀⠳⣀⠦⠴⠤⠔⠠⢀⠃⠄⡀⠦⠴⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⡽⢦⣼⡇⠀⠈⠀⠑⢄⠀⠀⢛⢿⣿
⠀⢀⠰⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢌⣴⣿⣿⣿⣿⠀⠀⣿⡈⢆⡀⠀⢣⠀⠌⠆⡀⠀⠀⠢⡅⠀⡐⢠⡶⢫⣾⣿⣿⣿⣿⣿⣿⣿⡿⣕⠎⣸⡇⠁⠀⠀⠀⠀⠀⠁⠢⡈⠄⢣
⠀⢠⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣰⣴⣿⣿⣿⣿⣿⡏⠀⢰⢧⠁⠈⡗⢤⠀⠳⠀⠸⡀⠀⠀⠃⢣⣴⡯⢋⣾⣿⣿⣿⣿⣿⣿⣿⣿⠉⠴⡜⢠⡿⠘⡀⠀⠀⠀⠀⠀⠀⠁⢈⢡⠀
⡀⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢐⣤⣿⣿⢿⣿⣿⣿⣿⣿⢁⣌⠏⢸⠐⠠⢡⠈⢆⣐⢡⠢⢡⠀⣀⣵⠿⠛⢠⣿⣿⣿⣿⣿⣿⣿⣿⠟⢡⣺⠉⣐⡾⠡⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠂
⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢁⣶⣿⣿⣿⠿⣱⣿⣿⣿⣿⡿⠿⠙⠀⢀⠂⡌⠐⢸⠀⠀⠉⠑⠡⠥⢃⡟⢠⠇⢨⣿⣿⣿⣿⣿⣿⣿⠟⢡⡼⠟⢁⠐⡺⡑⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡜
⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠋⣰⣿⣿⣿⣿⡿⠍⠀⠀⠀⢀⠣⠁⢈⠐⠀⠀⠀⠀⠠⢠⣽⠀⡏⠠⣾⣿⣿⣿⣿⡿⠟⡡⢼⠋⠐⣀⢖⡽⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢁
⡈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⠃⣰⣿⣿⣿⣿⣿⡏⠀⠀⠀⡀⡬⠁⠀⠀⡎⠀⠀⠀⠀⠀⠬⣇⠀⣌⡸⣿⣿⣿⣿⣟⣥⢚⠗⣁⢢⡵⠓⣁⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂
⡐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠃⢰⣿⣿⣿⣿⣿⣯⠁⡀⠠⢀⠌⠀⠀⠀⢰⠀⠀⠀⠀⠀⠀⠀⠛⣗⢌⢻⣿⣿⣿⠿⢭⠞⠴⠞⠘⠈⠀⢀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠠⠁
⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⢀⠆⠐⣾⣿⣿⢋⣾⣟⣿⠠⠄⡳⠂⠌⠀⠀⡀⠆⠀⢄⠆⠀⠀⠀⠀⠁⠀⠀⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠡
⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠆⠐⣾⣿⣿⢋⣾⣟⣿⠠⠄⡳⠂⠌⠀⠀⡀⠆⠀⢄⠆⠀⠀⠀⠀⠁⠀⠀⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠡
"""

SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 68: "dhcp", 69: "tftp", 80: "http",
    110: "pop3", 111: "rpcbind", 123: "ntp", 135: "msrpc", 137: "netbios",
    139: "netbios", 143: "imap", 161: "snmp", 389: "ldap", 443: "https",
    445: "smb", 465: "smtps", 514: "syslog", 587: "smtp", 631: "ipp",
    993: "imaps", 995: "pop3s", 1080: "socks", 1194: "openvpn", 1433: "mssql",
    1521: "oracle", 1723: "pptp", 2049: "nfs", 2082: "cpanel", 2083: "cpanel",
    3000: "node", 3306: "mysql", 3389: "rdp", 5060: "sip", 5432: "postgres",
    5900: "vnc", 5985: "winrm", 6379: "redis", 6667: "irc", 8000: "http-alt",
    8080: "http-proxy", 8443: "https-alt", 8888: "http-alt", 9000: "http-alt",
    9200: "elastic", 11211: "memcached", 27017: "mongodb", 25565: "minecraft",
    5353: "mdns", 3478: "stun", 19302: "discord-voice", 50000: "discord-rtc",
}


def color(text, c):
    return c + text + RESET


def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def loading_screen():
    clear()
    for line in LOGO.strip("\n").split("\n"):
        print(color(line, PURPLE))
    print()
    bar_width = 42
    for i in range(bar_width + 1):
        filled = color("█" * i, CYAN)
        empty = color("░" * (bar_width - i), GRAY)
        pct = int(i / bar_width * 100)
        sys.stdout.write("\r  " + color("[", WHITE) + filled + empty + color("]", WHITE) + color(" %3d%%" % pct, CYAN))
        sys.stdout.flush()
        time.sleep(0.012)
    print()
    print()
    time.sleep(0.2)


def expand_targets(raw):
    hosts = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "/" in chunk:
            try:
                net = ipaddress.ip_network(chunk, strict=False)
                hosts.extend(str(h) for h in net.hosts())
                continue
            except ValueError:
                pass
        if "-" in chunk and chunk.count(".") == 3:
            base, last = chunk.rsplit(".", 1)
            if "-" in last:
                start, end = last.split("-")
                if start.isdigit() and end.isdigit():
                    hosts.extend("%s.%d" % (base, i) for i in range(int(start), int(end) + 1))
                    continue
        hosts.append(chunk)
    return hosts


def parse_ports(raw):
    ports = set()
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start, end = chunk.split("-")
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(chunk))
    return sorted(p for p in ports if 0 < p < 65536)


def resolve(host):
    try:
        return socket.gethostbyname(host)
    except socket.error:
        return None


def scan_port(ip, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        if s.connect_ex((ip, port)) == 0:
            banner = ""
            try:
                s.settimeout(0.6)
                data = s.recv(64)
                banner = data.decode("utf-8", "ignore").strip().replace("\r", " ").replace("\n", " ")
            except socket.error:
                pass
            return port, True, banner
        return port, False, ""
    except socket.error:
        return port, False, ""
    finally:
        s.close()


def scan_host(host, ports, timeout, workers):
    ip = resolve(host)
    if ip is None:
        return host, None, []
    open_ports = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(scan_port, ip, p, timeout) for p in ports]
        for f in as_completed(futures):
            port, is_open, banner = f.result()
            if is_open:
                open_ports.append((port, banner))
    open_ports.sort()
    return host, ip, open_ports


def print_host_result(host, ip, open_ports):
    if ip is None:
        print(color("  ✖ ", RED) + color(host, WHITE) + color("  could not resolve", GRAY))
        print()
        return
    header = color("  ▸ ", CYAN) + color(host, BOLD + WHITE)
    if host != ip:
        header += color("  " + ip, GRAY)
    print(header)
    if not open_ports:
        print(color("      no open ports", GRAY))
        print()
        return
    for port, banner in open_ports:
        service = SERVICES.get(port, "unknown")
        line = color("      %-6d" % port, GREEN) + color("open  ", GREEN) + color("%-14s" % service, BLUE)
        if banner:
            line += color(banner[:48], YELLOW)
        print(line)
    print()


COMMON_PORTS = "21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,1723,3306,3389,5432,5900,6379,8080,8443,27017"


def ask(prompt, default=""):
    hint = color(" [%s]" % default, GRAY) if default else ""
    sys.stdout.write(color("  " + prompt, WHITE) + hint + color(" > ", CYAN))
    sys.stdout.flush()
    value = sys.stdin.readline().strip()
    return value if value else default


def run_scan(targets, ports_raw, timeout=0.5, workers=400):
    hosts = expand_targets(targets)
    ports = parse_ports(ports_raw)
    if not hosts:
        print(color("  no valid targets", RED))
        return
    if not ports:
        print(color("  no valid ports", RED))
        return
    print()
    print(color("  targets ", GRAY) + color(str(len(hosts)), WHITE) + color("   ports ", GRAY) + color(str(len(ports)), WHITE) + color("   timeout ", GRAY) + color("%.1fs" % timeout, WHITE))
    print(color("  " + "─" * 56, GRAY))
    print()
    start = time.time()
    total_open = 0
    for host in hosts:
        h, ip, open_ports = scan_host(host, ports, timeout, workers)
        total_open += len(open_ports)
        print_host_result(h, ip, open_ports)
    elapsed = time.time() - start
    print(color("  " + "─" * 56, GRAY))
    print(color("  done  ", CYAN) + color("%d open" % total_open, GREEN) + color("  across %d host(s)" % len(hosts), WHITE) + color("  in %.2fs" % elapsed, GRAY))


def ping_host(host):
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", host],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return host, result.returncode == 0
    except OSError:
        return host, False


def run_discovery(targets):
    hosts = expand_targets(targets)
    if not hosts:
        print(color("  no valid targets", RED))
        return
    print()
    print(color("  sweeping ", GRAY) + color(str(len(hosts)), WHITE) + color(" host(s)", GRAY))
    print(color("  " + "─" * 56, GRAY))
    print()
    live = []
    with ThreadPoolExecutor(max_workers=100) as pool:
        for host, up in pool.map(lambda h: ping_host(h), hosts):
            if up:
                live.append(host)
                print(color("  ● ", GREEN) + color(host, WHITE) + color("  alive", GREEN))
    print()
    print(color("  " + "─" * 56, GRAY))
    print(color("  %d of %d host(s) alive" % (len(live), len(hosts)), CYAN))


def run_lookup(host):
    print()
    try:
        ip = socket.gethostbyname(host)
        print(color("  " + host, WHITE) + color("  ->  ", GRAY) + color(ip, GREEN))
    except socket.error:
        print(color("  could not resolve " + host, RED))
        return
    try:
        name = socket.gethostbyaddr(ip)[0]
        print(color("  reverse  ", GRAY) + color(name, BLUE))
    except socket.error:
        print(color("  reverse  ", GRAY) + color("none", GRAY))


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except socket.error:
        return "unknown"
    finally:
        s.close()


def public_ip():
    try:
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "curl"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return resp.read().decode().strip()
    except Exception:
        return "unavailable"


def run_myip():
    print()
    print(color("  local   ", GRAY) + color(local_ip(), GREEN))
    print(color("  public  ", GRAY) + color(public_ip(), GREEN))
    print(color("  host    ", GRAY) + color(socket.gethostname(), WHITE))


def run_banner(host, port):
    print()
    ip = resolve(host)
    if ip is None:
        print(color("  could not resolve " + host, RED))
        return
    p, is_open, banner = scan_port(ip, port, 2.0)
    if not is_open:
        print(color("  %s:%d closed" % (host, port), RED))
        return
    service = SERVICES.get(port, "unknown")
    print(color("  %s:%d " % (host, port), WHITE) + color("open  ", GREEN) + color(service, BLUE))
    if banner:
        print(color("  banner  ", GRAY) + color(banner[:120], YELLOW))
    else:
        print(color("  banner  ", GRAY) + color("none returned", GRAY))


def menu():
    print()
    print(color("  ┌" + "─" * 40 + "┐", PURPLE))
    items = [
        ("1", "Scan one machine"),
        ("2", "Scan a range or network"),
        ("3", "Quick scan (common ports)"),
        ("4", "Find live machines"),
        ("5", "Look up a hostname / IP"),
        ("6", "Show my IP addresses"),
        ("7", "Grab a single port banner"),
        ("0", "Exit"),
    ]
    for key, label in items:
        print(color("  │ ", PURPLE) + color(key, CYAN) + color("  " + label.ljust(36), WHITE) + color("│", PURPLE))
    print(color("  └" + "─" * 40 + "┘", PURPLE))
    return ask("choose", "1")


def main():
    loading_screen()
    while True:
        choice = menu()
        if choice == "0":
            print(color("\n  made by Envio\n", PURPLE))
            return
        elif choice == "1":
            target = ask("machine (ip or hostname)")
            if target:
                ports = ask("ports", "1-1024")
                run_scan(target, ports)
        elif choice == "2":
            target = ask("range or network (e.g. 192.168.1.1-50 or 192.168.1.0/24)")
            if target:
                ports = ask("ports", COMMON_PORTS)
                run_scan(target, ports)
        elif choice == "3":
            target = ask("machine or range")
            if target:
                run_scan(target, COMMON_PORTS)
        elif choice == "4":
            target = ask("range or network")
            if target:
                run_discovery(target)
        elif choice == "5":
            target = ask("hostname or ip")
            if target:
                run_lookup(target)
        elif choice == "6":
            run_myip()
        elif choice == "7":
            target = ask("machine")
            port = ask("port", "80")
            if target and port.isdigit():
                run_banner(target, int(port))
        else:
            print(color("  unknown choice", RED))
        print()
        ask("press enter to continue")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color("\n  aborted", RED))
        sys.exit(130)
    except EOFError:
        sys.exit(0)
