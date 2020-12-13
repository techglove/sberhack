import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from parsers.database_handler import DatabaseReader
from settings import DB_HOST, DB_LOGIN, DB_DATABASE, DB_PASSWORD


app = Flask(__name__)
CORS(app)

database_reader = DatabaseReader(DB_HOST, DB_LOGIN, DB_PASSWORD, DB_DATABASE)


def get_cities(places):
    cities_ids = (place.city_id for place in places)
    cities = database_reader.get_cities(cities_ids)
    response = {}
    for city in cities:
        response[city.id] = city.name
    return response


def get_orgs(places):
    orgs_ids = (place.org_id for place in places)
    orgs = database_reader.get_orgs(orgs_ids)
    response = {}
    for org in orgs:
        response[org.id] = org.name
    return response


def output_place(place, orgs, cities):
    return {
        'organisation': orgs[place.org_id] if place.org_id in orgs else "Unknown",
        'city': cities[place.city_id] if place.city_id in cities else "Unknown",
        'address': place.address,
        'coord': database_reader.convert_point_to_lat_lon(place.coord),
        'url': place.url,
        'pcr_test_price': place.pcr_test_price,
        'antibodies_test_price': place.antibodies_test_price,
        'time_of_completion': place.time_of_completion,
    }


@app.route('/list_all', methods=['GET'])
def list_all():
    try:
        city = request.args.get('city')
        position_str = request.args.get('position')
        position_coords = None
        if position_str:
            position_coords = [float(x) for x in position_str.split(',')]
            if len(position_coords) != 2:
                return jsonify(ok=False, message="position should be in format 'lon0,lat0'"), 400

        places = database_reader.get_all_places(city, position_coords)
        cities = get_cities(places)
        orgs = get_orgs(places)
        response = jsonify(
            ok=True,
            places=[output_place(place, orgs, cities) for place in places]
        )
        return response, 200
    except:
        return jsonify(ok=False, message="Server internal error"), 500


@app.route('/list', methods=['GET'])
def list_places():
    try:
        viewport_str = request.args.get('viewport')
        sort = request.args.get('sort')
        position_str = request.args.get('position')
        distance_str = request.args.get('distance')
        position_coords = None
        viewport_coords = None
        distance = 100000

        if not viewport_str and not position_str:
            return jsonify(ok=False, message="position or viewport cgi is required"), 400

        if position_str:
            position_coords = [float(x) for x in position_str.split(',')]
            if len(position_coords) != 2:
                return jsonify(ok=False, message="position should be in format 'lon0,lat0'"), 400
            if distance_str:
                try:
                    distance = float(distance_str)
                except:
                    pass

        if viewport_str:
            viewport_coords = [float(x) for x in viewport_str.split(',')]
            if len(viewport_coords) != 4:
                return jsonify(ok=False, message="viewport should be in format 'lon0,lat0,lon1,lat1'"), 400

        sort_close_to = None
        if sort:
            sort_close_to = [(viewport_coords[0] + viewport_coords[2]) / 2,
                             (viewport_coords[1] + viewport_coords[3]) / 2]
        places = []
        if viewport_coords:
            places = database_reader.get_places_in_rect(viewport_coords, sort_close_to)
        if position_coords:
            places = database_reader.get_places_near_point(position_coords, distance)

        if len(places) == 0:
            return jsonify(ok=True, places=[]), 404
        cities = get_cities(places)
        orgs = get_orgs(places)
        response = jsonify(
            ok=True,
            places=[output_place(place, orgs, cities) for place in places]
        )
        return response, 200
    except:
        raise
        return jsonify(ok=False, message="Server internal error"), 500


