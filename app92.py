import streamlit as st
import lxml.etree as et
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt


# Définir BASE_DIR pour le chemin relatif
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



# Configuration de la page Streamlit
st.set_page_config(page_title="Cash App", layout="wide")

# Chargement des données
#@st.cache_data  # Mise en cache des données
# Fonction pour charger les données de Data.xlsx
def load_data():
    file_path = r'data/Data.xlsx'  # Spécifiez le chemin correct
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        st.warning("Le fichier Data.xlsx est introuvable. Veuillez vérifier le chemin.")
        return pd.DataFrame()

# Charger l'historique des transactions
def load_history():
    data = pd.read_excel('data/Data.xlsx')
    return data

# Charger les données de Prêt.xlsx
@st.cache_data  # Mise en cache des données
def load_pret_data():
    pret_data = pd.read_excel('data/Prêt.xlsx')
    return pret_data

# Chargement des données
data = load_data()
pret_data = load_pret_data()

# Fonction pour enregistrer les nouvelles transactions dans Data.xlsx
def save_to_excel(transactions):
    file_path = os.path.join(BASE_DIR, 'data', 'Data.xlsx')  # Utiliser un chemin relatif

    # Charger les données existantes
    existing_data = load_data()

    # Concaténer les nouvelles transactions avec les données existantes
    combined_data = pd.concat([existing_data, transactions], ignore_index=True)

    # Réorganiser les colonnes selon le format requis
    combined_data = combined_data[['Date', 'Libellé', 'Catégorie', 'Prix', 'Solde', 'Compte']]

    # Enregistrer dans le fichier Excel
    combined_data.to_excel(file_path, index=False)


# Onglets en haut
tabs = st.tabs(["Data", "Soldes", "Graphique", "Import", "Bourse","Trading"])




# Onglet Data
with tabs[0]:  # Supposons que cet onglet soit le premier
    st.title("Données")
    
    # Charger les données initiales
    data = load_data()
    
    # Bouton d'actualisation
    if st.button("Actualiser les données"):
        data = load_data()  # Recharger les données
        st.success("Données actualisées avec succès !")
    
    # Afficher les données
    st.dataframe(data, use_container_width=True)



