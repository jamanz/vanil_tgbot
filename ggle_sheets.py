import pygsheets
import pandas as pd
#authorization

gc = pygsheets.authorize(service_file='sheets_k1.json')

if __name__ == '__main__':

    # Create empty dataframe
    df = pd.DataFrame()
    # Create a column
    df['name'] = ['John', 'Steve', 'Sarah']
    df['count'] = [1, 2, None   ]
    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('agroTable')
    # sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1D6D-jEE5cBvrPABljLZla5d1NtjOhmCR76ymPgNN3r0/')
    #select the first sheet
    wks = sh[0]

    #update the first sheet with df, starting at cell B2.
    wks.set_dataframe(df,(1,1))