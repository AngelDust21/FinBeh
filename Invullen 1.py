import pandas as pd
from tabulate import tabulate
from datetime import datetime
import os
import time
from colorama import init, Fore
from tqdm import tqdm
from pyfiglet import Figlet

# Initialize colorama
init(autoreset=True)

BESTANDSNAAM = "historiek.txt"
GEBRUIKERSBESTAND = "gebruikers.txt"

# Functie om een laadbalk te tonen
def toon_laadbalk(seconden=5, bericht="Bezig met verwerken"):
    """
    Toont een laadbalk voor een bepaald aantal seconden.
    """
    print(Fore.YELLOW + bericht)
    for _ in tqdm(range(seconden), desc=bericht, ncols=75, colour='green'):
        time.sleep(1)

# Functie om ASCII-art titel te tonen
def toon_titel():
    """
    Toont de titel van het programma in ASCII-art.
    """
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Financieel Beheer'))

# Functie om gebruikers te beheren
def gebruikersbeheer():
    """
    Beheert het inlogproces voor gebruikers.
    """
    gebruikers = laad_gebruikers()
    while True:
        print(Fore.CYAN + "\n--- Gebruikersbeheer ---")
        keuze = input("1. Inloggen\n2. Registreren\nKies een optie (1-2): ").strip()
        if keuze == '1':
            username = input("Gebruikersnaam: ").strip()
            wachtwoord = input("Wachtwoord: ").strip()
            toon_laadbalk(2, "Bezig met inloggen")
            if username in gebruikers and gebruikers[username] == wachtwoord:
                print(Fore.GREEN + "Inloggen succesvol!")
                return username
            else:
                print(Fore.RED + "Ongeldige gebruikersnaam of wachtwoord.")
        elif keuze == '2':
            username = input("Kies een gebruikersnaam: ").strip()
            if username in gebruikers:
                print(Fore.RED + "Gebruikersnaam bestaat al. Kies een andere.")
                continue
            wachtwoord = input("Kies een wachtwoord: ").strip()
            gebruikers[username] = wachtwoord
            sla_gebruikers_op(gebruikers)
            toon_laadbalk(2, "Account aan het aanmaken")
            print(Fore.GREEN + "Registratie succesvol! Je kunt nu inloggen.")
        else:
            print(Fore.RED + "Ongeldige keuze, probeer opnieuw.")

# Functie om gebruikers te laden
def laad_gebruikers():
    """
    Laadt de gebruikers uit het bestand.
    """
    gebruikers = {}
    if os.path.exists(GEBRUIKERSBESTAND):
        with open(GEBRUIKERSBESTAND, "r") as f:
            for line in f:
                if line.strip() == "":
                    continue
                username, wachtwoord = line.strip().split(";")
                gebruikers[username] = wachtwoord
    return gebruikers

# Functie om gebruikers op te slaan
def sla_gebruikers_op(gebruikers):
    """
    Slaat de gebruikers op in het bestand.
    """
    with open(GEBRUIKERSBESTAND, "w") as f:
        for username, wachtwoord in gebruikers.items():
            f.write(f"{username};{wachtwoord}\n")

# Functie om bedragen van de gebruiker te vragen
def vraag_bedragen(categorieen):
    """
    Vraagt de bedragen voor de opgegeven categorieën aan de gebruiker.
    """
    bedragen = {}
    for categorie in categorieen:
        while True:
            invoer = input(Fore.BLUE + f"Voer het bedrag in voor {categorie} (laat leeg voor 0): ").strip()
            if invoer == "":
                bedragen[categorie] = 0.0  # Stel bedrag in op 0 als invoer leeg is
                break
            try:
                bedrag = float(invoer.replace(',', '.'))
                bedragen[categorie] = bedrag
                break
            except ValueError:
                print(Fore.RED + "Ongeldige invoer. Voer een geldig getal in.")
    return bedragen

# Functie om de datum in te voeren met validatie
def vraag_datum_met_streepjes():
    """
    Vraagt de datum in het formaat dd-mm-jjjj met validatie.
    """
    while True:
        datum_input = input(Fore.BLUE + "Voer de datum in (dd-mm-jjjj): ").strip()
        try:
            datum = datetime.strptime(datum_input, "%d-%m-%Y")
            return datum
        except ValueError:
            print(Fore.RED + "Ongeldige datum. Gebruik het formaat dd-mm-jjjj.")

# Functie om de geschiedenis te tonen, gesorteerd op datum
def toon_historiek(historiek):
    """
    Toont de volledige historiek gesorteerd op datum.
    """
    print(Fore.CYAN + "\n--- Historiek ---")
    if not historiek:
        print(Fore.YELLOW + "Er zijn nog geen records in de historiek.")
        return

    # Sorteer de historiek op datum
    gesorteerde_historiek = sorted(historiek, key=lambda x: x['Datum'])

    # Toon alle records in de gesorteerde historiek
    for index, record in enumerate(gesorteerde_historiek):
        print(Fore.GREEN + f"\nDatum: {record['Datum'].strftime('%d-%m-%Y')}")
        df = pd.DataFrame(record['Gegevens'])
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))

