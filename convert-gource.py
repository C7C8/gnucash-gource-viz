from datetime import datetime
from io import StringIO
import csv
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
			curr[acct] = {"val": 0}
			curr = curr[acct]
		else:
			curr = curr[acct]

	transactions.append(line)

transactions = sorted(transactions, key=lambda x: x["date"])

# Convert entire account history to Gource history
with open("output.log", "w") as log:
	for transaction in transactions:
		# Parse account path and navigate to the right account in the tree
		path = transaction["acct"].replace(".", "/")
		account = accounts
		for acct in transaction["acct"].split("."):
			account = account[acct]

		# Commit the transaction, then figure out how many "files" we need to add or remove
		old_filecount = math.ceil(abs(account["val"]) / 100)
		old_amnt = account["val"]
		account["val"] += transaction["amnt"]
		new_filecount = math.ceil(abs(account["val"]) / 100)

		base_str = "{timestamp}|User|{operation}|/{path}/{amnt}.{mtype}\n"
		tmp = range(old_filecount, new_filecount, 1 if old_filecount < new_filecount else -1)

		print("{path:<40}: {cnt1} ({amnt1:.2f}) -> {cnt2} ({amnt2:.2f}), ({rstart}, {rend})".format(
			path=path,
			cnt1=old_filecount,
			amnt1=old_amnt,
			cnt2=new_filecount,
			amnt2=account["val"],
			rstart=tmp.start,
			rend=tmp.stop))

		for i in tmp:
			log.write(base_str.format(
				timestamp=transaction["date"],
				operation="A" if new_filecount > old_filecount else "D",
				path=path,
				amnt=(i+1)*100,
				mtype="asset" if account["val"] > 0 else "debt"))


