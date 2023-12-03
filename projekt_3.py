"""

projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Ivana ROHOVÁ

email: bytypr@gmail.com

discord: Ivana #3941

"""
import requests
import sys
from bs4 import BeautifulSoup as bs
import pandas

def response_server(url):
    """získává a analyzuje data z požadované adresy URL"""
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    return soup

def locations_all(soup):
    """vyhledá názvy jednotlivých obcí"""
    locations_all = soup.find_all("td", {"class": "overflow_name"})
    locations = [location.text for location in locations_all]
    return locations

def codes_all(soup):
    """načte kódy jednotlivých obcí"""
    codes_all = soup.find_all("td", {"class": "cislo"})
    codes = [code.text for code in codes_all]
    return codes

def parties_all(url_sub, codes):
    """vyhledá názvy jednotlivých politických stran"""
    for code in codes:
        url = f"{url_sub}{code}"
        soup = response_server(url)
        parties_soup = soup.find_all("td", {"class": "overflow_name", "headers": ["t1sa1 t1sb2", "t2sa1 t2sb2"]})
        parties = [party.text for party in parties_soup]
    return parties

def data_join(url_sub, codes, locations, parties):
    """shromažďuje, třídí a doplňuje všechna data"""
    electors = []
    envelopes = []
    valid = []
    data_votes = []
    for code in codes:
        url = f"{url_sub}{code}"
        soup = response_server(url)
        electors.append(soup.find("td", {"class": "cislo", "headers": "sa2"}).text.replace(" ", "").replace('\xa0', ''))
        envelopes.append(soup.find("td", {"class": "cislo", "headers": "sa3"}).text.replace(" ", "").replace('\xa0', ''))
        valid.append(soup.find("td", {"class": "cislo", "headers": "sa6"}).text.replace(" ", "").replace('\xa0', ''))
        votes = soup.find_all("td", {"class": "cislo", "headers": ["t1sa2 t1sb3", "t2sa2 t2sb3"]})
        votes_clear = [vote.text.replace(" ", "").replace('\xa0', '') for vote in votes]
        data_votes.append(votes_clear)
        data_1 = {'Code': codes, 'Location': locations, 'Registered': electors, 'Envelopes': envelopes, 'Valid': valid}
        data_2 = {a: [data_votes[b][c] for b in range(len(data_votes)) for c, d in enumerate(parties) if d == a] for a in parties}
        data_all = {**data_1, **data_2}
    return data_all

def csv_maker(data_all, csv_file):
    """převede získaná data do CSV"""
    table = pandas.DataFrame.from_dict(data_all)
    print ("Zapisuji výsledky do souboru CSV! ")
    table.to_csv(csv_file, index=False)
    return table

def arguments():
    """kontrola argumentů ke spuštění programu"""
    if len(sys.argv) != 3:
        print(f"Program ke svému spuštění vyžaduje 2 argumenty: URL a název výstupního souboru CSV. Ukončuji program! ")
        sys.exit()
    if not sys.argv[1].startswith("https://www.volby.cz/pls/ps2017nss/"):
        print(f"První argument není správný. Ukončuji program! ")
        sys.exit()
    if not sys.argv[2].endswith(".csv"):
        print(f"Druhý argument není správný. Ukončuji program! ")
        sys.exit()
    else:
        print(f"Stahuji data z: {sys.argv[1]} ")

def main():
    """Hlavní funkce"""
    arguments()
    csv_file = "result.csv"
    url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
    csv_file = sys.argv[2]
    url = sys.argv[1]
    url_sub = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec="
    soup=response_server(url)
    codes=codes_all(soup)
    locations=locations_all(soup)
    parties=parties_all(url_sub, codes)
    data_all=data_join(url_sub, codes, locations, parties)
    csv_maker(data_all,csv_file)
    print(f"Data uložena do souboru: {csv_file}. Ukončuji program! ")
    
if __name__ == '__main__':
    main()