# Functie om de historiek op te slaan in een .txt bestand
def sla_historiek_op(historiek):
    """
    Slaat de historiek op in een tekstbestand.
    """
    with open(BESTANDSNAAM, "w") as f:
        for record in historiek:
            datum_str = record['Datum'].strftime("%d-%m-%Y")
            gegevens = record['Gegevens']
            f.write(
                f"{datum_str};{gegevens['Bedrag'][0]};{gegevens['Bedrag'][1]};{gegevens['Bedrag'][2]};{gegevens['Bedrag'][3]}\n")

# Functie om historiek in te laden vanuit een .txt bestand
def laad_historiek():
    """
    Laadt de historiek uit een tekstbestand.
    """
    historiek = []
    if os.path.exists(BESTANDSNAAM):
        with open(BESTANDSNAAM, "r") as f:
            for line in f:
                if line.strip() == "":
                    continue
                parts = line.strip().split(";")
                if len(parts) != 5:
                    continue
                datum_str, oud_saldo, totaal_inkomen, totaal_uitgaven, nieuw_saldo = parts
                try:
                    datum = datetime.strptime(datum_str, "%d-%m-%Y").date()
                    record = {
                        'Datum': datum,
                        'Gegevens': {
                            'Categorie': ['Oud Saldo', 'Totaal Inkomsten', 'Totaal Uitgaven', 'Nieuw Saldo'],
                            'Bedrag': [float(oud_saldo), float(totaal_inkomen), float(totaal_uitgaven), float(nieuw_saldo)]
                        }
                    }
                    historiek.append(record)
                except ValueError:
                    continue  # Als er een fout is in de data, sla die dan over
    return historiek

# Functie om een dag in de historiek aan te passen
def wijzig_dag(historiek):
    """
    Wijzigt de gegevens van een bestaande dag in de historiek.
    """
    print(Fore.CYAN + "\n--- Wijzig een bestaande dag ---")
    # Vraag de datum van de dag die je wilt wijzigen
    datum_input = vraag_datum_met_streepjes()
    datum = datum_input.date()

    # Zoek de dag met de ingevoerde datum
    for index, record in enumerate(historiek):
        if record["Datum"] == datum:
            print(Fore.GREEN + f"\n--- Wijzig gegevens voor {datum.strftime('%d-%m-%Y')} ---")

            # Vraag de nieuwe gegevens voor de inkomsten en uitgaven
            inkomsten_categorieen = ['Visa en Bank contact', 'Payconiq', 'Open Facturen', 'Cash']
            uitgaven_categorieen = ['Visa en Bank contact', 'Payconiq', 'Openstaande facturen', 'Betaalde facturen', 'Gestort']

            print(Fore.CYAN + "\n--- Vul de nieuwe inkomsten in ---")
            nieuwe_inkomsten = vraag_bedragen(inkomsten_categorieen)

            print(Fore.CYAN + "\n--- Vul de nieuwe uitgaven in ---")
            nieuwe_uitgaven = vraag_bedragen(uitgaven_categorieen)

            # Update het record in de historiek
            totaal_inkomen = sum(nieuwe_inkomsten.values())
            totaal_uitgaven = sum(nieuwe_uitgaven.values())
            oud_saldo = historiek[index - 1]['Gegevens']["Bedrag"][3] if index > 0 else 0.0
            nieuw_saldo = oud_saldo + totaal_inkomen - totaal_uitgaven

            record['Gegevens'] = {
                'Categorie': ['Oud Saldo', 'Totaal Inkomsten', 'Totaal Uitgaven', 'Nieuw Saldo'],
                'Bedrag': [oud_saldo, totaal_inkomen, totaal_uitgaven, nieuw_saldo]
            }

            # Recalculate all subsequent records
            herbereken_saldi(historiek, start_index=index)
            sla_historiek_op(historiek)

            print(Fore.GREEN + f"\nDe gegevens voor {datum.strftime('%d-%m-%Y')} zijn bijgewerkt.")
            return

    print(Fore.RED + f"Geen gegevens gevonden voor {datum.strftime('%d-%m-%Y')}.")

