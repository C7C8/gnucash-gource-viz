from datetime import datetime
from io import StringIO
import csv
import json
import sys

if len(sys.argv) != 2:
	print("Need to provide transactions file to operate on!", file=sys.stderr)
	exit(1)

print("Loading transactions from {}".format(sys.argv[1]))
reader = StringIO("")
try:
	with open(sys.argv[1], newline="") as file:
		file_r = file.read()

		# Replace headers to make processing by dictreader easier
		replacements = {
			"Date": "date",
			"Account Name": "acct",
			"Number": "num",
			"Description": "desc",
			"Full Category Path": "path",
			"Reconcile": "recon",
			"Amount With Sym": "amnt_s",
			"Amount Num.": "amnt",
			"Rate/Price": "rate"
		}
		for key, value in replacements.items():
			file_r = file_r.replace(key, value)

		reader = StringIO(file_r)

except FileNotFoundError:
	print("Could not load file {}".format(sys.argv[1]), file=sys.stderr)
	exit(1)

transactions_reader = csv.DictReader(reader)
transactions = []

# Pre-processing
accounts = {}
for line in transactions_reader:
	# Remove unneeded keys
	line.pop('desc')
	line.pop('num')
	line.pop('recon')
	line.pop('amnt_s')
	line.pop('rate')

	# Convert date into timestamp, amount into float
	line["date"] = int(datetime.strptime(line["date"], "%m/%d/%Y").timestamp())
	line["amnt"] = float(line["amnt"].replace(",", ""))

	# Process accounts
	curr = accounts
	for acct in line["acct"].split("."):
		if acct not in curr.keys():
			curr[acct] = {"val": 0.0}
			curr = curr[acct]
		else:
			curr = curr[acct]
	curr["val"] += line["amnt"]

	print(line)
	transactions.append(line)
