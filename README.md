# zookeeper browser
- GUI for zookeeper writtten in python 

This is python 2.7 web application for browsing zookeeper data. You can also add new nodes, delete nodes, and change node data.
![image](/zkbrowser.png?raw=true "Zookeeper browser")

# Installation

## Set up virtural environment (if you want)
```
pip install vertualenv
virtualenv vezk
. ./vezk/bin/activate
```

## Installing zookeeper browser
```
git clone https://github.com/mijalko/zookeeper_browser.git
cd zookeeper_browser
pip install -r requirements.txt
```

## Running application
```
python zkbrowser.py
```

Application will be availabele on http://localhost:4550

## Docker

Zookeeper browser is available as Docker container at https://hub.docker.com/r/mijalko/zkbrowser/
You can download container with command:
```docker run --name zkbrowser -d -p 4550:4550 mijalko/zkbrowser```


Like it? Buy me a coffe.
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DSVSVGSTSKNJ4)
