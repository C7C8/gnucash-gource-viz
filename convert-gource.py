from datetime import datetime
from io import StringIO
import csv
import json
import math
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

	# Generate account tree
	curr = accounts
	for acct in line["acct"].split("."):
		if acct not in curr.keys():
			curr[acct] = {}
			curr = curr[acct]
		else:
			curr = curr[acct]
	if "val" not in curr.keys():
		curr["val"] = line["amnt"]
	else:
		curr["val"] += line["amnt"]

	transactions.append(line)


def recurse_write(account, prefix, file):
	"""Recursively write out an account tree to file, without history included"""
	for acct_name in account.keys():
		if acct_name == "val":
			# Print out value of account in the form of "files"
			base_str = "{timestamp}|User|A|{path}".format(timestamp=int(datetime.now().timestamp()), path=prefix)
			for i in range(math.ceil(abs(account["val"]) / 100)):
				file.write("{path}/{amnt}.{mtype}\n".format(path=base_str, amnt=(i + 1) * 100,
															mtype="asset" if account["val"] > 0 else "debt"))
		else:
			recurse_write(account[acct_name], prefix + "/" + acct_name, file)


# Primitive conversion into Gource viz; does not take history into acccount
with open("output.log", "w") as log:
	recurse_write(accounts, "", log)
