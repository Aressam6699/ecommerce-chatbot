from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
#import csrf from CSRF protection
from django.views.decorators.csrf import csrf_exempt
#import df_library
from library.df_response_lib import *
#import json to get json request
import json
import requests
import re
#from cart.cart import Cart
#from myproducts.models import Product


def cleanhtml(raw_html):
    """ Return text without any html tags """

    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def home(request):
    return HttpResponse('Hello World!')

@csrf_exempt
def webhook(request):

	aog = actions_on_google_response()
	req = json.loads(request.body)
	action = req.get('queryResult').get('action')
	session = req.get("session")
	ff_response = fulfillment_response()
	responseid = req.get('responseId')
	print("\n===============================")
	print("Response id : ",responseid)
	print("\n===============================")
	



	# build a request object of the qebhook request
	#req = json.loads(request.body)
	# # get action from json
	# action = req.get('queryResult').get('action')
	# # Django responses from webhook
	# # response for the Stage_1 intent
	# if action == "S_1":
	# 	Text_response = "You are in Stage 1."
	# # response for the Stage_2 intent
	# elif action == "S_2":
	# 	Text_response = "You are in Stage 2."
	# 	# response for the Stage_3 intent
	# elif action == "S_3":
	# 	Text_response = "You are in Stage 3."

    # response for the Stage_4 intent
	# elif action == "S_4":
	# 	Text_response = "You are in Stage 4."

	storage = []
	context = []

	# loop over the all the context 
	mess = req.get('queryResult').get("outputContexts")
	for m in mess:
		name = m.get('name')
		# save the parameter value of 'back' context which is our saved last responses
		if name[-len("back"):] == "back":
			stored = m.get("parameters").get("parameter")
			for k in stored:
				storage.append(k)

		else:
			# contexts of the current stage
			context.append(m)
	# when request for back is arise, get the last response from the storage which was saved in the parameter of the back context and remove the currernt response from the data.
	# if action == "back":
	# 	temp = storage[-2]
	# 	ff_context = temp[1]
	# 	ff_text = temp[0]
	# 	storage.pop(len(storage)-1)
	# else:
	# 	ff_text = ff_response.fulfillment_text(action)
	# 	new_data = [ff_text, context]
	# 	storage.append(new_data)

	# 	ff_out_context  = ff_response.output_contexts(session, contexts)

	# # Also activate the contexts of the last response
	# if action == "back":
	# 	for i in range(len(ff_context)):
	# 		ff_out_context.get('output_contexts').append(ff_context[i])

	# 	# set webhook response for the requested action        
	# 	reply = ff_response.main_response(fulfillment_text = ff_text, output_contexts = ff_out_context)

	# 	# webhook response
	# 	return JsonResponse(reply, safe = False)

	
	# output context from the webhook for back functionality    
	contexts = [['back', 100, {'parameter': storage}]]
	# get session name from fulfilment reqest
	session = req.get("session")
	#print("??????????????????????????????")
	#print(contexts)
	#print("??????????????????????????????")








	if action == "input.welcome":
		text_response = "Welcome "
		suggestion_text_fb = "How would you like to explore?"
		suggestions = ["Show categories", "Search product", "Browse all product"]
		s = requests.Session()
		s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
		r = s.get("http://httpbin.org/cookies")

		print(r.text)

	elif action == "browse_product":
		#flow_indicator = 2
		text_response = "Which one you would like to buy? Select to choose your's."
		length = 0
		r = requests.get('http://smartwaydirect.com/api/products?pagination=0&limit=100')
		variants={}
		if(r):
			uglyjson = r.text
			parsed = json.loads(uglyjson)
			length = (len(parsed["data"]))
			if(length>0):
				for i in range(1,length):
					if(parsed["data"][i]["variants"]):
						variants[parsed["data"][i]["id"]] = parsed["data"][i]["variants"]

		length_product_sku_flow_2 = length
		list_elements = []
		p = parsed["data"]
		# loop over all products of the page, extract the features of the product and prepare response
		for n in range(1,length_product_sku_flow_2):
			product_name = p[n].get("name")
			product_id = p[n].get("id")
			#print(product_id)
			#print("===============")
			#product_sku = p[n].get("sku")
			product_type = p[n].get("type")
			if product_type == "configurable":
				price = "As per options"
			else:
				price = p[n].get('price') 
			special_price = None
			if(p[n].get("description")):
				product_description = cleanhtml(p[n].get("description"))
			else:
				product_description = None
			image_url = ''
			if(p[n]["images"]):
				text = re.search('"1024x1024":"(.+?)","280x350"', p[n]["images"][0]["original_image_url"]).group(1)
				#print(text)		
				found = text.replace(r'\/','/')
				image_url = found

			if(p[n]["base_image"]["small_image_url"]):
				image_url = p[n]["base_image"]["small_image_url"]
			if product_type == "configurable":
				price_text = "Price starts from: "
			else:
				price_text = "Price: ₹"

			if length_product_sku_flow_2 == 1:
				if special_price != None:
					aog_sc = aog.basic_card(product_name, subtitle=  price_text+"{0:.2f}".format(float(special_price)) + "\nRegular Price: ₹ "+ str(price), image=[image_url, "Sample_image"])
				else:
					if price != None: # <--
						aog_sc = aog.basic_card(product_name, subtitle=  price_text+ str(price), image=[image_url, "Sample_image"])
					else:
						aog_sc = aog.basic_card(product_name, subtitle= " ", image=[image_url, "Sample_image"])
			else:
				if special_price != None:
					list_elements.append([product_name,  price_text+"{0:.2f}".format(float(special_price)) + "\nRegular Price: ₹ "+ str(price), [product_id, [product_name+str(1), product_name+str(2)]],[image_url, 'image_discription']]) # <--
				else:
					if price != None: # <--
						list_elements.append([product_name,  price_text+ str(price), [product_id, [product_name+str(1), product_name+str(2)]],[image_url, 'image_discription']])
					else:
						list_elements.append([product_name, " ", [product_id, [product_name+str(1), product_name+str(2)]],[image_url, 'image_discription']])

		list_title = 'Products list'
		if length_product_sku_flow_2 != 1:
			aog_sc = aog.list_select(list_title, list_elements)


		fulfillmentText = 'Here are all the products'
		aog_sr = aog.simple_response([[fulfillmentText, fulfillmentText, False]])
		ff_response = fulfillment_response()
		ff_text = ff_response.fulfillment_text(fulfillmentText)
		ff_messages = ff_response.fulfillment_messages([aog_sr, aog_sc])	
		reply = ff_response.main_response(ff_text, ff_messages)
		return JsonResponse(reply, safe = False)

	elif action == "product_list":
		#flow_indicator = 2
		category_number = req.get('queryResult').get('parameters').get("category_number")
		#print(category_number)
		r = requests.get('http://smartwaydirect.com/api/products?category_id='+str(int(category_number)))
		text_response = "Which one you would like to buy? Select to choose your's."
		length = 0
		#r = requests.get('http://smartwaydirect.com/api/products?pagination=0&limit=100')
		
		variants={}
		if(r):
			uglyjson = r.text
			parsed = json.loads(uglyjson)
			length = (len(parsed["data"]))
			if(length>0):
				for i in range(1,length):
					if(parsed["data"][i]["variants"]):
						variants[parsed["data"][i]["id"]] = parsed["data"][i]["variants"]
		length_product_sku_flow_2 = length
		list_elements = []
		p = parsed["data"]
		# loop over all products of the page, extract the features of the product and prepare response
		"""
		if(length_product_sku_flow_2 == 1):
			action = "product_detail"
			print("=================")
			print("one product only")
			print("=================")
		else:
		"""
		for n in range(length_product_sku_flow_2):
			product_name = p[n].get("name")
			product_id = p[n].get("id")
			#product_sku = p[n].get("sku")
			product_type = p[n].get("type")
			if product_type == "configurable":
				price = "As per options"
			else:
				price = p[n].get('price') 
			special_price = None
			if(p[n].get("description")):
				product_description = cleanhtml(p[n].get("description"))
			else:
				product_description = None
			image_url = ''
			
			if(p[n]["base_image"]["small_image_url"]):
				image_url = p[n]["base_image"]["small_image_url"]
			if product_type == "configurable":
				price_text = "Price starts from: "
			else:
				price_text = "Price: ₹"

			if length_product_sku_flow_2 == 1:
				if special_price != None:
					aog_sc = aog.basic_card(product_name, subtitle=  price_text+"{0:.2f}".format(float(special_price)) + "\nRegular Price: ₹ "+ str(price), image=[image_url, "Sample_image"])
				else:
					if price != None: # <--
						aog_sc = aog.basic_card(product_name, subtitle=  price_text+ str(price), image=[image_url, "Sample_image"])
					else:
						aog_sc = aog.basic_card(product_name, subtitle= " ", image=[image_url, "Sample_image"])
			else:
				if special_price != None:
					list_elements.append([product_name,  price_text+"{0:.2f}".format(float(special_price)) + "\nRegular Price: ₹ "+ str(price), [product_id, [product_name+str(1), product_name+str(2)]],[image_url, 'image_discription']]) # <--
				else:
					if price != None: # <--
						list_elements.append([product_name, price_text + str(price), [product_id, [product_name+str(1), product_name+str(2)]],[image_url, "description"]])
					else:
						list_elements.append([product_name, " ", [product_id, [product_name+str(1), product_name+str(2)]],[image_url, 'image_discription']])

		list_title = 'Products list'
		if length_product_sku_flow_2 != 1:
			aog_sc = aog.list_select(list_title, list_elements)


		fulfillmentText = 'Here are all the products'
		aog_sr = aog.simple_response([[fulfillmentText, fulfillmentText, False]])
		ff_response = fulfillment_response()
		ff_text = ff_response.fulfillment_text(fulfillmentText)
		ff_messages = ff_response.fulfillment_messages([aog_sr, aog_sc])	
		reply = ff_response.main_response(ff_text, ff_messages)
		return JsonResponse(reply, safe = False)

	# Main categories of the store - selection list response
	elif action == 'category_names':
		#print("hello")
		r = requests.get('http://smartwaydirect.com/api/categories?pagination=0')
		uglyjson = r.text
		parsed = json.loads(uglyjson)
		text_response = 'Select your category here.'
		list_elements = [] 
		#print(parsed["data"])
		for i in range(len(parsed["data"])):
			category_name = parsed["data"][i]["name"]
			category_id = parsed["data"][i]["id"]
			image_url = ""
			description = ""
			if(parsed["data"][i]["image_url"] != None):
				text = re.search('"1024x1024":"(.+?)","418x418"', parsed["data"][i]["image_url"]).group(1)
				image_url = text.replace(r'\/','/')
			if(parsed["data"][i]["description"] != None):
				description = parsed["data"][i]["description"]
			if len(parsed["data"]) == 1:
				text_response = "Say 'Subcategory' to check more subcategory of "+ parsed["data"][i]["name"] +"."
				suggestions = ["Subcategory", "Back"]
				one_product = 1
				aog_sc = aog.basic_card(category_name, subtitle="check subcategories of "+str(category_name), image=[image_url, "Sample_image"])
			else:
				list_elements.append([category_name, "check products of "+str(category_name), [category_id, [category_name+str(1), category_name+str(2)]],[image_url, description]])
		if len(parsed["data"]) > 1:
			list_title = "Categories"
			aog_sc = aog.list_select(list_title, list_elements)

		fulfillmentText = 'Here are all the products'
		#print("wef,sl")
		aog_sr = aog.simple_response([[fulfillmentText, fulfillmentText, False]])
		ff_response = fulfillment_response()
		ff_text = ff_response.fulfillment_text(fulfillmentText)
		ff_messages = ff_response.fulfillment_messages([aog_sr, aog_sc])	
		reply = ff_response.main_response(ff_text, ff_messages)
		return JsonResponse(reply, safe = False)

	

	elif action == 'product_detail':
		#print("In Product detail")
		#print("=================")
		suggestion_text_fb = "Use 'Back' to check previous response."
		product_list = []

		# Exctracting the product details using the Magento API
		#product_id = req.get('queryResult').get('parameters').get("category_number") #get parameters from json
		product_id = req.get('queryResult').get('parameters').get("product_id")
		parameters = product_id
		#if(parameters != ""):
		#	request.session["current_product"] = parameters
		#print(parameters)
		#print("=================")
		# look at this later


		if parameters == "":
			redirect = 1
			outputContexts = req.get('queryResult').get('outputContexts')
			for m in outputContexts:
				name = m.get("name")
				word = "one_item_list"
				if name[-len(word):] == word:
					parameters = m.get('parameters').get('key_value')
		#print('http://smartwaydirect.com/api/products/'+str(int(parameters)))
		r = requests.get('http://smartwaydirect.com/api/products/'+str(int(parameters)))
		uglyjson = r.text
		parsed = json.loads(uglyjson)
		#print(parsed)

		length = (len(parsed["data"]))
		#text_response = "Which one you would like to buy? Select to choose your's."
			
		"""
		product_source_path = str(base_url+"rest/V1/products/?searchCriteria[filter_groups][0][filters][0][field]=sku&searchCriteria[filter_groups][0][filters][0][value]="+parameters+"&searchCriteria[filter_groups][0][filters][0][condition_type]=like")
		resource_product = Resource(product_source_path, oauth)
		product_dict = resource_product.get()
		product_list_json = product_dict.json()
		product_list.append(product_list_json)
		"""
		# Reading the features of the product (name, price, image url, url key, product description)
		# all try and excepts are either for solving SKU string format error or data insufficency of the product
		product_name = None
		product_type = None
		b = parsed["data"]
		try:
			product_name = b['name']
		except:
			try:
				product_name = b['name']
			except:
				pass
		product_id = b['id']
		product_type = b['type']
		"""
		try:
			product_id = b['id']
			button = base_url +"catalog/product/view/id/"+ str(product_id)
		except:
			try:
				product_id = b['id']
				button = base_url +"catalog/product/view/id/"+ str(product_id)
			except:
				pass
		try:
			product_type = b['type']
		except:
			try:
				product_type = b['items'][0]['type_id']
			except:
				pass

		"""
		prices = []
		if product_type == "configurable":
			# children_product_path = str(base_url+"rest/V1/configurable-products/"+str(parameters)+"/children")
			# children_product_resource = Resource(children_product_path, oauth)
			# children_product_dict = children_product_resource.get()
			# children_product_json = children_product_dict.json()
			# for child in children_product_json:
			# 	prices.append(child['price'])
			# product_price = min(prices)
			for j in range(len(b["variants"])):
				prices.append(b["variants"][j]["price"])
			product_price = min(prices)
		else:
			product_price = b["price"]
			"""
			try:
				product_price = b['price']
			except:
				try:
					product_price = b['items'][0]['price']
				except:
					pass
			
		if product_type == "configurable":
			try:
				configuration_options = b['extension_attributes']['configurable_product_options']
			except:
				try:
					configuration_options = b['items'][0]['extension_attributes']['configurable_product_options']
				except:
					pass

			"""
		product_description = ""
		image_url = ""
		meta_title = " "
		special_price = " "
		if(b['description']):
			product_description = cleanhtml(b['description'])
		if(b['base_image']):
			image_url = b['base_image']["small_image_url"]


			
		"""
		try:
			for c in b['items'][0]['custom_attributes']:
				if c['attribute_code'] == "description":
					product_description = df_lib.cleanhtml(c['value'])
				elif c['attribute_code'] == 'image':
					product_image = c['value']
					image_url = base_url+ 'pub/media/catalog/product' + product_image
				elif c['attribute_code'] == 'meta_title':
					meta_title = c['value']
				elif c['attribute_code'] == 'special_price':
					special_price = c['value']
		except:
			try:
				for c in b['items'][0]['custom_attributes']:
					if c['attribute_code'] == "description":
						product_description = df_lib.cleanhtml(c['value'])
					elif c['attribute_code'] == 'image':
						product_image = c['value']
						image_url = base_url+ 'pub/media/catalog/product' + product_image
					elif c['attribute_code'] == 'meta_title':
						meta_title = c['value']
					elif c['attribute_code'] == 'special_price':
						special_price = c['value']
			except:
				pass


		"""
		# if product type id is configurable than extract the conguration options of that product
		#if product_type == "configurable":
		#configuration_options = b 
		configuration_options_text = ""
		if product_type == "configurable":
			option_name = []
			options_text = []
			
			for i in b["variants"]:
				option_name.append(i["name"])

			for i in range(len(b["super_attributes"])):
				for j in range(len(b["super_attributes"][i]["options"])):
					options_text.append(b["super_attributes"][i]["options"][j]["label"])

			# print("==========================")
			# print(option_name)
			# print("==========================")
			# print(options_text)
			# print("==========================")

			"""
			for option_attribute in configuration_options["variants"]:
				attribute_code = option_attribute['id']
				option_name.append(option_attribute['name'])
				
				option_code = []
				for i in option_attribute['values']:
					option_code.append(i['value_index']) 

				attribute_source_path = str(base_url+"rest/V1/products/attributes/"+str(attribute_code))
				product_resource = Resource(attribute_source_path, oauth)
				attribute_dict = product_resource.get()
				attribute_list_json = attribute_dict.json()
				attribute_options = attribute_list_json['options']
				option_text = ""
				for i in attribute_options:
					try:
						if (int(i['value']) in option_code):
							option_text += str(i['label']) + ", "
					except:
						pass
				options_text.append(option_text)

			print("==========================")
			print(option_name)
			print("==========================")
			"""


			configuration_options_text = ""
			for i in range(len(option_name)):
				configuration_options_text += " \n"+option_name[i]+": abcdefg"

		no_update = 0
		if product_name == None:
			try:
				product_name = meta_title
			except:
				no_update = 1

		if product_type == "configurable":
			price_text = "Price starts from:"
		else:
			price_text = "Price:"
		button = "Back"
		if no_update != 1:
			text_response = "You have selected " + product_name
			#aog_sc = aog.basic_card(product_name, subtitle=price_text+" ₹"+str(product_price)+configuration_options_text, formattedText=product_description, image=[image_url, "Sample_image"])
			#aog_sc = aog.basic_card(product_name, subtitle=price_text+" ₹"+str(product_price), formattedText=product_description, image=[image_url, "Sample_image"])
		
			try:
				aog_sc = aog.basic_card(product_name, subtitle= price_text+" ₹"+"{0:.2f}".format(float(special_price)) + "\nRegular Price: ₹"+ str(product_price)+configuration_options_text, formattedText=product_description, image=[image_url, "Sample_image"])
			except:
				try:
					aog_sc = aog.basic_card(product_name, subtitle=price_text+" ₹"+str(product_price)+configuration_options_text, formattedText=product_description, image=[image_url, "Sample_image"])
				except:
					aog_sc = aog.basic_card(product_name, subtitle=configuration_options_text, formattedText=product_description, image=[image_url, "Sample_image"])
		fulfillmentText = 'Here are all the products'
		aog_sr = aog.simple_response([[fulfillmentText, fulfillmentText, False]])
		ff_response = fulfillment_response()
		ff_text = ff_response.fulfillment_text(fulfillmentText)
		suggestions = ["Back", "Add to cart"]
		ff_messages = ff_response.fulfillment_messages([aog_sr, aog_sc,aog.suggestion_chips(suggestions)])	
		reply = ff_response.main_response(ff_text, ff_messages)
		return JsonResponse(reply, safe = False)

	elif action == "ask_search_product":
		text_response = "Please enter product name."
		suggestion_text_fb = "Say BACK to browse previous response."
		# Response of the searched product
	
	if action == "item.add":
		try:
			product_id = req.get('queryResult').get('parameters').get("product")
			quantity = req.get('queryResult').get('parameters').get("quantity")
			r = requests.get('http://smartwaydirect.com/api/products/'+str(int(product_id)))
			uglyjson = r.text
			parsed = json.loads(uglyjson)
			print("product id :", product_id)
			print("quantity :", quantity)
			print(len(parsed["data"]["variants"]))
			if quantity > 0 and len(parsed["data"]["variants"]) > 0:
				print('inside if\n ========================')
				# response = {"fulfillmentText": "Please select from the below options:",
				# "fulfillmentMessages": fulfillment_messages['fulfillment_messages'],
				# "outputContexts": output_contexts['output_contexts'],
				# "followupEventInput": followup_event_input['followup_event_input']
				# }
				response = {
					"followupEventInput": {
					"name" : "example"
					}
				}
				order = {
				"product_id" : product_id,
				"quantity" : quantity,
				"size" : "",
				"color" : ""
				}
				print("about to return : \n", response)
				request.session[responseid] = order
				print(request.session.items())
				return JsonResponse(response, safe = False)

			else:
				order = {
				"product_id" : product_id,
				"quantity" : quantity,
				"size" : "",
				"color" : ""
				}
				request.session[responseid] = order
				print(request.session.items())

		except:
			pass
			# product_id = req.get('queryResult').get('parameters').get("product")
			# quantity = req.get('queryResult').get('parameters').get("quantity")
			# r = requests.get('http://smartwaydirect.com/api/products/'+str(int(product_id)))
			# uglyjson = r.text
			# parsed = json.loads(uglyjson)
			# print("123456")
			# print("===================")
		

	#print(action)
	elif action == "item.add.super":
		product_id = req.get('queryResult').get('parameters').get("product")
		quantity = req.get('queryResult').get('parameters').get("quantity")


	if action == "back":
		temp = storage[-2]
		ff_context = temp[1]
		ff_text = temp[0]
		storage.pop(len(storage)-1)
	else:
		ff_text = ff_response.fulfillment_text(action)
		new_data = [ff_text, context]
		storage.append(new_data)

		ff_out_context  = ff_response.output_contexts(session, contexts)

	# Also activate the contexts of the last response
	if action == "back":
		for i in range(len(ff_context)):
			ff_out_context.get('output_contexts').append(ff_context[i])

		# set webhook response for the requested action        
		reply = ff_response.main_response(fulfillment_text = ff_text, output_contexts = ff_out_context)

		# webhook response
		return JsonResponse(reply, safe = False)
