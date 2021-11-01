# Amazon Orders Parser

### Documentation out of date

Below documentation gives a basic understanding of program's purpose, but it does not reflect current code functionality. Added sales channel etsy, looking onwards: calculate order package weight, select *cheapest* shipping company, etc.

Note added: **2021.11**

Below documentation last updated: **2020.06**

## Description

Amazon seller oriented project. Client uses 3 different shipment companies, that require different formats to be uploaded into their systems. 

Application takes source file, parses it, filters out processed orders and outputs ready to go files.

Screenhot:

![GUI screenshot](https://user-images.githubusercontent.com/45366313/83858313-fb008d00-a724-11ea-8ffd-e08963356608.JPG)

## How it works

Workbook is applications' GUI entry point.
When user picks an export text file, compiled version of python program `main_amazon.py` (`main_amazon.exe`) is launched.

Any run-time warnings or errors are displayed in workbook. (See code for VBA: [ParseAmazonOrders.bas](VBA/ParseAmazonOrders.bas))

### Features

- sqlite database collects source files and orders for new vs old older filtering and potential debugging;
- database self-cleans records on trailing 14 days basis;
- logs, backups database
- prepares xlsx, csv outputs;
- prepares a text report orders made by same person (potential to merge shipment package)

## Compile

To compile one file executable with added icon: 
- create virtual environment
- install [requirements ](##Requirements)
- navigate to Helper Files dir (Windows: `cd "Helper Files"`)
- run in cmd:

`pyinstaller -w -F -i Python.ico main_amazon.py`

## Requirements

Python > 3.7

Most of requirements in [requirements.txt](requirements.txt) are required for pyinstaller