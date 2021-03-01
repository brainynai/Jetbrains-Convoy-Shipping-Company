import pandas as pd
import sqlite3
import json



def csvFromXl(excelName):
    csvName = excelName[:excelName.rfind('.')] + '.csv'

    my_df = pd.read_excel(excelName, sheet_name='Vehicles')

    my_df.to_csv(csvName, index=None)

    numRows = my_df.shape[0]

    lineOrLines = 'line was' if numRows == 1 else 'lines were'

    print(f'{numRows} {lineOrLines} imported to {csvName}')

    return csvName


def correctCsv(csvName):
    df = pd.read_csv(csvName)

    clean_df = df.replace(r'[^0-9]', '', regex=True)

    numDiffs = sum(clean_df[col].compare(df[col]).shape[0] for col in clean_df)  # Hax

    checkedName = csvName[:csvName.rfind('.')] + '[CHECKED].csv'
    clean_df.to_csv(checkedName, index=None)

    cellOrCells = 'cell was' if numDiffs == 1 else 'cells were'
    print(f'{numDiffs} {cellOrCells} corrected in {checkedName}')

    return checkedName


def initDB(dbName):
    conn = sqlite3.connect(dbName)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS convoy')  # Test will probably break otherwise
    conn.commit()

    cur.execute('''create table convoy (
    vehicle_id INTEGER not null primary key, 
    engine_capacity INTEGER not null, 
    fuel_consumption INTEGER not null, 
    maximum_load integer not null)''')

    conn.commit()

    return conn, cur


def dbToJson(conn, cur, dbName):
    allRows = cur.execute("SELECT * FROM convoy").fetchall()
    rowDict = [dict(row) for row in allRows if row['score'] > 3]
    numRowsToJson = len(rowDict)
    jsonDict = {"convoy": rowDict}
    #print(jsonDict)

    for i in range(len(rowDict)):
        rowDict[i].pop('score', None)

    jsonName = dbName[:dbName.rfind('.')] + '.json'

    with open(jsonName, 'w') as outFile:
        json.dump(jsonDict, outFile)

    carOrCars = 'vehicle was' if numRowsToJson == 1 else 'vehicles were'
    print(f'{numRowsToJson} {carOrCars} saved into {jsonName}')


def dbToXml(conn, cur, dbName):
    allRows = cur.execute("SELECT * FROM convoy").fetchall()
    rowDict = [dict(row) for row in allRows if row['score'] <= 3]
    numRowsToXml = len(rowDict)
    xmlName = dbName[:dbName.rfind('.')] + '.xml'

    with open(xmlName, 'w') as f:
        f.write('<convoy>')
        for row in rowDict:  # This is not the best way of doing this, but meh
            f.write('<vehicle>')
            f.write('<vehicle_id>')
            f.write(str(row['vehicle_id']))
            f.write('</vehicle_id>')
            f.write('<engine_capacity>')
            f.write(str(row['engine_capacity']))
            f.write('</engine_capacity>')
            f.write('<fuel_consumption>')
            f.write(str(row['fuel_consumption']))
            f.write('</fuel_consumption>')
            f.write('<maximum_load>')
            f.write(str(row['maximum_load']))
            f.write('</maximum_load>')
            f.write('</vehicle>')
        f.write('</convoy>')

    carOrCars = 'vehicle was' if numRowsToXml == 1 else 'vehicles were'
    print(f'{numRowsToXml} {carOrCars} saved into {xmlName}')


def scoreVehicles(conn, cur):
    dbRow = cur.execute('select * from convoy').fetchall()[0]
    if 'score' not in dbRow.keys():
        cur.execute('alter table convoy add column score integer not null default 0')
        conn.commit()

    allRows = cur.execute('select * from convoy').fetchall()
    for row in allRows:
        score = calcScore(row['engine_capacity'], row['fuel_consumption'], row['maximum_load'])
        cur.execute('update convoy set score = ? where vehicle_id = ?', (score, row['vehicle_id']))

    conn.commit()


def calcScore(engCap, fuelCon, maxLoad):
    points = 0
    routeLength = 450
    fuelNeeded = 450/100 * fuelCon
    stops = fuelNeeded//engCap
    if stops == 0:
        points += 2
    elif stops == 1:
        points += 1

    if fuelNeeded <= 230:
        points += 2
    else:
        points += 1

    if maxLoad >= 20:
        points += 2

    return points


inputName = input('Input file name\n')

extension = inputName[inputName.rfind('.'):]

if not extension == '.s3db':
    if extension == '.xlsx':
        csvName = csvFromXl(inputName)
    else:
        csvName = inputName

    if not csvName.endswith('[CHECKED].csv'):
        csvName = correctCsv(csvName)

    dataDF = pd.read_csv(csvName)

    dbName = csvName[:csvName.rfind('[')] + '.s3db'
    conn, cur = initDB(dbName)

    numOldRows = cur.execute('select count(*) from convoy').fetchone()[0]
    dataDF.to_sql('convoy', con=conn, if_exists='append', index=False)
    conn.commit()
    cur.execute('select count(*) from convoy')
    numNewRows = cur.fetchone()[0] - numOldRows

    recOrRecs = 'record was' if numNewRows == 1 else 'records were'
    print(f'{numNewRows} {recOrRecs} inserted into {dbName}')
else:
    dbName = inputName

    conn = sqlite3.connect(dbName)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

scoreVehicles(conn, cur)
dbToJson(conn, cur, dbName)
dbToXml(conn, cur, dbName)

conn.commit()
conn.close()

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
