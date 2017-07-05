# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest, Selector
from scrapy.http import HtmlResponse

import json
import urllib
import getpass
from scrapy.utils.response import open_in_browser

class StartSpider(scrapy.Spider):
    name = 'start'
    allowed_domains = ['startnext.de', 'startnext.com']
    start_urls = ['https://www.startnext.com/tycon/modules/crowdfunding/mvc/controller/ajax/user/login/show.php?popin=1&type=simpleLogin&activeTab=0']

    def __init__(self, backers = [],  project = ""):
		self.backers = []
		self.project = ""

    def parse(self, response):
		email = raw_input("Please enter your e-mail-address: ")
		password = getpass.getpass("Please enter your password: ")
		request = FormRequest.from_response(
		response,
		formdata={"login_email": email, "login_password": password},
		callback=self.after_login)
		return request

    def after_login(self, response):
		if response.xpath('//div[@class="errorMsg alert alert-block alert-error"]'):
			print "Login failed!\n=========="
			yield scrapy.Request(url=self.start_urls[0], callback=self.parse)
			pass
		else:
			print "Login successful!\n=========="
			# Begin by going to first 1000 messages (as startnext enforces a
			# limit of 1000 messages per request)
			print "Updating list of already messaged backers..."
			url = "https://www.startnext.com/tycon/modules/crowdfunding/api/v1.2/users/me/conversations/private?access_token=session&client_id=10712545182146&limit=1000"
			offset = 0
			request = scrapy.Request(url=url, callback = self.message_list)
			request.meta["offset"] = offset
			yield request

    def message_list(self, response):
		# Append the first 1000 message recipients to class attribute
		data = json.loads(response.body)
		if data["conversations"]:
			for message in range(0, len(data["conversations"])):
				self.backers.append(data["conversations"][message]["participants"][1]["url"])

			offset = response.meta["offset"]
			offset += 1000
			url = response.url + "&offset={}".format(offset)
			request = scrapy.Request(url=url, callback=self.message_list)
			request.meta["offset"] = offset
			yield request

		else:
			print "Retrieved all new messages! Total of {} messages.".format(len(self.backers))
			# Begin the messaging part
			inp = input("===========\nWhat do you want to do?\n    1: Crawl a project\n    2: Send message to person\n")
			while inp not in (1, 2):
				inp = input( "==========\n Please enter a valid number (1, 2):\n")
			if inp == 1:
				project_url = raw_input("===========\nPlease paste the project-url: ")
				self.project = project_url.split("/")[-1]
				yield scrapy.Request(url=project_url, callback=self.project_page, headers={"Referer": "https://startnext.com"})
			elif inp == 2:
				backer_url = raw_input("Please paste the backer-url: ")
				self.project = raw_input("Please enter the Project name: ")
				yield scrapy.Request(url=backer_url, callback=self.backer_page)

    def project_page(self, response):
		# Each backers-page that is now being requested yields 10 backers.
		# To get the max number of pages, increment page-number up to number_of_backers / 10
		number_of_backers = int(response.xpath('////span[@class="count tyNavigationTopicID_199"]/text()').extract_first())
		for page in range(0, number_of_backers / 10):
			url = "https://www.startnext.com/tycon/modules/crowdfunding/mvc/controller/ajax/project/supporterlist.php?cf_tpl=%2Ftemplates%2Fplatforms%2Fstartnext%2Fsnippets%2Fproject%2Ffans_supporter%2Fproject.supporters.list.tpl&project_link_caption={}&page={}&topic=tyNavigationTopicID_199".format(self.project, page)
			yield scrapy.Request(url=url, callback=self.backers_page)

    def backers_page(self, response):
		data = json.loads(response.body)
		sel = Selector(text=data["supporterListHTML"])
		for backer in sel.xpath('//span[@class="headline"]/a/@href'):
			url = response.urljoin(backer.extract())
			yield scrapy.Request(url=url, callback=self.backer_page)

    def backer_page(self, response):
		if response.url in self.backers:
			print "Already message this person! Passing...\n==========="
			pass
		else:
			print "Not yet messaged.\nAdding supporter to list...\nMessaging..."
			self.backers.append(response.url)
			url = response.xpath('//a[@data-role="message"]/@href').extract_first()
			yield scrapy.Request(url=response.urljoin(url), callback=self.message)

    def message(self, response):
		supporter = response.xpath('//div[@class="contact"]/text()').extract()
		full_name = response.url.split("/")[-2]
		full_name = full_name.split("%20")
		name = full_name[0]
		surname = full_name[-1] if len(full_name) > 1 else ""
		backer_id = response.url.split("/")[-1]

		message = "Hey {}, ich habe gesehen, dass du {} unterstützt."
		adress  = "https://www.startnext.com/tycon/modules/crowdfunding/api/v1.2/conversations?access_token=session&client_id=10712545182146&userIds={}&text={}&groupTitle="
		if any(char.isdigit() for char in name):
			request_url = adress.format(backer_id, urllib.quote(message.format("du", self.project.capitalize())))
		else:
			request_url = adress.format(backer_id, urllib.quote(message.format(name.capitalize(), self.project.capitalize())))

		request = scrapy.Request(url=request_url, method="POST", callback=self.after_message)

		# Uncomment the following lines if you want to confirm the sending of each message 
		# IMPORTANT: Comment the "return request" in line 120 too!
	#	print request
	#	confirmation = raw_input("Do you want to send this message? y/n ")
	#	if confirmation == "y":
	#		print "Sending message..."
	#		return request
	#		pass
	#	else:
	#		pass
		return request

    def after_message(self, response):
	pass