# Onglet Soldes
with tabs[1]:
    st.title("Soldes")

    # Bouton d'actualisation
    if st.button("Actualiser les soldes"):
        # Charger les données mises à jour
        data = load_data()  # Assurez-vous d'appeler la fonction pour charger les données mises à jour

        # Convertir la colonne Date en datetime
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d', errors='coerce')

        # Initialiser le tableau de soldes
        dates = pd.date_range(start='2016-12-31', end=data['Date'].max(), freq='D')
        comptes = data['Compte'].unique().tolist()

        # Création d'un DataFrame vide pour stocker les soldes
        soldes = pd.DataFrame(index=dates, columns=comptes + ['Immobilier'])

        # Remplir le DataFrame de soldes
        for compte in comptes:
            transactions = data[data['Compte'] == compte].sort_values(by='Date')
            solde = 0

            for date in dates:
                if date in transactions['Date'].values:
                    transaction = transactions[transactions['Date'] == date]
                    solde = transaction['Solde'].values[0] if not transaction.empty else solde
                soldes.at[date, compte] = solde

        # Ajout des données du prêt dans la colonne 'Immobilier'
        solde_immobilier = None

        for _, row in pret_data.iterrows():
            row_date = pd.to_datetime(row['Date'])
            if row_date >= pd.to_datetime('2016-12-31'):
                solde_immobilier = row['Détention réelle']
                soldes.at[row_date, 'Immobilier'] = solde_immobilier

                for date in dates:
                    if date >= row_date and soldes.at[date, 'Immobilier'] is None:
                        soldes.at[date, 'Immobilier'] = solde_immobilier

        soldes['Immobilier'].fillna(method='ffill', inplace=True)
        last_date = data['Date'].max()
        soldes_truncated = soldes.loc[soldes.index <= last_date]

        st.dataframe(soldes_truncated, use_container_width=True)
        st.success("Soldes actualisés avec succès !")  # Message de succès
    else:
        # Si le bouton n'est pas cliqué, charger les données existantes par défaut
        data = load_data()
        
        # Convertir la colonne Date en datetime
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d', errors='coerce')

        # Initialiser le tableau de soldes
        dates = pd.date_range(start='2016-12-31', end=data['Date'].max(), freq='D')
        comptes = data['Compte'].unique().tolist()

        # Création d'un DataFrame vide pour stocker les soldes
        soldes = pd.DataFrame(index=dates, columns=comptes + ['Immobilier'])

        # Remplir le DataFrame de soldes
        for compte in comptes:
            transactions = data[data['Compte'] == compte].sort_values(by='Date')
            solde = 0

            for date in dates:
                if date in transactions['Date'].values:
                    transaction = transactions[transactions['Date'] == date]
                    solde = transaction['Solde'].values[0] if not transaction.empty else solde
                soldes.at[date, compte] = solde

        # Ajout des données du prêt dans la colonne 'Immobilier'
        solde_immobilier = None

        for _, row in pret_data.iterrows():
            row_date = pd.to_datetime(row['Date'])
            if row_date >= pd.to_datetime('2016-12-31'):
                solde_immobilier = row['Détention réelle']
                soldes.at[row_date, 'Immobilier'] = solde_immobilier

                for date in dates:
                    if date >= row_date and soldes.at[date, 'Immobilier'] is None:
                        soldes.at[date, 'Immobilier'] = solde_immobilier

        soldes['Immobilier'].fillna(method='ffill', inplace=True)
        last_date = data['Date'].max()
        soldes_truncated = soldes.loc[soldes.index <= last_date]

        st.dataframe(soldes_truncated, use_container_width=True)






    # Étape 1 : Identifier les dates de versement de salaire dans `data`
    compte_courant = "Cpt 01900 00031437702"

    # Filtrer les transactions du compte courant pour les montants de salaire, excluant les transferts
    salaire_transactions = data[
        (data['Compte'] == compte_courant) &
        (data['Prix'] >= 2000) &
        (data['Catégorie'] != "Transfert") &  # Exclure les transactions de type "Transfert"
        (
            ((data['Date'].dt.day >= 20) & (data['Date'].dt.day <= 31)) |  # Du 20 au 31 du mois courant
            ((data['Date'].dt.day >= 1) & (data['Date'].dt.day <= 2))      # Du 1er au 2 du mois suivant
        )
    ]

    # Grouper par date pour obtenir le solde en fin de journée pour chaque date (dernier enregistrement de chaque jour)
    salaire_transactions = salaire_transactions.sort_values('Date').drop_duplicates(subset='Date', keep='last')

    # Extraire les dates de versement de salaire (les dernières 12 dates)
    versement_dates = salaire_transactions['Date'].values[-12:]

    # Étape 2 : Tracer l'évolution normalisée des soldes en base 100% pour chaque mois de salaire
    fig_base_100 = go.Figure()

    # Identifier le dernier mois disponible dans les données
    dernier_mois = salaire_transactions['Date'].max().to_period('M')

    # Créer une palette de couleurs en dégradé de bleu
    bleu_palette = [
        '#E1F5FE',  # bleu très clair
        '#B3E5FC',  # bleu clair
        '#81D4FA',  # bleu clair
        '#4FC3F7',  # bleu
        '#29B6F6',  # bleu
        '#03A9F4',  # bleu
        '#039BE5',  # bleu moyen
        '#0288D1',  # bleu moyen
        '#0277BD',  # bleu foncé
        '#01579B',  # bleu très foncé
        '#003F5C'   # bleu marine
    ]

    # Liste pour stocker les soldes normalisés par jour
    saldos_normalises_dict = {}

    for i in range(len(versement_dates) - 1):
        start_date = pd.to_datetime(versement_dates[i])
        end_date = pd.to_datetime(versement_dates[i + 1])

        # Récupérer les transactions du compte entre start_date et end_date dans `data`
        periode_salaire = data[
            (data['Compte'] == compte_courant) &
            (data['Catégorie'] != "Transfert") &  # Exclure les transactions de type "Transfert"
            (data['Date'] >= start_date) & 
            (data['Date'] < end_date)
        ]

        # Grouper les transactions par date pour obtenir le solde en fin de journée (dernier solde de chaque jour)
        periode_salaire = periode_salaire.sort_values('Date').drop_duplicates(subset='Date', keep='last')
        
        # Calculer les jours D0, D1, ..., Dn en fonction de start_date
        jours = [(d - start_date).days for d in periode_salaire['Date']]
        
        # Normaliser les soldes pour que D0 soit à 100%
        solde_D0 = periode_salaire['Solde'].iloc[0]
        solde_normalise = (periode_salaire['Solde'] / solde_D0) * 100
        
        # Stocker les soldes normalisés dans un dictionnaire par jour
        for j, jour in enumerate(jours):
            if jour not in saldos_normalises_dict:
                saldos_normalises_dict[jour] = []
            saldos_normalises_dict[jour].append(solde_normalise.iloc[j])
        
        # Déterminer la couleur pour le tracé : rouge pour le dernier mois, sinon un bleu dégradé
        if end_date.to_period('M') == dernier_mois:  # le dernier mois dans les données
            color = 'red'
        else:
            color = bleu_palette[i % len(bleu_palette)]

        # Ajouter une trace pour la période de salaire au graphique normalisé
        nom_mois_precedent = (end_date + pd.DateOffset(months=1)).strftime('%Y-%m')  # Format YYYY-MM
        fig_base_100.add_trace(go.Scatter(x=jours, y=solde_normalise,
                                            mode='lines+markers',
                                            name=nom_mois_precedent,  # Format YYYY-MM
                                            line=dict(color=color)))

    # Calculer la moyenne des soldes normalisés par jour
    jours_moyenne = sorted(saldos_normalises_dict.keys())
    moyenne_normalisee = [np.mean(saldos_normalises_dict[jour]) for jour in jours_moyenne]

    # Tracer la moyenne en jaune
    fig_base_100.add_trace(go.Scatter(x=jours_moyenne, y=moyenne_normalisee,
                                        mode='lines',
                                        name='Moyenne Normalisée',
                                        line=dict(color='#F3D440', width=2)))

    # Configurer le layout du graphique normalisé
    fig_base_100.update_layout(
        title="Évolution normalisée du solde par 'mois de salaire' (dernier 12 mois, base 100%)",
        xaxis_title="Jour (D0 à Dn)",
        yaxis_title="Solde (% de D0)",
        legend_title="Période de salaire",
        template="plotly_white"
    )

    # Afficher le graphique normalisé dans Streamlit
    st.plotly_chart(fig_base_100, use_container_width=True)





    
