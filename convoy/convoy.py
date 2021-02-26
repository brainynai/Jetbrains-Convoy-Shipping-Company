import pandas as pd

excelName = input('Input file name\n')  # don't know if newline is allowed
csvName = excelName[:excelName.rfind('.')] + '.csv'

my_df = pd.read_excel(excelName, sheet_name='Vehicles')

my_df.to_csv(csvName, index=None)

numRows = my_df.shape[0]

lineOrLines = 'line was' if numRows == 1 else 'lines were'

print(f'{numRows} {lineOrLines} imported to {csvName}')