@app.route('/news', methods=['GET'])
def list_news():
    news = {
        'news': [{
                'header': 'Москва расширила список тех, кому сделают прививку от COVID-19. - Meduza - Сайт Сергея Собянина - 15:54, 11 декабря 2020',
                'text': '<p>С 14 декабря власти Москвы расширяют список лиц, которые могут сделать прививку от COVID-19. Как объявил мэр Москвы Сергей Собянин, вакцинироваться смогут «работники МФЦ, культуры, а также работники торговли и услуг».</p> \n<p>«По роду своей работы они контактируют с миллионами граждан, рискуют сами, а в случае заболевания представляют угрозу для окружающих», — сообщается на сайте Собянина.</p>',
                'pic': 'https://cdn.sobyanin.ru/post/b0/21/be66ec38f1f22d440af8399f6d0f842902972426.jpg'
            },
            {
                'header': 'В России за сутки выявлены 28 137 новых случаев заболевания ковидом — на 448 меньше, чем днем ранее. - Meduza - Стопкоронавирус.рф - 11:06, 12 декабря 2020',
                'text': '<p>В России за прошедшие сутки зарегистрированы 28 137 новых случаев заражения коронавирусной инфекцией, сообщает оперативный штаб по борьбе с вирусом. Это на 448 случаев меньше, чем днем ранее.</p>\n<p>Больше всего заболевших в Москве (+6622 случая за сутки), Петербурге (+3776) и Подмосковье (+1393). Общее число инфицированных в стране достигло 2 625 848 человек.</p>\n<p>За сутки от коронавируса умерли 560 человек, за все время с начала пандемии, по данным оперативного штаба, — 46 453 человека.</p>\n<p>Выздоровели в общей сложности 2 085 958 человек, в том числе 26 118 пациентов выписаны из больниц за минувший день.</p>',
                'pic': 'https://img.vesti-yamal.ru/i/6c/6c3fa476a3b36ee95977565dfbf9b020.jpg'
            },
            {
                'header': '120 тысяч погибших с начала пандемии. «Медиазона» исследовала избыточную смертность в России. - Медиазона - 12:00, 23 ноября 2020',
                'text': '<p>За время пандемии COVID-19 с апреля по октябрь 2020 года в России умерло на 120 тысяч человек больше, чем в среднем за этот период за последние 5 лет, следует из данных Росстата, которые изучила «Медиазона». Избыточная смертность составила 18%.</p>\n<p>Если учесть только период с апреля по сентябрь — те месяцы, по которым есть полные данные Росстата — то прирост смертности составит 106 тысяч человек.</p>\n<p>По официальной статистике Роспотребнадзора за апрель-сентябрь в России от COVID-19 умерло в пять раз меньше — 20 698 человек. Росстат, который ведет подсчет жертв коронавируса по другой методике, дает другую цифру — 55,6 тысяч человек. Но даже оценка Росстата не объясняет такую избыточную смертность.</p> \n<p>Примечание: избыточная смертность за апрель-октябрь составляла 120 тысяч человек на момент публикации текста 23 ноября. 26 ноября мы обновили инфографику, так как отчитались еще несколько ЗАГСов; по этим данным она превысила 124 тысячи.</p> ',
                'pic': 'https://www.lrt.lt/img/2020/10/17/743487-56050-1287x836.jpg'
            },
            {
                'header': 'В США одобрили использование вакцины Pfizer и BioNTech от COVID-19. - Новая газета - 10:00, 12 декабря 2020',
                'text': '<p>Управление по санитарному надзору за качеством пищевых продуктов и медикаментов (FDA) США одобрило использование в стране вакцины от COVID-19, произведенной американской компанией Pfizer и немецкой BioNTech. Об этом говорится в сообщении управления. </p>\n<p>Вакцинироваться смогут люди от 16 лет. Как отмечает CNN, в ближайшие недели в США могут привить от коронавируса примерно 20 млн человек. Президент США Дональд Трамп заявил, что вакцинация начнется не менее чем через 24 часа. «Мы создали безопасную и эффективную вакцину всего за девять месяцев. Это одно из величайших научных достижений в истории», — сказал он</p>',
                'pic': 'https://img.gazeta.ru/files3/31/13392031/2020-12-08T132713Z_1626716802_RC21JK92Z0OR_RTRMADP_3_HEALTH-CORONAVIRUS-FDA-PFZIER-pic4_zoom-1500x1500-1164.JPG'
            },
            {
                'header': 'Сбербанк предупредил о риске заболеть COVID-19 из-за квитанций ЖКХ. - Ведомости 14:21, 4 декабря',
                'text': '<p>Сбербанк провел исследование и выявил пять групп людей, наиболее подверженных риску заражения коронавирусом. Среди них оказались те, кто оплачивает ЖКХ с помощью квитанций, рассказал в ходе конференции по искусственному интеллекту AI Journey первый заместитель председателя Сбербанка Александр Ведяхин.</p>\n<p>«Первые люди, максимально подверженные риску ковида, вот прям с огромным отрывом, — это люди, которые пользуются наличными денежными средствами. Вторая категория — это если человек платит с помощью квитанции ЖКХ. Все, что связано с наличными деньгами, наличными квитанциями и так далее — это все сильно увеличивает риск заболевания», — пояснил он.</p>\n<p>Также, по словам Ведяхина, риску заражения подвержены люди, которые активнее большинства используют общественный транспорт. Кроме того, в Сбербанке выяснили, что частое использование каршеринга и такси также увеличивает шансы заболеть.</p>\n<p>Вдобавок в ходе исследования выяснилось, что заражению подвержены люди, в большом количестве покупающие лотерейные билеты. Ведяхин разъяснил, что это опять же связано с использованием бумажных носителей.</p>',
                'pic': 'https://im.kommersant.ru/Issues.photo/CORP/2020/04/30/KMO_175605_00037_1_t218_110309.jpg'
            }
        ]
    }
    return jsonify(news)


@app.route('/')
def hello_world():
    return jsonify(message="Hello world test")
