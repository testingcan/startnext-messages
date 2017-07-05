# startnext-messaging

Tool to send message to backers of startnext-projects.
This tool uses [Scrapy](https://github.com/scrapy/scrapy) to navigate startnext.com in order to send a predefinded message to all backers of a particular project. 

## 1. Requirements

* Python 2.7
* Scrapy 1.4
* Works on Linux/Mac/Windows

## 2. Usage

After having [installed Scrapy](https://doc.scrapy.org/en/latest/intro/install.html), clone the repo, navigate to the repo and start the spider. 

    git clone https://github.com/testingcan/startnext-messaging.git
    cd startnext-messaging
    scrapy crawl start
    
The crawler will then lead you through the crawling process, just follow the prompts. 

### 2.1 Login-credentials

The crawler will ask you to enter your login-credentials each time. You can also set them manually in the spider, see 

## 3. Tips

Some parts of the spider are customizable:

### 3.1 Confirmation

If you want, you can enable a confirmation, before sending each message. Simply uncomment *lines 112 - 119* and comment *line 120* in `startnext/startnext/spiders/start.py`
The crawler will now ask you for confirmation before sending **each** message. 

### 3.2 Customize message

The message is located in line 101. You can simply edit the message to suit your needs. Simply remember to insert breaks with `\n`. 
The spider takes care of converting the message before sending it to the server. 

### 3.3 Setting login-credentials

You can set the login-credentials in the `parse`-function. Simply input your credentials into the request (*line 25*) and delete *lines 21 - 22*. 

## 4. Notes

Please consider setting `CONCURRENT_REQUESTS` and `DOWNLOAD_DELAY` in the `settings.py` or enabling the Scrapy [Autothrottle-extension](https://doc.scrapy.org/en/latest/topics/autothrottle.html) before running the spider. This eases the load on the server by not hitting it with to many requests at once. 

### Respect the site you are crawling!
