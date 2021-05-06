Fetch AWS MFA accounts and security keys from [Chrome](https://www.google.com/chrome/) using [Selenium for Python](https://selenium-python.readthedocs.io/).

## Prerequisites

In order to build **mfakeys** you need to have
[Python 3.6.*](https://www.python.org/downloads/release/python-360/),
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

### Print AWS accounts (no account privided)
<pre>
$ dist/mfakeys -U USERNAME -P PASSWORD -C CODE --url URL
</pre>

### Print AWS account's profiles (no profile privided)
<pre>
$ dist/mfakeys -U USERNAME -P PASSWORD -C CODE -a ACCOUNT --url URL
</pre>

### Print AWS keys for an account and its profile
<pre>
$ dist/mfakeys -U USERNAME -P PASSWORD -C CODE -a ACCOUNT -p PROFILE --url URL
</pre>

### Use AWS keys for an account and its profile
<pre>
$ $(dist/mfakeys -U USERNAME -P PASSWORD -C CODE -a ACCOUNT -p PROFILE --url URL)
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
$ dist/mfakeys -a ACCOUNT -p PROFILE
</pre>

### Debugging

#### Print debug info
<pre>
$ DEBUG=1 dist/mfakeys -a ACCOUNT -p PROFILE
</pre>

#### Print debug info and show browser
<pre>
$ DEBUG=2 dist/mfakeys -a ACCOUNT -p PROFILE
</pre>

#### Print debug info, show browser and run under [pdb](https://docs.python.org/3/library/pdb.html)
<pre>
$ DEBUG=3 dist/mfakeys -a ACCOUNT -p PROFILE
(Pdb) break 130
(Pdb) continue
</pre>
