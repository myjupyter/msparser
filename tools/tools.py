import json

CONT_SELECTOR = 'div[class="table-responsive"] table[class="sbody-table table"]'
ITEM_SELECTOR = 'tr[class="sbody-tr"]'
PART_SELECTOR = 'td[class="sbody-td"]'
SUBCATH_SELECTOR = 'h4[class="sbody-h4"]'
CATH_AND_SUBCATH = ['h3', 'h4']

def getcontent(tag):
    if len(tag.contents):
        return tag.contents[0]
    return ""

def check_tags(tag):
    if len(tag.select(PART_SELECTOR)):
        return True
    return False

class Item:
    def __init__(self, parser):
        parts = parser.select(PART_SELECTOR)
        self.__value = str(getcontent(parts[0]))
        self.__meaning = str(getcontent(parts[1]))

    def to_json(self):
        return {
            "EventCode": self.__value,
            "Description": self.__meaning 
        }

class ItemContainer:
    def __init__(self, parser, sub_cath = "default"):
        items = parser.select(ITEM_SELECTOR)
        self.__items = [Item(i) for i in filter(check_tags ,items)]
        self.__sub_cath = sub_cath

    def set_sub_cath(self, sub_cath):
        self.__sub_cath = sub_cath

    def to_json(self):
        return {
            "Title": self.__sub_cath,
            "Items": [i.to_json() for i in self.__items]
        }
    
class Cathegory:
    def __init__(self, cath = 'default'):
        self.__cath = cath 
        self.__containers = list()

    def append(self, cont):
        self.__containers.append(cont)

    def set_cath(cath):
        self.__cath = cath 
    
    def to_json(self):
        return {
            "Title": self.__cath,
            "Items": [c.to_json() for c in self.__containers]
        }

class Descriptions:
    def __init__(self, parser):
        containers = parser.select(CONT_SELECTOR)
        sub_caths = parser.select(SUBCATH_SELECTOR)
        
        conts = [ItemContainer(c) for c in containers]
        
        self.__caths = list()
        iterator = iter(conts)

        for head in parser.find_all(CATH_AND_SUBCATH):    
            head_name = getcontent(head).split(':')
            head = head.get('class')[0]
            if len(head_name) == 1:
                return
            if head == 'sbody-h3':
                self.__caths.append(Cathegory(head_name[1]))
            if head == 'sbody-h4':
                cont = next(iterator)
                cont.set_sub_cath(head_name)
                self.__caths[-1].append(cont)

    def to_json(self):
        return json.dumps({
            "data": [cath.to_json() for cath in self.__caths]
        }, ensure_ascii=False)
