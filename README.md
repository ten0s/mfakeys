Fetch AWS MFA accounts and security keys from [Chrome](https://www.google.com/chrome/) using [Selenium for Python](https://selenium-python.readthedocs.io/).

## Prerequisites

In order to build **mfakeys** you need to have [Python 3.6.*](https://www.python.org/downloads/release/python-360/),
[Virtualenv](https://virtualenv.pypa.io/en/latest/) and
[GNU Make](http://www.gnu.org/software/make/) installed.

## Build
Creates standalone executable without any dependencies

<pre>
$ git clone https://github.com/ten0s/mfakeys.git
$ cd mfakeys
$ make
</pre>

## Usage

### General help
<pre>
$ dist/mfakeys -h
</pre>

### Print all AWS accounts (no account privided)
<pre>
$ dist/mfakeys -u USERNAME -p PASSWORD -c CODE --url URL
</pre>

### Print AWS keys for an account
<pre>
$ dist/mfakeys -u USERNAME -p PASSWORD -c CODE -a ACCOUNT --url URL
</pre>

### Use AWS keys for an account
<pre>
$ $(dist/mfakeys -u USERNAME -p PASSWORD -c CODE -a ACCOUNT --url URL)
$ aws ec2 describe-instances
</pre>

### Resource file
<pre>
$ cat ~/.mfakeysrc
[default]
username=USERNAME
password=PASSWORD
code=CODE | PATH_TO_SCRIPT
url=URL
$ dist/mfakeys -c CODE -a ACCOUNT
</pre>

### Debugging

#### Print debug info
<pre>
$ DEBUG=1 dist/mfakeys -c CODE -a ACCOUNT
</pre>

#### Print debug info and show browser
<pre>
$ DEBUG=2 dist/mfakeys -c CODE -a ACCOUNT
</pre>

#### Print debug info, show browser and run under [pdb](https://docs.python.org/2/library/pdb.html)
<pre>
$ DEBUG=3 dist/mfakeys -c CODE -a ACCOUNT
(Pdb) break 149
(Pdb) continue
</pre>