# Functie om een dag uit de historiek te verwijderen
def verwijder_dag(historiek):
    """
    Verwijdert een bestaande dag uit de historiek.
    """
    print(Fore.CYAN + "\n--- Verwijder een bestaande dag ---")
    datum_input = vraag_datum_met_streepjes()
    datum = datum_input.date()

    for index, record in enumerate(historiek):
        if record["Datum"] == datum:
            bevestiging = input(Fore.YELLOW + f"Weet je zeker dat je de gegevens voor {datum.strftime('%d-%m-%Y')} wilt verwijderen? (ja/nee): ").strip().lower()
            if bevestiging == 'ja':
                historiek.pop(index)
                herbereken_saldi(historiek, start_index=index)
                sla_historiek_op(historiek)
                toon_laadbalk(2, "Verwijderen")
                print(Fore.GREEN + "Dag succesvol verwijderd.")
            else:
                print(Fore.YELLOW + "Verwijderen geannuleerd.")
            return
    print(Fore.RED + f"Geen gegevens gevonden voor {datum.strftime('%d-%m-%Y')}.")

# Functie om de saldi van de historiek te herberekenen
def herbereken_saldi(historiek, start_index=0):
    """
    Herberekent de saldi vanaf een bepaald startpunt in de historiek.
    """
    # Sorteer de historiek op datum
    gesorteerde_historiek = sorted(historiek, key=lambda x: x['Datum'])

    # Begin met de herberekening vanaf de start_index
    for i in range(start_index, len(gesorteerde_historiek)):
        if i == 0:
            oud_saldo = 0.0
        else:
            oud_saldo = gesorteerde_historiek[i - 1]['Gegevens']["Bedrag"][3]
        totaal_inkomen = gesorteerde_historiek[i]['Gegevens']["Bedrag"][1]
        totaal_uitgaven = gesorteerde_historiek[i]['Gegevens']["Bedrag"][2]
        nieuw_saldo = oud_saldo + totaal_inkomen - totaal_uitgaven

        gesorteerde_historiek[i]['Gegevens']["Bedrag"][0] = oud_saldo
        gesorteerde_historiek[i]['Gegevens']["Bedrag"][3] = nieuw_saldo

# Functie om een samenvatting te tonen
def toon_samenvatting(historiek):
    """
    Toont een samenvatting van alle inkomsten en uitgaven.
    """
    print(Fore.CYAN + "\n--- Samenvatting ---")
    if not historiek:
        print(Fore.YELLOW + "Er zijn nog geen records in de historiek.")
        return

    totaal_inkomsten = sum(record['Gegevens']['Bedrag'][1] for record in historiek)
    totaal_uitgaven = sum(record['Gegevens']['Bedrag'][2] for record in historiek)
    eindsaldo = historiek[-1]['Gegevens']['Bedrag'][3]

    print(Fore.GREEN + f"Totaal Inkomsten: {totaal_inkomsten}")
    print(Fore.RED + f"Totaal Uitgaven: {totaal_uitgaven}")
    print(Fore.BLUE + f"Eindsaldo: {eindsaldo}")

# Functie om data te exporteren naar Excel
def exporteer_naar_excel(historiek):
    """
    Exporteert de historiek naar een Excel-bestand.
    """
    if not historiek:
        print(Fore.YELLOW + "Er zijn geen gegevens om te exporteren.")
        return

    # Maak een DataFrame voor export
    data = []
    for record in historiek:
        data.append({
            'Datum': record['Datum'].strftime('%d-%m-%Y'),
            'Oud Saldo': record['Gegevens']['Bedrag'][0],
            'Totaal Inkomsten': record['Gegevens']['Bedrag'][1],
            'Totaal Uitgaven': record['Gegevens']['Bedrag'][2],
            'Nieuw Saldo': record['Gegevens']['Bedrag'][3]
        })
    df = pd.DataFrame(data)
    bestandsnaam = 'historiek_export.xlsx'
    df.to_excel(bestandsnaam, index=False, engine='openpyxl')
    print(Fore.GREEN + f"Historiek succesvol geëxporteerd naar {bestandsnaam}.")

# Functie om instellingen te beheren
def beheer_instellingen():
    """
    Beheert de instellingen van het programma.
    """
    print(Fore.CYAN + "\n--- Instellingen ---")
    print("1. Wijzig wachtwoord")
    print("2. Terug naar hoofdmenu")
    keuze = input("Kies een optie (1-2): ").strip()
    if keuze == '1':
        nieuw_wachtwoord = input("Voer een nieuw wachtwoord in: ").strip()
        gebruikers = laad_gebruikers()
        gebruikers[username] = nieuw_wachtwoord
        sla_gebruikers_op(gebruikers)
        print(Fore.GREEN + "Wachtwoord succesvol gewijzigd.")
    elif keuze == '2':
        return
    else:
        print(Fore.RED + "Ongeldige keuze.")

# Functie om hulpinformatie te tonen
def toon_hulp():
    """
    Toont hulpinformatie over het programma.
    """
    print(Fore.CYAN + "\n--- Hulp ---")
    print(Fore.YELLOW + "Dit programma helpt je bij het beheren van je financiën.")
    print("Je kunt inkomsten en uitgaven invoeren, je historiek bekijken, gegevens wijzigen en meer.")
    print("Gebruik het menu om de gewenste acties te selecteren.")

