# 💰⚡️ up2ynab

A command-line interface for integrating the Australian neobank [Up](https://up.com.au) with
the budgeting platform [You Need A Budget](https://www.youneedabudget.com).

For now it is capable of importing transactions from Up into YNAB. Future plans include the ability to synchronise the balances of Up Savers with YNAB categories.

Any other feature you'd find useful? [Create an issue](https://github.com/lachholden/up2ynab/issues/new)!

![demo of up2ynab transactions](https://github.com/lachholden/up2ynab/blob/master/docs/transactions-demo.gif?raw=true)

## 💽 Installation
First, make sure you have Python 3 installed. Then, install this tool from PyPI:
```shell
$ pip install up2ynab
```

If you get a SSLError when you try to use the program, you might need to also run
```shell
$ pip install certifi
```
but this *should* be done automatically as part of the above command.

## 🛠 Configuration
You'll need your API tokens for both Up and YNAB for this program to work.

Although you can use the command-line flags `--up-api-token` and `--ynab-api-token` to pass your tokens to each command (see `up2ynab --help` for info), the recommended way to use this CLI is to configure it via environment variables – this goes for some other configuration options also.

1. Get your Up API token [here](https://api.up.com.au/getting_started)

2. Get your YNAB API token [here](https://app.youneedabudget.com/settings/developer)

3. Add the following configuration to your `~/.bash_profile`, `~/.zshenv`, or similar, changing the values to ones appropriate to you – or configure your system environment variables as follows:
```bash
# Your API tokens
export UP_API_TOKEN=up:yeah:xxxxxxxx
export YNAB_API_TOKEN=xxxxxxxx

# The name of your Up transactional account in YNAB
# The default is "Up Spending" – if this is what yours is called, remove the following line:
export YNAB_ACCOUNT_NAME="Up Transactional"

# The coloured flag in YNAB you wish to apply to transactions in a foreign currency
# If you don't wish to apply any, remove the following line:
export YNAB_FOREIGN_TRANSACTION_FLAG=yellow
```

**Note:** It is *CRITICAL* that you do not make your API keys publicly available. If you version control your config files, consider exporting your tokens in a separate file (e.g. `~/.up2ynab`) ignored by version control that you source as part of your shell configuration.

4. Restart your shell and run `up2ynab check` to confirm that your API tokens are set up properly.

## 💸 Usage
All of the information required to use this tool can be found in the tool's help pages, i.e.
```shell
$ up2ynab --help
$ up2ynab check --help
$ up2ynab transactions --help
```
What follows is a summary of key tasks.

### Importing Transactions
To import your transactions, run the command:
```shell
$ up2ynab transactions
```
By default it will upload all transactions from the past 14 days, but this can be configured via the `--days/-d` option. For example, to instead search for transactions within the last month:
```shell
$ up2ynab transactions -d 30
```
YNAB (and this CLI) is smart about duplicate imports, so you can safely run `up2ynab transactions` as many times as you wish and only new transactions (as determined by their internal ID from Up) will appear. Note that this does *not* detect duplicates from file-based uploading, so if you were using that prior to using this tool, you might want to limit the number of days of transactions to import for the next two weeks.
