import concurrent.futures
import platform

from colorama import Fore, Style, just_fix_windows_console
from settings.settings import settings
from proxy_client import *
from webparser import *


if platform.system() == "Windows":
    just_fix_windows_console()


proxy_client = ProxyClient(
    open("proxy_list.txt").read().split("\n"),
    ProxyProtocol.HTTP
)
parsers = (
    Parser(proxy_client, "/schuhe/fahrradschuhe/", "велообувь"),
    Parser(proxy_client, "/schuhe/sneaker/", "кроссовки"),
    Parser(proxy_client, "/schuhe/laufschuhe/", "обувь для бега")
)

urls = []
products = []

print(f"[{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Получение URLs...")
for parser in parsers:
    n_pages = parser.get_n_pages()
    url_pack = []

    with concurrent.futures.ThreadPoolExecutor(settings.threads) as executor:
        for url in executor.map(parser.get_urls, range(1, n_pages + 1)):
            if url: url_pack += url
    
    urls.append(url_pack)

print(f"[{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] Получено {len(list(url for url_pack in urls for url in url_pack))} URLs\n")

for parser, urls_pack in zip(parsers, urls):
    n = 0

    with concurrent.futures.ThreadPoolExecutor(settings.threads) as executor:
        for variations in executor.map(parser.parse_url, urls_pack):
            if variations:
                products += variations
                n += 1

            if n % 100 == 0: print(f"[{Fore.CYAN + Style.BRIGHT}i{Style.RESET_ALL}] {parser.category}: Обработано {Style.BRIGHT + str(n) + Style.RESET_ALL} URLs")

        print(f"[{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] {parser.category}: Получено {len(products)} вариаций\n")

print(f"[{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Создание CSV...")
create_df(products).to_csv("output/intersport-products.csv", sep=settings.csv_sep, index=False, encoding="utf-8")
create_df(products, True).to_csv("output/intersport.csv", sep=settings.csv_sep, index=False, encoding="utf-8")