# ShodanGen.py
Shodan Free Account Generator Script

![](https://raw.githubusercontent.com/Jansky1997/ShodanGen.py/main/images/ShodanGen.png)

## Use case

Shodan accounts with the free plan are limited to a certain number of queries in a specific timespan.
This script helps you to generate free accounts in order to do more queries without subscribing.

## Information

Keep in mind, that too many requests or some VPNs may trigger Cloudflare DDoS protection which leads errors in account creation.
ShodanGen.py will inform you about that in the terminal output. **ERROR: Account 5: Failed to activate**

ShodanGen.py uses the API of temp-mail.io to create e-mail adresses and automatically activate the accounts.

## Features

** Multithreaded account creation **
** Color encoded output **
** Logging component **

## Parameters

**-o (Output)**  

Define the file to redirect the output to e.g. shodan.txt

**-t (Threads)**  

Number of threads working simultaneous

**-m (Max Retries)**  

Number of retries to activate the account

**Number of Accounts to create**  

Number of Shodan accounts to create