# Start van het programma
def main():
    """
    De hoofdprogrammafunctie die alle onderdelen aanroept.
    """
    toon_titel()
    global username
    username = gebruikersbeheer()
    historiek = laad_historiek()

    # Categorieën voor inkomsten en uitgaven
    inkomsten_categorieen = ['Visa en Bank contact', 'Payconiq', 'Open Facturen', 'Cash']
    uitgaven_categorieen = ['Visa en Bank contact', 'Payconiq', 'Openstaande facturen', 'Betaalde facturen', 'Gestort']

    # Programma loop voor meerdere dagen
    while True:
        # Toon opties aan de gebruiker
        print(Fore.CYAN + f"\n--- Menu (Ingelogd als: {username}) ---")
        print("1. Toon historiek")
        print("2. Voeg een nieuwe dag toe")
        print("3. Wijzig een bestaande dag")
        print("4. Verwijder een dag")
        print("5. Toon samenvatting")
        print("6. Exporteer naar Excel")
        print("7. Instellingen")
        print("8. Hulp")
        print("9. Uitloggen")
        print("10. Stop het programma")

        keuze = input(Fore.BLUE + "Kies een optie (1-10): ").strip()

        if keuze == '1':
            toon_laadbalk(2, "Historiek laden")
            toon_historiek(historiek)
        elif keuze == '2':
            print(Fore.CYAN + "\n--- Voeg een nieuwe dag toe ---")

            # Vraag de datum van de dag met automatische streepjes
            datum_input = vraag_datum_met_streepjes()
            datum = datum_input.date()

            # Controleer of de datum al bestaat
            if any(record['Datum'] == datum for record in historiek):
                print(Fore.RED + "Er bestaat al een record voor deze datum.")
                continue

            # Stel het oude saldo in
            if historiek:
                laatste_dag = sorted(historiek, key=lambda x: x['Datum'])[-1]
                oud_saldo = laatste_dag['Gegevens']["Bedrag"][3]
            else:
                while True:
                    try:
                        oud_saldo = float(input(Fore.BLUE + "Voer het oude saldo voor de eerste dag in: ").strip())
                        break
                    except ValueError:
                        print(Fore.RED + "Ongeldige invoer. Voer een geldig getal in.")

            # Vraag inkomsten en uitgaven van de gebruiker
            print(Fore.CYAN + "\n--- Vul de inkomsten in ---")
            inkomsten = vraag_bedragen(inkomsten_categorieen)

            print(Fore.CYAN + "\n--- Vul de uitgaven in ---")
            uitgaven = vraag_bedragen(uitgaven_categorieen)

            # Bereken totaal inkomen en uitgaven
            totaal_inkomen = sum(inkomsten.values())
            totaal_uitgaven = sum(uitgaven.values())

            # Bereken nieuw saldo
            nieuw_saldo = oud_saldo + totaal_inkomen - totaal_uitgaven

            # Maak een record voor deze dag
            record = {
                'Categorie': ['Oud Saldo', 'Totaal Inkomsten', 'Totaal Uitgaven', 'Nieuw Saldo'],
                'Bedrag': [oud_saldo, totaal_inkomen, totaal_uitgaven, nieuw_saldo]
            }

            # Voeg datum en record toe aan de historiek
            historiek.append({"Datum": datum, "Gegevens": record})

            # Herbereken alle saldi om ervoor te zorgen dat de historiek consistent blijft
            herbereken_saldi(historiek)
            sla_historiek_op(historiek)

            # Toon overzicht van de dag
            toon_laadbalk(2, "Gegevens verwerken")
            print(Fore.GREEN + "\n--- Overzicht van de dag ---")
            df = pd.DataFrame(record)
            print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))

        elif keuze == '3':
            toon_laadbalk(2, "Gegevens laden")
            wijzig_dag(historiek)

        elif keuze == '4':
            verwijder_dag(historiek)

        elif keuze == '5':
            toon_samenvatting(historiek)

        elif keuze == '6':
            exporteer_naar_excel(historiek)

        elif keuze == '7':
            beheer_instellingen()

        elif keuze == '8':
            toon_hulp()

        elif keuze == '9':
            print(Fore.YELLOW + "Uitloggen...")
            toon_laadbalk(2, "Uitloggen")
            username = gebruikersbeheer()

        elif keuze == '10':
            print(Fore.GREEN + "Programma beëindigd.")
            break
        else:
            print(Fore.RED + "Ongeldige keuze, probeer opnieuw.")

    print(Fore.GREEN + "Dank je wel voor het gebruik van het programma!")

if __name__ == "__main__":
    main()
