import datetime
import re

from flask import g
import evelink

from audit.skills import skills


class Character(object):

    def __init__(self, cid=None, name=None):
        self.id = cid
        self.name = name
        self.corporation = None
        self.alliance = None

    @classmethod
    def from_api(cls, char_id):
        acc = evelink.account.Account(g.api)
        char = acc.characters()[char_id]
        c = Character(char_id, char['name'])
        c.corporation, alliance_id = Corporation().from_api(char['corp']['id'])
        if alliance_id:
            c.alliance = Alliance().from_api(alliance_id)
        return c

    def skill_sheet_from_api(self):
        char = evelink.char.Char(self.id, g.api)
        self.char_sheet = char.character_sheet()
        self.set_skills()

    def mails_from_api(self):
        char = evelink.char.Char(self.id, g.api)
        self._messages = {}
        for m in char.messages():
            mid = m['timestamp']
            m['from'] = self.messages_from(m)
            m['to'] = self.messages_to(m)
            m['timestamp'] = datetime.datetime.fromtimestamp(m['timestamp']).strftime("%Y-%m-%d %H:%M")
            self._messages[mid] = m
        mids = []
        m_to_t = {}
        for t, m in self._messages.iteritems():
            mids.append(m['id'])
            m_to_t[m['id']] = t
        for mid, body in char.message_bodies(mids).iteritems():
            # strip font tags... They fuck shit up
            body = re.sub(r"\<font.*?\>", "", body)
            body = body.replace("</font>", "")
            self._messages[m_to_t[mid]]['body'] = body

    @property
    def contacts(self):
        char = evelink.char.Char(self.id, g.api)
        personal = char.contacts()['personal']
        return [x for x in personal.itervalues()]

    @property
    def wallet(self):
        char = evelink.char.Char(self.id, g.api)
        reftypes = g.eve.reference_types()
        trans = char.wallet_journal()
        self._transactions = {}
        for t in trans:
            tid = t['timestamp']
            t['reftype'] = reftypes[t['type_id']]
            t['timestamp'] = datetime.datetime.fromtimestamp(t['timestamp']).strftime("%Y-%m-%d %H:%M")
            self._transactions[tid] = t
        return [self._transactions[x] for x in reversed(sorted(self._transactions.iterkeys()))]

    @property
    def messages(self):
        return [self._messages[x] for x in reversed(sorted(self._messages.iterkeys()))]

    def messages_to(self, m):
        if m['to']['list_ids']:
            to = ["(mailing list)", ]
        elif m['to']['org_id']:
            to = self.messages_org_from_to(m['to']['org_id'])
        elif m['to']['char_ids']:
            to = self.messages_chars_from_to(m['to']['char_ids'])
        else:
            to = ["(unknown)", ]
        return to

    def messages_from(self, m):
        mfrom = self.messages_chars_from_to(m['sender_id'])
        if not mfrom or len(mfrom) < 1:
            mfrom = self.messages_org_from_to(m['sender_id'])
        return mfrom[0]

    def messages_org_from_to(self, org_id_list):
        if isinstance(org_id_list, int):
            oid = org_id_list
            org_id_list = [oid, ]
        alliances = g.eve.alliances()
        corp_api = evelink.corp.Corp(g.api)
        names = []
        for cs in org_id_list:
            if cs in alliances:
                names.append(alliances[cs]['name'])
            try:
                cs = corp_api.corporation_sheet(cs)
                names.append(cs['name'])
            except evelink.api.APIError:
                names.append("(unknown)")
        return names

    def messages_chars_from_to(self, char_id_list):
        if isinstance(char_id_list, int):
            cid = char_id_list
            char_id_list = [cid, ]
        try:
            return [x for x in g.eve.character_names_from_ids(char_id_list).itervalues()]
        except evelink.api.APIError:
            return []

    def set_skills(self):
        self.skills = {}
        lskills = {}
        for askill in self.char_sheet['skills']:
            lskills[askill['id']] = {'level': askill['level'],
                                     'sp': askill['skillpoints']}
        for skill in skills:
            level = 0
            sp = 0
            if skill['id'] in lskills.keys():
                level = lskills[skill['id']]['level']
            if skill['id'] in lskills.keys():
                sp = lskills[skill['id']]['sp']
            s = Skill(skill['id'], skill['name'],
                      skill['group_id'], skill['group_name'],
                      level, sp)
            self.skills[s.id] = s

    @property
    def balance(self):
        return '{:20,.2f}'.format(self.char_sheet['balance'])

    @property
    def skillpoints(self):
        return '{:20,d}'.format(self.char_sheet['skillpoints'])

    @property
    def number_of_skills(self):
        return '{:20,d}'.format(len(self.char_sheet['skills']))

    @property
    def frigates(self):
        frigs = (3331, 3330, 3328, 3329)
        return [self.skills[x] for x in frigs]

    @property
    def cruisers(self):
        cruisers = (3335, 3334, 3332, 3333)
        return [self.skills[x] for x in cruisers]

    @property
    def battleships(self):
        battleships = (3339, 3338, 3336, 3337)
        return [self.skills[x] for x in battleships]

    @property
    def t2_ships(self):
        t2 = (12093, 12092, 12098, 16591, 28609, 22761,
              12096, 23950, 28656, 28667)
        return [self.skills[x] for x in t2]

    @property
    def t3_ships(self):
        t3 = (30650, 30532, 30536, 30539, 30537, 30538,
              30651, 30544, 30542, 30548, 30549, 30552,
              30652, 30540, 30541, 30546, 30550, 30553,
              30653, 30545, 30543, 30547, 30551, 30554)
        return [self.skills[x] for x in t3]

    @property
    def scanning(self):
        scan = (3412, 25811, 25810, 25739)
        return [self.skills[x] for x in scan]

    # cap skills...
    @property
    def cap_support(self):
        cap_support = (20342, 20533, 3456, 21611, 21610,
                       21803, 21802)
        return [self.skills[x] for x in cap_support]

    @property
    def drugs(self):
        drugs = (3405, 25538, 25530)
        return [self.skills[x] for x in drugs]

    @property
    def carriers(self):
        carriers = (24311, 24312, 24313, 24314, 27906,
                    24568, 24571, 24572)
        return [self.skills[x] for x in carriers]

    @property
    def dreads(self):
        dreads = (20525, 20530, 20531, 20532, 22043,
                  20327, 32435, 21668, 21666, 21667)
        return [self.skills[x] for x in dreads]

    @property
    def guns(self):
        guns = (12213, 11083, 12210, 11082, 11084, 12201,
                12214, 12204, 12211, 12206, 12208, 12202,
                12215, 12205, 12212, 12207, 12209, 12203,
                3318, 11207, 3316, 3312, 3310, 3311, 3316,
                3317)
        return [self.skills[x] for x in guns]

    @property
    def missiles(self):
        missiles = (20210, 20209, 25718, 20211, 20212,
                    20213, 28073, 20312, 12441, 20314,
                    20315)
        return [self.skills[x] for x in missiles]

    def racial_drones_level(self, wanted):
        r = (12484, 12487, 12486, 12485)
        for i in r:
            if self.skills[i].level >= wanted:
                return True
        return False

    @property
    def t2_lights(self):
        if self.racial_drones_level(2) and self.skills[3437].level == 5:
            return True

    @property
    def t2_heavies(self):
        if self.racial_drones_level(4) and self.skills[3441].level == 5:
            return True

    @property
    def t2_sentries(self):
        return True if self.skills[23594].level == 5 else False

    @property
    def t2_repair_drones(self):
        return True if self.skills[3439].level == 5 else False

    @property
    def fighters(self):
        return True if self.skills[23069].level > 0 else False

    @property
    def fighter_bombers(self):
        return True if self.skills[32339].level > 0 else False

    @property
    def leadership(self):
        leadership = (3348, 11574, 24764, 20494, 11569, 20495, 3352,
                      3350, 3351, 3349, 11572, 3354)
        return [self.skills[x] for x in leadership]

    @property
    def armored_warfare_mindlink(self):
        if self.skills[3411].level == 5 and self.skills[11569].level == 5:
            return True
        return False

    @property
    def information_warfare_mindlink(self):
        if self.skills[3411].level == 5 and self.skills[3352].level == 5:
            return True
        return False

    @property
    def siege_warfare_mindlink(self):
        if self.skills[3411].level == 5 and self.skills[3351].level == 5:
            return True
        return False

    @property
    def skirmish_warfare_mindlink(self):
        if self.skills[3411].level == 5 and self.skills[11572].level == 5:
            return True
        return False


class Corporation(object):

    def __init__(self, cid=None, name=None, ticker=None):
        self.id = cid
        self.name = name
        self.ticker = ticker

    @classmethod
    def from_api(cls, corp_id):
        corp_api = evelink.corp.Corp(g.api)
        corp_sheet = corp_api.corporation_sheet(corp_id)
        corp_name = corp_sheet['name']
        corp_ticker = corp_sheet['ticker']
        alliance_id = corp_sheet['alliance']['id']
        return Corporation(corp_id, corp_name, corp_ticker), alliance_id


class Alliance(object):

    def __init__(self, aid=None, name=None, ticker=None):
        self.id = aid
        self.name = name
        self.ticker = ticker

    @classmethod
    def from_api(cls, alliance_id):
        alliances = g.eve.alliances()
        alliance_sheet = alliances[alliance_id]
        alliance_name = alliance_sheet['name']
        alliance_ticker = alliance_sheet['ticker']
        return Alliance(alliance_id, alliance_name, alliance_ticker)


class Skill(object):

    def __init__(self, sid, name, gid, gname, level=0, skillpoints=0):
        self.id = int(sid)
        self.name = name
        self.group_id = gid
        self.group_name = gname
        self.level = level
        self.skillpoints = skillpoints
