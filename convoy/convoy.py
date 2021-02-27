import pandas as pd


def csvFromXl(excelName):
    csvName = excelName[:excelName.rfind('.')] + '.csv'

    my_df = pd.read_excel(excelName, sheet_name='Vehicles')

    my_df.to_csv(csvName, index=None)

    numRows = my_df.shape[0]

    lineOrLines = 'line was' if numRows == 1 else 'lines were'

    print(f'{numRows} {lineOrLines} imported to {csvName}')

    return csvName, my_df


inputName = input('Input file name\n')

extension = inputName[inputName.rfind('.'):]

if extension == '.xlsx':
    csvName, df = csvFromXl(inputName)
else:
    csvName = inputName
    df = pd.read_csv(csvName)

clean_df = df.replace(r'[^0-9]', '', regex=True)

numDiffs = sum(clean_df[col].compare(df[col]).shape[0] for col in clean_df)  # Hax

checkedName = csvName[:csvName.rfind('.')] + '[CHECKED].csv'
clean_df.to_csv(checkedName, index=None)

cellOrCells = 'cell was' if numDiffs == 1 else 'cells were'
print(f'{numDiffs} {cellOrCells} corrected in {checkedName}')


#   vehicle_id engine_capacity fuel_consumption maximum_load
# 0          2             200    fuel cons. 25      tons 14
# 1          4            220l               55           22
# 2        n.8             280  liter per km 69       16 ton
# 3         16             100              34l           24

#   vehicle_id engine_capacity fuel_consumption maximum_load
# 0          2             200               25           14
# 1          4             220               55           22
# 2          8             280               69           16
# 3         16             100               34           24