# Fonction pour importer les données des différents onglets
def import_transactions(file, existing_data):
    dfs = []  # Liste pour stocker les DataFrames de chaque onglet
    xls = pd.ExcelFile(file)  # Charger le fichier Excel

    for sheet_name in xls.sheet_names:
        if sheet_name != "Vos comptes":  # Ignorer l'onglet "Vos comptes"
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)  # Charger l'onglet sans en-tête
            
            # Chercher les en-têtes (généralement en ligne 5)
            header_row = 4  # Ligne d'en-tête (index 4 pour 0-based)
            if len(df) > header_row:  # Vérifier si la ligne existe
                df.columns = df.iloc[header_row]  # Définir la première ligne comme en-têtes
                df = df[header_row + 1:]  # Garder seulement les données
                df.reset_index(drop=True, inplace=True)

                # Vérifier que toutes les colonnes nécessaires existent
                required_columns = ['Date', 'Valeur', 'Libellé', 'Débit', 'Crédit', 'Solde']
                if all(col in df.columns for col in required_columns):
                    # Filtrer et renommer les colonnes
                    df = df[['Date', 'Libellé', 'Débit', 'Crédit']]
                    df['Compte'] = sheet_name  # Ajouter la colonne Compte

                    # Trouver la dernière ligne avec une date valide dans la colonne 'Date'
                    last_valid_index = df['Date'].last_valid_index()
                    if last_valid_index is not None:
                        df = df.loc[:last_valid_index]  # Garder seulement jusqu'à la dernière date valide

                    # Convertir les colonnes Débit et Crédit en float avec gestion des erreurs
                    df['Débit'] = pd.to_numeric(df['Débit'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).infer_objects()
                    df['Crédit'] = pd.to_numeric(df['Crédit'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).infer_objects()

                    # Renommer les colonnes pour correspondre au format de Data
                    df.rename(columns={
                        'Date': 'Date',
                        'Libellé': 'Libellé',
                        'Débit': 'Débit',
                        'Crédit': 'Crédit',
                        'Solde': 'Solde'
                    }, inplace=True)

                    # Supprimer les lignes où la date est NaT (non valide) ou où le Libellé est "Liste de vos comptes"
                    df = df[df['Date'].notna() & (df['Libellé'] != "Liste de vos comptes")]

                    # Convertir le format de date pour correspondre à celui de Data
                    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')

                    # Calculer Prix comme somme des colonnes Débit et Crédit
                    df['Prix'] = df['Crédit'] + df['Débit']  # Prix = Crédit + Débit

                    # Comparer avec les données existantes pour éviter les doublons
                    mask = (
                        df['Date'].isin(existing_data['Date']) &
                        df['Libellé'].isin(existing_data['Libellé']) &
                        df['Compte'].isin(existing_data['Compte']) &
                        (df['Prix'].isin(existing_data['Prix']))
                    )

                    # Garder seulement les nouvelles transactions
                    df = df[~mask]

                    # Ajouter les nouvelles transactions à la liste
                    if not df.empty:
                        dfs.append(df)

    # Combiner tous les DataFrames en un seul
    if dfs:
        transactions = pd.concat(dfs, ignore_index=True)
        return transactions
    return pd.DataFrame()  # Retourner un DataFrame vide si aucune donnée n'est trouvée

# Chargement des données existantes
def load_existing_data():
    # Charger le fichier Excel contenant les données existantes
    file_path = r'data/Data.xlsx'  # Spécifiez le chemin correct
    try:
        existing_data = pd.read_excel(file_path)
        return existing_data
    except FileNotFoundError:
        st.warning("Le fichier Data.xlsx est introuvable. Veuillez vérifier le chemin.")
        return pd.DataFrame()

# Fonction pour recalculer le solde
def recalculate_soldes(existing_data, transactions):
    # Créer un dictionnaire pour stocker les soldes par compte
    soldes = existing_data.groupby('Compte')['Solde'].last().to_dict()

    # Créer une liste pour stocker les nouveaux soldes
    nouveaux_soldes = []

    # Mettre à jour les soldes avec les nouvelles transactions
    for _, row in transactions.iterrows():
        compte = row['Compte']
        prix = row['Prix']

        # Vérifier si le compte a un solde connu
        if compte in soldes:
            # Ajouter le montant de l'opération au dernier solde connu
            nouveau_solde = soldes[compte] + prix
        else:
            # Si c'est un nouveau compte, initialiser le solde
            nouveau_solde = prix

        # Mettre à jour le dictionnaire des soldes
        soldes[compte] = nouveau_solde
        nouveaux_soldes.append(nouveau_solde)

    # Ajouter les nouveaux soldes au DataFrame des transactions
    transactions['Solde'] = nouveaux_soldes

    return transactions

# Onglet Import
with tabs[3]:
    st.title("Importation des Transactions")
    
    # Charger les données existantes
    existing_data = load_existing_data()

    # Uploader le fichier
    uploaded_file = st.file_uploader("Choisissez un fichier comptes.xlsx", type="xlsx")
    
    if uploaded_file:
        transactions = import_transactions(uploaded_file, existing_data)

        if not transactions.empty:
            st.subheader("Transactions importées")
            st.dataframe(transactions, use_container_width=True)

            # Liste des catégories pour le menu déroulant
            categories = [
                "Salaire+", "Immobilier", "Exceptionnel", "Frais bancaires", "Investissement", "Loyer", 
                "Habitat", "Courses", "Loisirs", "Restaurant", "Impôts", 
                "Retrait", "Voiture", "Énergie + Internet", "Transports", 
                "Habits", "Santé", "Prep", "Bar", "RATP", "Braska", 
                "Portable", "Livre", "Petit-Déjeuner", "Notes de Frais", "Aides", 
                "Aides CAF"
            ]

            # Créer un dictionnaire pour stocker les catégories choisies
            category_choices = {}

            for index, row in transactions.iterrows():
                transaction_label = f"Opération: {row['Libellé']} - Montant: {row['Prix']}"
                category = st.selectbox(transaction_label, categories, key=index)
                category_choices[index] = category
            
            if st.button("Enregistrer les transactions"):
                # Enregistrer les transactions avec les catégories choisies
                for idx, category in category_choices.items():
                    transactions.at[idx, 'Catégorie'] = category
                
                # Recalculer les soldes
                transactions = recalculate_soldes(existing_data, transactions)
                
                # Enregistrer les transactions dans Data.xlsx
                save_to_excel(transactions)
                st.success("Transactions enregistrées avec succès !")

class PortfolioPerformanceFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.root = None  # Initialiser self.root à None par défaut

        # Tentative de chargement du fichier XML
        try:
            self.root = et.parse(filepath)
            st.success(f"Fichier '{filepath}' chargé avec succès.")
        except OSError:
            st.error(f"Le fichier '{filepath}' est introuvable ou ne peut pas être ouvert. Vérifiez le chemin et la présence du fichier.")
        except et.XMLSyntaxError as e:
            st.error(f"Le fichier '{filepath}' ne semble pas être un fichier XML valide. Erreur : {str(e)}")

        # Vérification si le chargement a échoué
        if self.root is None:
            st.warning("Le fichier XML n'a pas été chargé correctement. Les méthodes de cette classe ne seront pas disponibles.")

    def check_for_ref_lx(self, element):
        if self.root is None or element is None:
            return None
        ref = element.attrib.get("reference")
        while ref is not None:
            element = self.root.find(self.root.getelementpath(element) + "/" + ref)
            ref = element.attrib.get("reference")
        return element
        
    def get_df_securities(self):
        dfcols = ['idx', 'uuid', 'name', 'ticker', 'isin', "wkn", "cur"]
        rows = []
        for idx, security in enumerate(self.root.findall(".//securities/security")):
            if security is not None:
                sec_idx = idx + 1
                sec_uuid = security.find('uuid').text if security.find('uuid') is not None else ""
                sec_name = security.find('name').text if security.find('name') is not None else ""
                sec_isin = security.find('isin').text if security.find('isin') is not None else ""

                # Imposer l'ISIN pour T212EUR
                if sec_name == "T212EUR" and (sec_isin is None or sec_isin == ""):
                    sec_isin = "T212EUR"

                sec_wkn = security.find('wkn').text if security.find('wkn') is not None else ""
                sec_curr = security.find('currencyCode').text if security.find('currencyCode') is not None else ""
                sec_ticker = security.find('tickerSymbol').text if security.find('tickerSymbol') is not None else ""
                rows.append([sec_idx, sec_uuid, sec_name, sec_ticker, sec_isin, sec_wkn, sec_curr])
        return pd.DataFrame(rows, columns=dfcols)


            
    def get_df_all_prices(self):
        dfcols = ['date', 'price', 'isin']
        rows = []  # Utiliser une liste pour stocker les lignes

        for security in self.root.findall(".//securities/security"):
            sec_isin = security.find('isin').text if security.find('isin') is not None else None
            for price in security.findall(".//prices/price"):
                date = price.attrib.get("t")
                price_value = float(price.attrib.get("v")) / 100000000  # Diviser par 100 000 000
                
                # Si sec_isin est None, imposer l'ISIN "T212EUR"
                if sec_isin is None:
                    sec_isin = "T212EUR"

                # Ajouter les détails à la liste de lignes
                rows.append([date, price_value, sec_isin])

        # Créer un DataFrame à partir de la liste de lignes
        df = pd.DataFrame(rows, columns=dfcols)

        # Convertir la colonne 'date' en datetime pour un meilleur tri
        df['date'] = pd.to_datetime(df['date'])

        # Pivot du DataFrame pour avoir une structure avec ISIN comme colonnes
        df = df.pivot(index='date', columns='isin', values='price')

        # Obtenir la date d'aujourd'hui
        today = pd.to_datetime('today').normalize()

        # Tronquer le DataFrame pour ne garder que les dates jusqu'à aujourd'hui
        df = df[df.index <= today]

        # Propager le dernier cours connu pour les dates manquantes
        df.ffill(inplace=True)  # Propager vers le bas

        return df
        
    def get_df_portfolios(self):
        dfcols = ['idx', 'uuid', 'name', 'currencycode', 'isretiredxpath']
        rows = []           
        for idx, portfolio in enumerate(self.root.findall(".//portfolios/portfolio")):
            portfolio = self.check_for_ref_lx(portfolio)
            ptf_idx = idx + 1 
            ptf_uuid = portfolio.find('uuid').text if portfolio.find('uuid') is not None else ""
            ptf_name = portfolio.find('name').text if portfolio.find('name') is not None else ""
            ptf_currencycode = portfolio.find("currencyCode").text if portfolio.find('currencyCode') is not None else ""
            ptf_isretired = portfolio.find("isRetired").text if portfolio.find('isRetired') is not None else ""
            rows.append([ptf_idx, ptf_uuid, ptf_name, ptf_currencycode, ptf_isretired])
        
        return pd.DataFrame(rows, columns=dfcols)
    

    
    def get_df_accounts(self):
        dfcols = ['idx', 'uuid', 'name', 'currencycode', 'isretiredxpath', "xpath"]
        rows = []  # Utiliser une liste pour stocker les lignes
        
        for idx, account in enumerate(self.root.findall('.//accounts/account')):
            account = self.check_for_ref_lx(account)
            acc_idx = idx + 1
            acc_uuid = account.find('uuid').text if account.find('uuid') is not None else ""
            acc_name = account.find('name').text if account.find('name') is not None else ""
            acc_currencycode = account.find('currencyCode').text if account.find('currencyCode') is not None else ""
            acc_isretired = account.find('isRetired').text if account.find('isRetired') is not None else ""
            acc_xpath = f".//accounts/account[{idx + 1}]"
            
            # Ajouter les détails à la liste de lignes
            rows.append([acc_idx, acc_uuid, acc_name, acc_currencycode, acc_isretired, acc_xpath])
        
        # Créer un DataFrame à partir de la liste de lignes
        return pd.DataFrame(rows, columns=dfcols)

        
    def get_transactions(self):
        transactions = []  # List to store transaction details

        for account in self.root.findall("./accounts/account"): 
            account = self.check_for_ref_lx(account)
            account_uuid = account.find("uuid").text
            account_name = account.find("name").text  # Extract account name
            account_currencyCode = account.find("currencyCode").text

            for account_transaction in account.findall("transactions/account-transaction"): 
                account_transaction = self.check_for_ref_lx(account_transaction)
                account_transaction_uuid = account_transaction.find("uuid").text
                account_transaction_date = account_transaction.find("date").text
                account_transaction_currencyCode = account_transaction.find("currencyCode").text
                account_transaction_amount = float(account_transaction.find("amount").text) / 100
                account_transaction_shares = float(account_transaction.find("shares").text)
                account_transaction_type = account_transaction.find("type").text
                
                # Capture the fees if present
                account_transaction_fee = float(account_transaction.find('units/unit[@type="FEE"]/amount').attrib["amount"]) / 100 if account_transaction.find('units/unit[@type="FEE"]/amount') is not None else 0
                account_transaction_fee_iso = account_transaction.find('units/unit[@type="FEE"]/amount').attrib["currency"] if account_transaction.find('units/unit[@type="FEE"]/amount') is not None else ""

                account_transaction_security = self.check_for_ref_lx(account_transaction.find("security")).find("uuid").text if account_transaction.find("security") is not None else ""

                # Append account name to the transaction data
                transactions.append([
                    account_transaction_date,
                    account_transaction_type,
                    account_transaction_currencyCode,
                    account_transaction_amount,
                    account_transaction_fee,
                    account_transaction_fee_iso,
                    account_transaction_amount,
                    account_transaction_shares,
                    account_transaction_security,
                    account_transaction_uuid,
                    account_name  # Include account name here
                ])

                # Handle transactions from portfolios under cross entries
                for portfolio in account_transaction.findall("crossEntry/portfolio"):
                    portfolio = self.check_for_ref_lx(portfolio)
                    portfolio_uuid = portfolio.find("uuid").text

                    for portfolio_transaction in portfolio.findall("transactions/portfolio-transaction"):
                        portfolio_transaction = self.check_for_ref_lx(portfolio_transaction)
                        portfolio_transaction_uuid = portfolio_transaction.find("uuid").text
                        portfolio_transaction_date = portfolio_transaction.find("date").text
                        portfolio_transaction_currencyCode = portfolio_transaction.find("currencyCode").text
                        portfolio_transaction_amount = float(portfolio_transaction.find("amount").text) / 100
                        portfolio_transaction_shares = float(portfolio_transaction.find("shares").text) / 100000000
                        portfolio_transaction_type = portfolio_transaction.find("type").text

                        portfolio_transaction_fee = float(portfolio_transaction.find('units/unit[@type="FEE"]/amount').attrib["amount"]) / 100 if portfolio_transaction.find('units/unit[@type="FEE"]/amount') is not None else 0
                        portfolio_transaction_fee_iso = portfolio_transaction.find('units/unit[@type="FEE"]/amount').attrib["currency"] if portfolio_transaction.find('units/unit[@type="FEE"]/amount') is not None else ""

                        portfolio_transaction_security = self.check_for_ref_lx(portfolio_transaction.find("security")).find("uuid").text if portfolio_transaction.find("security") is not None else ""

                        # Append account name here as well
                        transactions.append([
                            portfolio_transaction_date,
                            portfolio_transaction_type,
                            portfolio_transaction_currencyCode,
                            portfolio_transaction_amount,
                            portfolio_transaction_fee,
                            portfolio_transaction_fee_iso,
                            portfolio_transaction_amount,
                            portfolio_transaction_shares,
                            portfolio_transaction_security,
                            portfolio_transaction_uuid,
                            account_name  # Include account name here too
                        ])

        # Create a DataFrame from the transaction list
        df_transactions = pd.DataFrame(transactions, columns=[
            'date', 'type', 'currencyCode', 'net_price', 'fees', 'fee_currency', 'amount', 'shares', 'security_uuid', 'transaction_uuid', 'account_name'
        ])

        df_transactions.dropna(how='all', inplace=True)
        df_transactions['date'] = pd.to_datetime(df_transactions['date'])
        # Filtrer les transactions où (type='BUY' OR type='SELL') AND shares=0
        df_transactions = df_transactions[~((df_transactions['type'].isin(['BUY', 'SELL'])) & (df_transactions['shares'] == 0))]
        # Sort by date
        df_transactions = df_transactions.sort_values(by='date', ascending=False)

        return df_transactions


# Onglet Bourse
with tabs[4]:
    st.title("Bourse")

    # Ajout d'un champ de téléchargement de fichier
    uploaded_xml = st.file_uploader("Importer un fichier Portfolio Performance Alex.xml", type="xml")
    #############################################################
    # Si un fichier est importé
    if uploaded_xml:
        # Chemin pour enregistrer le fichier
        file_path = os.path.join(BASE_DIR, 'data', 'Portfolio Performance Alex.xml')
        
        # Enregistrer le fichier téléchargé dans le dossier data
        with open(file_path, "wb") as f:
            f.write(uploaded_xml.getbuffer())
        st.success("Le fichier XML a été mis à jour avec succès.")
        
        # Actualiser l'instance PortfolioPerformanceFile avec le nouveau fichier
        PP = PortfolioPerformanceFile(filepath=file_path)
        
        # Actualiser les données affichées dans les onglets
        # Extraction des données mises à jour
        df_securities = PP.get_df_securities()
        df_accounts = PP.get_df_accounts()
        df_portfolios = PP.get_df_portfolios()
        df_transactions = PP.get_transactions()
        
        # Afficher les données mises à jour
        st.subheader("Securities DataFrame")
        st.dataframe(df_securities)

        st.subheader("Accounts DataFrame")
        st.dataframe(df_accounts)

        st.subheader("Portfolios DataFrame")
        st.dataframe(df_portfolios)

        st.subheader("Transactions DataFrame")
        st.dataframe(df_transactions)

    #############################################################
    # Configuration de l'application Streamlit
    st.title("Portfolio Performance Analysis")

    # Spécifiez le chemin du fichier XML
    file_path = r'data/Portfolio Performance Alex.xml'  # Remplacez par le chemin correct

    # Créer une instance de PortfolioPerformanceFile
    PP = PortfolioPerformanceFile(filepath=file_path)

    # Extraire les données
    st.subheader("Securities DataFrame")
    df_securities = PP.get_df_securities()
    st.dataframe(df_securities)

    st.subheader("Accounts DataFrame")
    df_accounts = PP.get_df_accounts()
    st.dataframe(df_accounts)

    st.subheader("Portfolios DataFrame")
    df_portfolios = PP.get_df_portfolios().sort_index(ascending=False)
    st.dataframe(df_portfolios)

    st.subheader("All Prices DataFrame")
    df_all_prices = PP.get_df_all_prices().sort_index(ascending=False)
    st.dataframe(df_all_prices)

    st.subheader("Transactions DataFrame")
    df_transactions = PP.get_transactions()

    # Create a mapping DataFrame from the Securities DataFrame
    securities_mapping = df_securities[['uuid', 'isin', 'name']].copy()
    securities_mapping.rename(columns={'uuid': 'security_uuid'}, inplace=True)

    # Merge the Transactions DataFrame with the Securities mapping
    df_transactions = df_transactions.merge(securities_mapping, how='left', on='security_uuid')
    st.dataframe(df_transactions)

    # Traitement des données pour créer un dataframe consolidé
    st.subheader("Résumé par ISIN (détail par date)")

    # Convertir les dates en format datetime
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])
    df_all_prices.index = pd.to_datetime(df_all_prices.index)

    # Créer un dataframe avec toutes les dates entre la plus ancienne transaction et aujourd'hui
    date_range = pd.date_range(start=df_transactions['date'].min(), end=pd.Timestamp.today(), freq='D')

    # Initialiser les colonnes du dataframe final : nombre de shares, valorisation, prix moyen, plus-value, performance, et cash
    consolidated_df = pd.DataFrame(index=date_range, columns=['Cash'])

    # Initialiser le dataframe des shares détenues pour chaque ISIN
    shares_held = pd.DataFrame(0, index=date_range, columns=df_all_prices.columns)

    # Mettre à jour les shares détenues en fonction des transactions (BUY, SELL)
    for idx, transaction in df_transactions.iterrows():
        isin = transaction['isin']
        if pd.notna(isin) and transaction['type'] in ['BUY', 'SELL']:
            change = float(transaction['shares']) if transaction['type'] == 'BUY' else -float(transaction['shares'])
            shares_held.loc[transaction['date']:, isin] = shares_held.loc[transaction['date']:, isin].astype(float) + change

    # Ajouter les shares détenues à chaque ISIN dans le dataframe consolidé
    for isin in shares_held.columns:
        consolidated_df[f'Shares Held {isin}'] = shares_held[isin].astype(float)  # Convertir en float

    # Calcul de la valorisation totale pour chaque ISIN à chaque date
    valorisation = shares_held * df_all_prices.reindex(date_range).ffill()

    # Assurez-vous que valorisation est de type float
    valorisation = valorisation.astype(float)

    # Ajouter la valorisation totale au dataframe consolidé
    consolidated_df = pd.concat([consolidated_df, valorisation], axis=1)

    # Calcul du prix de revient moyen
    cumulative_cost = pd.DataFrame(0.0, index=date_range, columns=df_all_prices.columns)
    total_shares = pd.DataFrame(0, index=date_range, columns=df_all_prices.columns)

    for idx, transaction in df_transactions.iterrows():
        isin = transaction['isin']
        if pd.notna(isin):
            if transaction['type'] == 'BUY':
                cumulative_cost.loc[transaction['date']:, isin] += (transaction['net_price'] + transaction['fees'])
                # Convertir en float avant l'addition
                total_shares.loc[transaction['date']:, isin] += float(transaction['shares'])
            elif transaction['type'] == 'SELL':
                cumulative_cost.loc[transaction['date']:, isin] -= (transaction['net_price'] + transaction['fees'])
                total_shares.loc[transaction['date']:, isin] -= float(transaction['shares'])
        
    # Prix moyen = montant total investi / nombre de shares
    average_cost = cumulative_cost / total_shares.replace(0, np.nan)

    # S'assurer que average_cost est de type float
    average_cost = average_cost.astype(float).fillna(0).infer_objects()  # Remplir les NaN et inférer les objets
    
    # Calcul de la plus-value
    plus_value = valorisation - cumulative_cost

    # Calcul de la plus-value
    plus_value = valorisation - cumulative_cost

    # Correction de la performance lors de la fermeture de position :
    performance_abs = pd.DataFrame(0.0, index=date_range, columns=df_all_prices.columns)
    for isin in df_all_prices.columns:
        for date in date_range:
            if total_shares.loc[date, isin] == 0:  # Si toutes les actions sont vendues
                if date > df_transactions['date'].min():  # On ne modifie que si on est après la première transaction
                    performance_abs.loc[date, isin] = performance_abs.loc[date - pd.Timedelta(days=1), isin]
            else:
                cumulative_cost_value = cumulative_cost.loc[date, isin]
                if cumulative_cost_value > 0:  # Pour éviter la division par zéro
                    performance_abs.loc[date, isin] = (plus_value.loc[date, isin] / cumulative_cost_value) * 100
                else:
                    performance_abs.loc[date, isin] = 0  # Ou toute autre valeur que vous souhaitez utiliser

    # Convertir la colonne de date des transactions
    df_transactions['date'] = pd.to_datetime(df_transactions['date'])

    # S'assurer que cash_account a un index qui couvre toutes les dates de transactions
    all_dates = pd.date_range(start=df_transactions['date'].min(), end=pd.Timestamp.today(), freq='D')
    cash_account = pd.Series(0, index=all_dates)

    # Gestion du cash en prenant en compte les transactions
    for idx, row in df_transactions.iterrows():
        transaction_date = row['date']
        if transaction_date in cash_account.index:
            if row['type'] == 'DEPOSIT':
                cash_account[transaction_date] += row['net_price']
            elif row['type'] == 'REMOVAL':
                cash_account[transaction_date] -= row['net_price']
            elif row['type'] == 'TAXES':
                cash_account[transaction_date] -= row['net_price']
            elif row['type'] == 'FEES_REFUND':
                cash_account[transaction_date] += row['net_price']
            elif row['type'] == 'BUY':
                cash_account[transaction_date] -= row['net_price']
            elif row['type'] == 'SELL':
                cash_account[transaction_date] += row['net_price']
        #else:
        #    st.warning(f"Transaction date {transaction_date} not found in cash_account index.")


    # Calculer le solde cumulatif de cash
    cash_account = cash_account.cumsum()

    # S'assurer que cash_account est de type float
    cash_account = cash_account.astype(float)

    # Ajouter le cash au dataframe consolidé
    consolidated_df['Cash'] = cash_account.astype(float)

    # Ajouter les coûts moyens, plus-values, performances et shares détenues pour chaque ISIN séparément
    for isin in average_cost.columns:
        consolidated_df[f'Average Cost {isin}'] = average_cost[isin].astype(float)  # Forcer float
        consolidated_df[f'Plus-Value {isin}'] = plus_value[isin].astype(float)  # Forcer float
        consolidated_df[f'Performance (%) {isin}'] = performance_abs[isin].astype(float)  # Forcer float

    # S'assurer que les noms de colonnes sont tous des chaînes
    consolidated_df.columns = [str(col) for col in consolidated_df.columns]

    # Afficher le résumé par ISIN et par date
    df_summary_isin = pd.DataFrame(index=date_range)

    # Ajouter les colonnes pour chaque KPI par ISIN
    for isin in average_cost.columns:
        df_summary_isin[f'Valorisation {isin}'] = valorisation[isin]
        df_summary_isin[f'Shares Held {isin}'] = shares_held[isin]
        df_summary_isin[f'Plus-Value {isin}'] = plus_value[isin]
        df_summary_isin[f'Performance (%) {isin}'] = performance_abs[isin]

    # S'assurer que les noms de colonnes sont tous des chaînes
    df_summary_isin.columns = [str(col) for col in df_summary_isin.columns]

    # Trier par index (dates) de manière décroissante
    df_summary_isin = df_summary_isin.sort_index(ascending=False)

    # Afficher le résumé par ISIN et par date
    st.dataframe(df_summary_isin)

    # Step 1: Extraire les colonnes de valorisation par ISIN à partir de df_summary_isin
    # Filtrer uniquement les colonnes de valorisation
    valorisation_columns = [col for col in df_summary_isin.columns if col.startswith('Valorisation ')]
    # Step 2: Restructurer les données pour les regrouper par `account_name`
    # Créer un dataframe pour stocker les valorisations agrégées
    df_aggregate = pd.DataFrame(index=df_summary_isin.index)
    # Associer chaque ISIN à un account_name
    isin_account_mapping = df_transactions[['isin', 'account_name']].drop_duplicates()
    # Rassembler les valorisations en fonction de `account_name`
    for account_name in isin_account_mapping['account_name'].unique():
        # Obtenir les ISIN associés à cet `account_name`
        isins_for_account = isin_account_mapping[isin_account_mapping['account_name'] == account_name]['isin']
        # Sélectionner les colonnes de valorisation pour ces ISIN
        valorisation_cols_for_account = [f'Valorisation {isin}' for isin in isins_for_account if f'Valorisation {isin}' in df_summary_isin.columns]
        # Additionner les valorisations de tous les ISIN pour cet `account_name`
        df_aggregate[account_name] = df_summary_isin[valorisation_cols_for_account].sum(axis=1)
    # Step 3: S'assurer que toutes les dates du `date_range` sont incluses
    # Étendre l'index de `df_aggregate` pour inclure toutes les dates du calendrier
    df_aggregate = df_aggregate.reindex(date_range).fillna(0).infer_objects()
    df_aggregate = df_aggregate.sort_index(ascending=False)
    st.subheader("Valorisation Totale par Account Name et par Date")
    st.dataframe(df_aggregate, use_container_width=True)
    




