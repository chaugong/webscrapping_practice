import requests
from bs4 import BeautifulSoup
from time import sleep
import sys 
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
import csv
import os.path

class Render(QWebEnginePage):  
  def __init__(self, url):  
    if not QApplication.instance():
      self.app = QApplication(sys.argv)  
    else:
      self.app = QApplication.instance()      
    QWebEnginePage.__init__(self)  
    self.html = ''
    self.loadFinished.connect(self._on_load_finished)  
    self.load(QUrl(url))  
    self.app.exec_()  
    
  def _on_load_finished(self):
    self.html = self.toHtml(self.Callable)
    print('Load finished')

  def Callable(self, html_str): 
    self.html = html_str
    self.app.quit()  

def view_html(soup):
    f = open("viewhtml.txt",'w',encoding="utf-8")
    f.write(soup)
    f.close()


def get_soup(url):
    response = requests.get(url)
    if not response.ok:  #status code == 200
        print(f'Code:{response.status_code},url:{url}')
    #print(response.text)
    return BeautifulSoup(response.text,'lxml')

def write_csv(data,fields):
    file_exists = os.path.isfile('stock.csv') #check if the file exists
    with open('stock.csv','a',encoding='utf8',newline='') as f: 
        writer=csv.DictWriter(f,fieldnames=fields)
        if not file_exists:
            writer.writeheader()  #Write the header once when append mode
        writer.writerow(data)
#https://stackoverflow.com/questions/28325622/python-csv-writing-headers-only-once 

def percentage_changes(lixt):
    temp = []
    for i in range(len(lixt)-1): #i want to make a try-except to print the problematic stock no if any
           changes=str(round((lixt[i+1]-lixt[i])/lixt[i]*100,2))+'%'
           temp.append(changes)
    return temp


url = 'http://www.aastocks.com/tc/stocks/market/industry/industry-performance.aspx'

soup = get_soup(url)

#stores the tags that has industries info in a list 
ind_tags=soup.find_all("a",class_="a15 cls")

#get the links of each industries
ind_links=[ind["href"] for ind in ind_tags] #print(ind_link)

stock_links=[]
for ind in ind_links:
  url = 'http://www.aastocks.com' + ind
  r = Render(url)
  soup = BeautifulSoup(r.html,'lxml')
  stock_links.extend([tag["href"] for tag in soup.find_all("a",class_="a14 cls")])
  sleep(0.3)

for stock in stock_links:
    stock_no=stock.split('=')[1]
    full_link='http://www.aastocks.com' + stock
    r=Render('http://www.aastocks.com/tc/stocks/analysis/company-fundamental/profit-loss?symbol='+ stock_no)
    soup = BeautifulSoup(r.html,'lxml')
#we cannot change a list of string to a list of int by int(list)
#replace(',','') removes all the comma
    gross_profit=[]
    try: 
       tags = soup.find("tr",attrs={"ref":"PL_Field_NB_4_6"}).find_all("td",class_=r"cfvalue")
       for tag in tags:
          try:
            gross_profit.append(int(tag.text.replace(',','')))
          except:
            pass
    except AttributeError:
      gross_profit_changes=[]
      pass
    else:
      gross_profit_changes=percentage_changes(gross_profit)    
    
    data={
         'stock no.':stock_no,
         'link':full_link,
         'gross_profit_changes':', '.join(gross_profit_changes)
    }
    fields = ['stock no.','link','gross_profit_changes']
    write_csv(data,fields)
    sleep(0.3)

#print(len(stock_links))





           


