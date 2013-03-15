import sys
import os
import traceback
import MySQLdb
sys.path.append("..")
import settings

schemaUpgradesDir = 'schemaUpgrades'

def getLegacySchemaVersion():
	cursor = db.cursor()
	cursor.execute("show columns in skills like 'handle'")
	results = cursor.fetchall()
	cursor.close()
	if len( results ) == 0:
		return (0, 0, 0)
	return (1, 0, 0)

def getSchemaVersion():
	cursor = db.cursor()
	cursor.execute("show tables like 'schema_version'")
	results = cursor.fetchall()
	if len( results ) == 0:
		cursor.close()
		return getLegacySchemaVersion()
	cursor.execute( "select major, middle, minor from schema_version" )
	result = cursor.fetchone()
	cursor.close()
	if result is None:
		return getLegacySchemaVersion()
	return result

def isScript( s ):
	return s.endswith( ".sql" ) and os.path.isfile( s )

def getScripts( upgradeDir ):
	fullUpgradePath = os.path.join( schemaUpgradesDir, upgradeDir )
	files = os.listdir( fullUpgradePath )
	scripts = filter( lambda f: isScript( os.path.join( fullUpgradePath, f ) ), files )
	return sorted( scripts )

def runScript( upgradeDir, script ):
	fullPath = os.path.join( schemaUpgradesDir, upgradeDir, script )
	scriptFile = open( fullPath )
	scriptText = scriptFile.read()
	scriptFile.close()
	cursor = db.cursor()
	cursor.execute( scriptText )
	cursor.close()

def parseVersion( name ):
	numbers = name.split('.')
	if len( numbers ) != 3 or not any(n.isdigit() for n in numbers):
		return None
	return (int(numbers[0]), int(numbers[1]), int(numbers[2]))

def getAvailableSchemaUpgrades():
	dirs = os.listdir( schemaUpgradesDir )
	versions = dict();
	for dir in dirs:
		parsedVersion = parseVersion( dir )
		if parsedVersion is not None:
			versions[parsedVersion] = dir
	return versions

def compareVersions( x, y ):
	for i in (0, 1, 2):
		diff = x[i] - y[i]
		if diff != 0:
			return diff
	return 0

db = MySQLdb.connect(host="localhost", user=settings.DATABASE_USER, db=settings.DATABASE_NAME, passwd=settings.DATABASE_PASSWORD)
(major, middle, minor) = getSchemaVersion();
print str.format( "Current db version: {0}.{1}.{2}", major, middle, minor )

print "Reading available upgrades..."
versions = getAvailableSchemaUpgrades()
sortedVersionKeys = sorted( versions.keys(), cmp = lambda x, y: compareVersions( x, y ) )
for version in sortedVersionKeys :
	print str.format( "\t{0}.{1}.{2}", version[0], version[1], version[2] )
if major == 0 and middle == 0 and minor == 0:
	currentIndex = -1
else:
	currentIndex = sortedVersionKeys.index( (major, middle, minor) )
if currentIndex == len( sortedVersionKeys ) - 1:
	print "Your schema is up to date!"
else:
	print "These upgrades will be executed: "
	for upgradeVersion in sortedVersionKeys[currentIndex+1:]:
		print str.format( "\t{0}.{1}.{2}", upgradeVersion[0], upgradeVersion[1], upgradeVersion[2] )

	print "Executing..."
	for upgradeVersion in sortedVersionKeys[currentIndex+1:]:
		print str.format( "\t{0}.{1}.{2}", upgradeVersion[0], upgradeVersion[1], upgradeVersion[2] )
		try:
			for script in getScripts( versions[upgradeVersion] ):
				print str.format( "\tRunning script: {0}", script )
				runScript( versions[upgradeVersion], script )
				print "\tDone"
			db.commit()
		except:
			db.rollback()
			print "A script failed. Rolling back changes."
			traceback.print_exc()
			break

	print "Schema upgrade complete!"