# Onglet Graphique
with tabs[2]:
    st.title("Évolution des Soldes")

    soldes_truncated[soldes_truncated < 0] = 0
    # Combiner les soldes des comptes bancaires avec les valorisations par account_name
    consolidated_data = pd.concat([soldes_truncated, df_aggregate], axis=1).fillna(0).infer_objects()


    # Graphique en aires empilées pour l'évolution des soldes et valorisations
    fig = go.Figure()

    for compte in consolidated_data.columns:
        fig.add_trace(go.Scatter(
            x=consolidated_data.index,
            y=consolidated_data[compte],
            mode='lines',
            name=compte,
            stackgroup='one',
            fill='tonexty',
            line=dict(width=2)
        ))

#    for compte in consolidated_data.columns:
#        last_value = consolidated_data[compte].iloc[-1]
#        fig.add_annotation(
#            x=consolidated_data.index[-1],
#            y=last_value,
#            text=f"{last_value:.2f}",
#            showarrow=True,
#            arrowhead=2,
#            ax=0,
#            ay=-40,
#            font=dict(color='black', size=12),
#            bgcolor='white',
#            bordercolor='black',
#            borderwidth=1,
#            borderpad=4,
#        )

    fig.update_layout(
        title="Évolution des Soldes par Compte et Valorisation",
        xaxis_title="Date",
        yaxis_title="Solde",
        legend_title="Comptes et Valorisation",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig)

    # Création du graphique empilé à 100% pour la répartition relative
    fig_percent = go.Figure()

    # Calculer les pourcentages de chaque colonne pour chaque date
    consolidated_data_percent = consolidated_data.div(consolidated_data.sum(axis=1), axis=0)

    for compte in consolidated_data_percent.columns:
        fig_percent.add_trace(go.Scatter(
            x=consolidated_data_percent.index,
            y=consolidated_data_percent[compte],
            mode='lines',
            name=compte,
            stackgroup='one',
            fill='tonexty',
            line=dict(width=2)
        ))

    fig_percent.update_layout(
        title="Répartition des Soldes et Valorisation (Empilé à 100%)",
        xaxis_title="Date",
        yaxis_title="Proportion",
        legend_title="Comptes et Valorisation",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig_percent)





    # Onglet Trading
    with tabs[5]:
        st.title("Évolution des Valorisations et Performances")

        # Sélecteur pour choisir entre Performance et Valorisation
        graph_type = st.selectbox("Choisissez le type de graphique :", ["Valorisation", "Performance"])

        # Créer une figure Plotly
        fig = go.Figure()

        if graph_type == "Valorisation":

            # Ajouter des traces pour chaque ISIN
            for isin in valorisation.columns:
                fig.add_trace(go.Scatter(
                    x=valorisation.index,
                    y=valorisation[isin],
                    mode='lines',
                    name=isin,
                    stackgroup='one',  # Empilement des valeurs
                    fill='tonexty',    # Remplissage vers le bas
                    line=dict(width=2)
                ))

            # Initialiser un compteur pour le décalage des annotations
            annotation_counter = 0

            # Ajouter des annotations pour la dernière valeur de chaque ISIN
            for isin in valorisation.columns:
                last_value = valorisation[isin].iloc[-1]  # Valeur de valorisation à la dernière date
                last_date = valorisation.index[-1]  # Dernière date

                # Récupérer les colonnes précédentes en évitant les NaN
                previous_columns = valorisation.columns[:valorisation.columns.get_loc(isin)]
                previous_values = valorisation[previous_columns]

                # Filtrer les NaN et calculer la somme des valorisations des ISIN précédents
                cumulative_value = previous_values.iloc[-1].dropna().sum() + last_value

                # Calculer le décalage basé sur le compteur
                ax_offset = 10 + (annotation_counter % 3) * 40  # Décalage de 40, 80, 120

                fig.add_annotation(
                    x=last_date + pd.Timedelta(days=ax_offset),  # Décalage horizontal vers la droite
                    y=cumulative_value,  # Positionner l'annotation à la hauteur de la courbe cumulée
                    text=f"{last_value:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=ax_offset,  # Appliquer le décalage calculé
                    ay=0,  # Ajuster la position verticale de l'annotation
                    font=dict(color='black', size=12),
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1,
                    borderpad=4,
                )

                # Incrémenter le compteur pour la prochaine annotation
                annotation_counter += 1

            # Mise à jour de la mise en page pour Valorisation
            fig.update_layout(
                title="Évolution des Valorisations par ISIN",
                xaxis_title="Date",
                yaxis_title="Valorisation",
                legend_title="ISIN",
                template="plotly_white",
                height=500
            )


        elif graph_type == "Performance":

            # Ajouter des traces pour chaque ISIN
            for isin in performance_abs.columns:
                fig.add_trace(go.Scatter(
                    x=performance_abs.index,
                    y=performance_abs[isin],
                    mode='lines',
                    name=isin,
                    line=dict(width=2)
                ))

            # Ajouter des annotations pour la dernière valeur de chaque ISIN
            for isin in performance_abs.columns:
                last_value = performance_abs[isin].iloc[-1]
                fig.add_annotation(
                    x=performance_abs.index[-1],
                    y=last_value,
                    text=f"{last_value:.2f}%",
                    showarrow=True,
                    arrowhead=2,
                    ax=40,
                    ay=0,
                    font=dict(color='black', size=12),
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1,
                    borderpad=4,
                )

            # Mise à jour de la mise en page pour Performance
            fig.update_layout(
                title="Évolution des Performances par ISIN",
                xaxis_title="Date",
                yaxis_title="Performance (%)",
                legend_title="ISIN",
                template="plotly_white",
                height=500
            )

        # Afficher le graphique
        st.plotly_chart(fig)
