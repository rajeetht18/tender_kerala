# -*- coding: utf-8 -*-
import scrapy
import psycopg2
import re

conn = psycopg2.connect(database = "Kerala_Tenders", user = "postgres", password = "odoo", host = "localhost", port = "5432")
cur = conn.cursor()
allowed_domains = ["etenders.kerala.gov.in"]
page_count = 1

class TenderSpider(scrapy.Spider):
    name = "tender"
    start_urls = [
        'https://etenders.kerala.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page',
    ]
    
    def parse(self, response):
        tenders = response.xpath('//table[@id="table"]/tr')
        count = 1
        global page_count

        for tender in tenders:
            if count > 1:
                publish_date = tender.xpath('td[2]/text()').extract()
                closing_date = tender.xpath('td[3]/text()').extract()
                opening_date =  tender.xpath('td[4]/text()').extract()
                title = tender.xpath('td[5]/a/text()').extract()
                #title = re.split(r'\[|\]', title)
                tender_details = '\t'.join(tender.xpath('td[5]/text()').extract()).strip()
                tender_details = re.split(r'\[|\]', tender_details)
                organisation = '\t'.join(tender.xpath('td[6]/text()').extract()).strip()
                #Insert values
                if publish_date:
                    #cur.execute("INSERT INTO tender_details (e_published_date,bid_submission_closing_date,tender_opening_date,title,reference_no,tender_id,organisation_chain) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (publish_date[0], closing_date[0], opening_date[0], title[0], tender_details[1], tender_details[3], organisation));
                    cur.execute("INSERT INTO tender_details (e_published_date,bid_submission_closing_date,tender_opening_date,title,reference_no,tender_id,organisation_chain) SELECT * FROM (SELECT '%s', '%s', '%s', '%s', '%s', '%s', '%s') AS tmp WHERE NOT EXISTS ( SELECT tender_id FROM tender_details WHERE tender_id = '%s') LIMIT 1" % (publish_date[0], closing_date[0], opening_date[0], title[0], tender_details[1], tender_details[3], organisation, tender_details[3]));

            count += 1
        conn.commit()

        next_page = response.css('span[id=informal_11] a[id=linkFwd]::attr(href)').extract_first()
        print page_count,' page_count'
        #print allowed_domains[0] + next_page,' Link'
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        page_count += 1
        #conn.close()
            
