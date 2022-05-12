# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

class ProductSpider(scrapy.Spider):
    name = 'firestore'
    allowed_domains = ['www.thefirestore.com']

    def start_requests(self):
        url = 'https://www.thefirestore.com/store/brands.aspx/'
        yield SplashRequest(
            url,
            headers = {
                'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
            }
            )    

    def parse(self, response):
        for manufacturer in response.xpath("//ul[@class = 'quad']/li"):
            man_link = manufacturer.xpath(".//a/@href").get()
            man_link += '#/orderby/9/offset/0/limit/10000'
            yield SplashRequest(
                man_link,
                headers = {
                    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
                },
                callback = self.parse_products
                ) 


    def parse_products(self, response):
        products = response.xpath("//div[contains(@class, 'listing-item')]")
        for product in products:
            product_url = product.xpath("div[@class = 'product-name']/a/@href").get()
            yield SplashRequest(
                product_url,
                headers = {
                    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
                },
                callback = self.parse_details                                
            )
            # yield {
            #     'Brand' : product.xpath("//div[@class = 'manufacturer-name']/text()").get(),
            #     'Product' : product.xpath("div[@class = 'product-name']/a/text()").get(),
            #     'product_url' : product.xpath("div[@class = 'product-name']/a/@href").get()
            #     }

    def parse_details(self, response):
        brand = response.xpath("normalize-space(//span[@itemprop = 'brand']/text())").get()
        name = response.xpath("//h1[@class = 'ProductNameDiv']/text()").get()
        sku = response.xpath("//span[@class = 'ProductCode']/text()").get()

        seller = response.xpath("//span/span[@itemprop = 'name']/text()").get()

        list_price =response.xpath("(//div[@id = 'ProductActualListPriceDiv']/span)[1]/text()").get()
        markdown_price = response.xpath("(//div[@id = 'ProductActualListPriceDiv']/span)[2]/text()").get()
        sale_price = response.xpath("normalize-space(//div[@id = 'ProductActualPriceDiv']/text())").get()

        buyer_rating = response.xpath("//span[@class = 'pr-rating pr-rounded average']/text()").get()
        review_count = response.xpath("(//div[@class = 'pr-snippet-read-reviews']/a/span)[1]/text()").get()
        recommendation_score = response.xpath("//p[@class = 'pr-snapshot-consensus-value pr-rounded']/text()").get()
        questions_answers = response.xpath("//div[@class = 'prPaCounts']/text()").get()          

        breadcrumbs = response.xpath("//div[@class = 'CategoryBreadCrumb']/a")
        breadcrumb = []
        for b in breadcrumbs:
            breadcrumb.append(b.xpath(".//text()").get())
        
        keywords = response.xpath("normalize-space(///meta[@name = 'keywords']/@content)") .get()


        all_options = {}
        options = response.xpath("//div[@class = 'ProductOptionSetDiv']")
        for o in options:
            option_title = o.xpath(".//span[1]/text()").get()

            suboptions = []
            for s in o.xpath(".//span[contains(@class, 'ProductOptionButtonSpan ')]"):
                suboptions.append(s.xpath(".//text()").get())
            all_options[option_title] = suboptions

        sentiments = {}

        for s in response.xpath("(//div[@class  = 'pr-review-points-attr-wrapper'])[1]/div[not(@style)]"):
            sentiment_category = s.xpath(".//div/div/p/text()").get()
            sentiment_attributes = s.xpath(".//div[@class = 'pr-attribute-value']/ul/li")
            attributes = []
            for sa in sentiment_attributes:
                attributes.append(sa.xpath(".//text()").get())
            sentiments[sentiment_category] = attributes


        yield {
            'product' : name,
            'brand' : brand,
            'sku' : sku,
            'seller' : seller,
            'list_price' : list_price,
            'markdown_price' : markdown_price,
            'sale_price' : sale_price,
            'buyer_rating' : buyer_rating,
            'review_count' : review_count,
            'recommendation_score' : recommendation_score,
            'question_answer' : questions_answers,
            'keywords' : keywords,
            'product_options' : all_options,
            'sentiment' : sentiments
        }