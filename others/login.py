import re
from mechanize import Browser


def login(bbsid, passwd):
    URL = "http://www.mitbbs.com/mitbbs_login.php"
    br = Browser()
    br.open(URL)
    br.select_form(name="login")
    br["id"] = bbsid
    br["passwd"] = passwd
    response = br.submit()
    #response.geturl()
    #print(response.read()) # this will destroy response?
    text = response.read()
    if('alert' in text):
        return False
    else:
        return True



#login("myid","mypassword")