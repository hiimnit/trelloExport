from trello import TrelloApi
import json
from datetime import datetime

CUSTOMFIELDSID = '56d5e249a98895a9797bebb9'
FIELDID = [
            ['t5vcK1ms-9ISN06', 'Hodiny'] # HPST
          ]


def handleCustomFields(valueString):
    if valueString == '':
        return([])

    try:
        fields = json.loads(valueString)
    except json.decoder.JSONDecodeError:
        return([])

    list = []

    #handle fields
    #try:
    #    list.append([FIELDID[0][1], fields['fields'][FIELDID[0][0]]])
    #except KeyError:
    #    pass

    for ID in FIELDID:
        if ID[0] in fields['fields'].keys():
            list.append([ID[1], fields['fields'][ID[0]]])

    return(list)


def getIntegerInput(prompt):
    while True:
        try:
            return(int(input(prompt)))
        except ValueError:
            print('NaN')


class tr:
    trello  = None
    boards  = []
    cards   = []
    lists   = []
    #members = []
    me      = None

    def __init__(self, key, token):
        self.trello = TrelloApi(key, token)

    def getMyBoards(self, doPrint=False):
        self.me = self.trello.members.get('me')
        boards = self.trello.members.get_board('me')

        self.boards = []
        for board in boards:
            self.boards.append([board['id'], board['name']])

        if doPrint:
            self.printList(self.boards, 1, False)

    def printList(self, list, position=1, all_option=False):
        i = 0

        for element in list:
            print(str(i) + ' : ' + element[position])
            i += 1

        if all_option:
            print(str(i) + ' : all')

    def getBoardListsByNo(self, boardNo, doPrint=False):
        if boardNo < 0 or boardNo >= len(self.boards):
            return

        boardId = self.boards[boardNo][0]

        self.getBoardListsById(boardId, doPrint)

    def getBoardListsById(self, boardId, doPrint=False):
        lists = []
        lists = self.trello.boards.get_list(boardId, fields='id,name')
        #members = []
        #members = self.trello.boards.get_member(boardId, fields='id,username')

        for list in lists:
            self.lists.append([list['id'], list['name']])

        if doPrint:
            self.printList(self.lists, 1, True)
        #for member in members:
        #    self.members.append([member['id'], member['username']])

    def getBoardCardsById(self, boardId):
        cards = []
        cards = self.trello.boards.get_card(boardId, fields='id,name')

        for card in cards:
            self.cards.append([card['id'], card['name']])

    def getBoardCardsByNo(self, boardNo):
        if boardNo < 0 or boardNo >= len(self.boards):
            return

        boardId = self.boards[boardNo][0]

        self.getBoardCardsById(BoardId)

    def getListCardsById(self, listId):
        cards = []
        cards = self.trello.lists.get_card(listId, fields='id,name')

        for card in cards:
            self.cards.append([card['id'], card['name']])

    def getListCardsByNo(self, listNo):
        if listNo < 0 or listNo >= len(self.lists):
            return

        listId = self.lists[listNo][0]

        self.getListCardsById(listId)

    def getCardById(self, cardId, field=''):
        card = self.trello.cards.get(cardId, fields=field)

        return card

    def getCardByNo(self, cardNo):
        if cardNo < 0 or cardNo >= len(self.cards):
            return

        cardId = self.cards[cardNo][0]

        return self.getCardById(cardId)

    def getCardPluginDataById(self, cardId):
        pluginData = self.trello.cards.get_plugin_data(cardId)

        customFields = []
        for data in pluginData:
            if data['idPlugin'] == CUSTOMFIELDSID:
                customFields = handleCustomFields(data['value'])

        return customFields

    def getCardPluginDataByNo(self, cardNo):
        if cardNo < 0 or cardNo >= len(self.cards):
            return

        cardId = self.cards[cardNo][0]

        return self.getCardPluginDataById(cardId)

    def exportCurrentCards(self, me_only=False):
        file = open(str(datetime.now().strftime('%Y%m%d')) + '.csv', 'a')

        i = 0
        for card in self.cards:
            cardDetails = self.getCardById(card[0], 'id,name,shortUrl,idMembers')
            if me_only:
                if not self.me['id'] in cardDetails['idMembers']:
                    continue

            customFields = self.getCardPluginDataById(card[0])

            line = str(i) + ';"' + cardDetails['name'][:30] + '";"' + cardDetails['shortUrl'] + '"'

            for field in customFields:
                line += ';' + field[1]

            file.write(line + '\n')

            i += 1

        file.close()

## main ####################################

with open('key.txt', 'r') as f:
    lines = f.readlines()

KEY = lines[0].rstrip('\n')
TOKEN = lines[1].rstrip('\n')

print(KEY)
print(TOKEN)

t = tr(KEY, TOKEN)

selectedBoard = -1

while True:
    print('=============================================')

    t.getMyBoards(True)
    while selectedBoard < 0 or selectedBoard >= len(t.boards):
        selectedBoard = getIntegerInput('board no.: ')

    print('=============================================')

    t.getBoardListsByNo(int(selectedBoard), True)
    selectedList = -1
    while selectedList < 0 or selectedList > len(t.lists):
        selectedList = getIntegerInput('list no.: ')

    if selectedList == len(t.lists):
        t.getBoardCardsByNo(selectedBoard)
    else:
        t.getListCardsByNo(selectedList)

    print('=============================================')

    t.printList([['me']], 0, True)

    selectedMember = -1
    while selectedMember < 0 or selectedMember > 1:
        selectedMember = getIntegerInput('member .: ')


    print('=============================================')

    t.exportCurrentCards(selectedMember == 0)

    break

pass
