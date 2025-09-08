from compeng_gg.rest_api import RestAPI

import requests

class QuercusRestAPI(RestAPI):

    API_URL = 'https://q.utoronto.ca/api/v1'

    def __init__(self, user):
        self.TOKEN = user.quercus_token.access_token

    def get(self, endpoint):
        token = self.TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.get(
            f'{self.API_URL}{endpoint}',
            headers=headers,
        )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def post(self, endpoint, data):
        token = self.TOKEN
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        r = requests.post(
            f'{self.API_URL}{endpoint}',
            headers=headers,
            json=data,
        )
        r.raise_for_status()
        if r.text == '':
            return None
        return r.json()

    def list_assignments(self, course_id):
        return self.get(f'/courses/{course_id}/assignments')

    def create_assignment(self, course_id, name, points_possible):
        data = {
            "assignment": {
                "name": name,
                "submission_types": ["none"],
                "notify_of_update": False,
                "points_possible": points_possible,
                "grading_type": "points",
                "published": True,
            }
        }
        assignment = self.post(f'/courses/{course_id}/assignments', data)
        return assignment

    def update_grades(self, course_id, assignment_id, data):
        progress = self.post(f'/courses/{course_id}/assignments/{assignment_id}/submissions/update_grades', data)
        return progress

    def list_users(self, course_id, enrollment_type):
        data = []
        page = 1
        per_page = 100
        while True:
            response = self.get(f'/courses/{course_id}/users?enrollment_type={enrollment_type}&page={page}&per_page={per_page}')
            data += response
            if len(response) != per_page:
                return data
            page += 1

    def list_instructors(self, course_id):
        return self.list_users(course_id, "teacher")

    def list_tas(self, course_id):
        return self.list_users(course_id, "ta")

    def list_students(self, course_id):
        return self.list_users(course_id, "student")

    # Required to get the `primary_email` of a user
    def get_user_profile(self, user_id):
        return self.get(f'/users/{user_id}/profile')

    def test(self):
        pass
        #import json
        #students = self.list_students('363755')
        #print('[ ', end='')
        #students = set()
        #for student in self.list_students('363755'):
        #    students.add(student)
        #    print(f"'{student['sis_user_id']}'", end=', ')
        #print(']')
        #s = set()
        #students = [ 'abdels61', 'abdelw27', 'abdelw27', 'abdul436', 'adnannoo', 'adnannoo', 'agarw556', 'agarw556', 'aggar376', 'agraw266', 'agraw266', 'ahmedi37', 'ahmedi37', 'ahujarea', 'ainaolu5', 'ainaolu5', 'alevrasy', 'alevrasy', 'alimahja', 'alimahja', 'alimithi', 'aliantod', 'aliantod', 'alievjam', 'alireza8', 'alloteyb', 'alloteyb', 'alyaser1', 'alyaser1', 'aminabd2', 'amiraffa', 'amiraffa', 'ander983', 'kartose1', 'kartose1', 'azmeeram', 'azmeeram', 'bakrnad1', 'bakrnad1', 'baner207', 'baner207', 'bansa106', 'bansa106', 'belayaar', 'belayaar', 'benipuri', 'benipuri', 'bhand158', 'bhatthit', 'biancol6', 'biancol6', 'dyerkyle', 'dyerkyle', 'caipeis1', 'caipeis1', 'carbon55', 'carnide1', 'carnide1', 'chenci10', 'chenci10', 'chenjo31', 'chenjo31', 'cheny805', 'cheny805', 'chens506', 'chens506', 'cheu1579', 'chouch14', 'choud443', 'choud443', 'chowd673', 'chowd673', 'chowd822', 'chungh44', 'ciudadre', 'ciudadre', 'clarkelo', 'clarkelo', 'cuikenny', 'cuikenny', 'dsouz463', 'dsouz463', 'daiyan3', 'dandadom', 'dangarad', 'dangarad', 'debnat25', 'delduca6', 'delduca6', 'denghan9', 'dengweia', 'diamon64', 'dometita', 'dometita', 'donerahs', 'donerahs', 'dongxi50', 'dongxi50', 'eryilma6', 'eryilma6', 'ettaarno', 'ettaarno', 'feifan11', 'ferrerja', 'ferrerja', 'feyziog2', 'firsovro', 'ganlu10', 'ganlu10', 'genusjoh', 'genusjoh', 'gergesg1', 'gergesg1', 'guogary1', 'guogary1', 'guopeiy2', 'guopeiy2', 'haggagma', 'haggagma', 'haileaha', 'haileaha', 'hanchany', 'hanchany', 'harhaymi', 'hassa949', 'hassa949', 'helanlin', 'helanlin', 'hewanni1', 'hewanni1', 'henvill1', 'henvill1', 'hilario4', 'hilario4', 'hochieh2', 'hochieh2', 'howai13', 'howai13', 'hoquerai', 'hoquerai', 'hsiangwe', 'hsiangwe', 'huchenj2', 'huchenj2', 'huzachar', 'huzachar', 'huangd54', 'hussa975', 'hussa975', 'imsihyun', 'imsihyun', 'incesum1', 'incesum1', 'jaggigu1', 'jaggigu1', 'jassima1', 'jassima1', 'jayant16', 'jengetha', 'jengetha', 'jixu5', 'jixu5', 'jian1055', 'jian1055', 'jiaokevi', 'jiaoruoj', 'jiaoruoj', 'josep324', 'josep324', 'kaewkamn', 'kaewkamn', 'kangyuje', 'kangyuje', 'karamcar', 'kashya66', 'kashya66', 'kerkate', 'kerkate', 'khanm519', 'khanm519', 'khanruh2', 'khanruh2', 'khanta32', 'khanta32', 'kimyon30', 'kimyon30', 'kimseo62', 'kingclay', 'kosztaev', 'kuangya1', 'kupendi2', 'kupendi2', 'kurttufa', 'kurttufa', 'lealashl', 'lealashl', 'leemat41', 'leesomi3', 'leesomi3', 'ligeorg7', 'lidongye', 'lidongye', 'liliuyue', 'liliuyue', 'lirich20', 'lirich20', 'liryan7', 'liryan7', 'lixia223', 'lishiy11', 'lishiy11', 'liyiqin9', 'litian59', 'litian59', 'limchri6', 'limchri6', 'linyiha3', 'linyiha3', 'linlaur2', 'linlaur2', 'linche60', 'lingyik', 'lingyik', 'liusih12', 'liusih12', 'liuedwa5', 'liuedwa5', 'liueri28', 'liueri31', 'liueri31', 'liuqingt', 'liuqingt', 'liukath8', 'liukath8', 'liuyon31', 'liuyon31', 'liusimi9', 'louying3', 'louissim', 'luyan14', 'luyan14', 'luvanes1', 'luvanes1', 'lubanata', 'lubanata', 'maciesow', 'maciesow', 'mahjess1', 'mahjess1', 'mahaj133', 'makhejag', 'marzacha', 'marzacha', 'mehtaved', 'mehtaved', 'mengjohn', 'mengjohn', 'mishrau1', 'mishrau1', 'moelinau', 'moha2276', 'moha2478', 'moha2478', 'forouha3', 'montinoa', 'montinoa', 'santo281', 'santo281', 'mostaf90', 'motasim2', 'motasim2', 'mousav79', 'mousav79', 'muyanjun', 'mujibzuh', 'mujibzuh', 'namdayou', 'namdayou', 'nazari25', 'neagudan', 'neagudan', 'ngwei7', 'ngwei7', 'ngaihan', 'ngaihan', 'nimalan9', 'nisarmu1', 'nooran26', 'nooran26', 'ohmicha3', 'omidiank', 'owusupho', 'palanik3', 'palanik3', 'panerh', 'parkja57', 'parksuy1', 'parksuy1', 'pately56', 'pately56', 'perei579', 'pethaka1', 'pethaka1', 'phambri2', 'phambri2', 'phanevel', 'phanevel', 'phasookp', 'phasookp', 'pizzonia', 'pizzonia', 'poianava', 'poianava', 'prasad74', 'prasad74', 'qidarsan', 'qidarsan', 'qihao2', 'qihao2', 'qianshi2', 'qianshi2', 'qinalexa', 'qinalexa', 'quyue4', 'quyue4', 'qures571', 'qures571', 'rahma956', 'rajabia3', 'rajabia3', 'rakhech2', 'rakhech2', 'rakhsh13', 'rakhsh13', 'rapananb', 'ravee149', 'raviku51', 'raviku51', 'raviku26', 'rayrishi', 'rayrishi', 'rehma182', 'rehma182', 'rosehar2', 'rosehar2', 'sabadoky', 'sabadoky', 'sadekhei', 'sadekhei', 'saliceso', 'savchyns', 'savchyns', 'selvend7', 'setotris', 'setotris', 'shahjay8', 'shahjay8', 'shar2399', 'shar2399', 'shar2374', 'shengx16', 'shihlanc', 'shihlanc', 'shimozat', 'shirdar2', 'shirdar2', 'shivann2', 'shrevena', 'shrevena', 'sing1726', 'sing1726', 'srivartk', 'srivartk', 'suntia27', 'sunchiyu', 'sunchiyu', 'sunxin25', 'sunxin25', 'sunmin50', 'sunmin50', 'taahata1', 'tabackad', 'tabackad', 'tahakhuw', 'tahakhuw', 'tahseen5', 'tanming4', 'tanming4', 'tanrich2', 'tangcat8', 'tangcat8', 'tangdanj', 'tangjo10', 'tazintas', 'tazintas', 'terefen5', 'terefen5', 'tongalwy', 'tongalwy', 'torres81', 'torres81', 'tsoulihs', 'tsoulihs', 'tualfa', 'tualfa', 'tuyuchen', 'tuyuchen', 'uguroyku', 'uguroyku', 'vadonama', 'vaishaka', 'wadhwaj2', 'wadhwaj2', 'wanglyu', 'wangt266', 'wangt266', 'wang3454', 'wang3454', 'waqarers', 'waqarers', 'juhwang', 'weijiaxi', 'wenjiah1', 'woojimin', 'woojimin', 'wucary', 'wuedwar5', 'xiangke1', 'xiaoji51', 'xiaoji51', 'xiechri7', 'xuyunxi1', 'xuyunxi1', 'xuechen7', 'yamaokaf', 'yamaokaf', 'yanbryan', 'yanbryan', 'yangz248', 'yangz248', 'yaokevi2', 'yaokevi2', 'yuzhengf', 'yuzhengf', 'yurache6', 'yurache6', 'zaidis72', 'zaidis72', 'zannierm', 'zannierm', 'zhan9202', 'zhan9202', 'zha12533', 'zha12533', 'zha13062', 'zha13062', 'zha13137', 'zha12442', 'zha12442', 'zha13148', 'zha13148', 'zha12746', 'zha12746', 'zha13015', 'zha13015', 'zha13280', 'zha13280', 'zha12747', 'zha12747', 'zha12504', 'zha12504', 'zha10716', 'zhan9375', 'zhan9375', 'zhaoho35', 'zhaoru59', 'zhengle4', 'zhengle4', 'zhengso7', 'zhengso7', 'zhousih5', 'zhousih5', 'zhouy309', 'zhouy309', 'zhurick1', 'zhurick1', 'zhuryan1', 'zhuanga2', 'zhuanga2', 'zongchuy', 'zoujing9', 'zoujing9', 'zuoyixia', 'zuoyixia', ]
        #for student in students:
        #    s.add(student)
        #print(len(s))
