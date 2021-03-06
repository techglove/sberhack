import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import cast
from geoalchemy2 import Geography, Geometry
from geoalchemy2.shape import to_shape
import argparse

Base = declarative_base()
Session = sessionmaker()

class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<City(id={}, name={})>".format(id, name)


class MedOrganisation(Base):
    __tablename__ = 'med_organisations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<MedOrganisation(id={}, name={})>".format(id, name)


class TestPlace(Base):
    __tablename__ = 'test_places'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('med_organisations.id'))
    city_id = Column(Integer, ForeignKey('cities.id'))
    address = Column(String)
    coord = Column(Geography('POINT'))
    url = Column(String)
    pcr_test_price = Column(String)
    antibodies_test_price = Column(String)
    time_of_completion = Column(String)


class TestType(Base):
    __tablename__ = 'test_type'
    id = Column(Integer, primary_key=True)
    type = Column(String)


class Tests(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('test_type.id'))
    org_id = Column(Integer, ForeignKey('med_organisations.id'))
    price = Column(String)
    is_urgent = Column(Boolean)
    options = Column(String)


class DatabaseReader:
    def __init__(self, host, user, password, database):
        self.engine = sqlalchemy.create_engine("postgresql+psycopg2://{}:{}@{}/{}".format(user, password, host, database))
        Session.configure(bind=self.engine)
        self.session = Session()

    def get_all_places(self, city, position = None):
        query = self.session.query(TestPlace)
        if city:
            req_city_id = self.get_city_by_name(city)
            query = query.filter_by(city_id=req_city_id)

        if position is not None:
            query = query.order_by(func.ST_DistanceSphere(func.ST_GeomFromText('POINT({} {} 4326)'.format(position[0], position[1])), cast(TestPlace.coord, Geometry),))

        places = query.limit(1000)
        return [place for place in places]

            # places = database_reader.get_places_near_point(position_coords, distance)

    def get_places_near_point(self, position, distance):
        query = self.session.query(TestPlace)
        query = query.filter(func.ST_DistanceSphere(func.ST_GeomFromText('POINT({} {} 4326)'.format(position[0], position[1])), cast(TestPlace.coord, Geometry),) <= distance)
        query = query.order_by(func.ST_DistanceSphere(func.ST_GeomFromText('POINT({} {} 4326)'.format(position[0], position[1])), cast(TestPlace.coord, Geometry),))
        places = query.limit(100)
        return [place for place in places]

    def get_places_in_rect(self, rect, sort_close_to = None):
        query = self.session.query(TestPlace)
        query = query.filter(func.ST_Contains(func.ST_MakeEnvelope(rect[0], rect[1], rect[2], rect[3], 4326), cast(TestPlace.coord, Geometry)))
        if sort_close_to is not None:
            query = query.order_by(func.ST_DistanceSphere(func.ST_GeomFromText('POINT({} {} 4326)'.format(sort_close_to[0], sort_close_to[1])), cast(TestPlace.coord, Geometry),))
        places = query.limit(100)
        return [place for place in places]

    def convert_point_to_lat_lon(self, point):
        shape = to_shape(point)
        return {'lat': shape.y, 'lon': shape.x}

    def get_city_by_name(self, city_name):
        return self.session.query(City).filter_by(name=city_name).first()

    def get_org_by_name(self, org_name):
        return self.session.query(MedOrganisation).filter_by(name=org_name).first()

    def get_cities(self, cities_ids):
        return [city for city in self.session.query(City).filter(City.id.in_(cities_ids))]

    def get_orgs(self, orgs_ids):
        return [org for org in self.session.query(MedOrganisation).filter(MedOrganisation.id.in_(orgs_ids))]

class TestPlacePusher:
    def __init__(self, host, user, password, database):
        self.engine = sqlalchemy.create_engine("postgresql+psycopg2://{}:{}@{}/{}".format(user, password, host, database))
        Session.configure(bind=self.engine)
        self.session = Session()

    def get_or_add_city(self, city_name):
        city = self.session.query(City).filter_by(name=city_name).first()
        if city:
            return city.id
        else:
            city = City(name=city_name)
            self.session.add(city)
            self.session.commit()
            return city.id

    def get_or_add_med_org(self, med_org):
        org = self.session.query(MedOrganisation).filter_by(name=med_org).first()
        if org:
            return org.id
        else:
            org = MedOrganisation(name=med_org)
            self.session.add(org)
            self.session.commit()
            return org.id

    def add_test_place(self, city, med_org, address, position, url, pcr_test_price, antibodies_test_price, time_of_completion):
        city_id = self.get_or_add_city(city)
        org_id = self.get_or_add_med_org(med_org)
        test_place = TestPlace(
            org_id=org_id,
            city_id=city_id,
            address=address,
            coord='POINT({} {})'.format(position['lat'], position['lon']),
            url=url,
            pcr_test_price=pcr_test_price,
            antibodies_test_price=antibodies_test_price,
            time_of_completion=time_of_completion
        )

        self.session.add(test_place)
        self.session.commit()

    def add_test_type(self, type: str):
        test_place = TestType(type=type)
        self.session.add(test_place)
        self.session.commit()

    def add_test(self, type_id: int, org_id: int, price: str, is_urgent: bool, options: str):
        test = Tests(
            type_id=type_id,
            org_id=org_id,
            price=price,
            is_urgent=is_urgent,
            options=options
        )
        self.session.add(test)
        self.session.commit()


def test_inserter():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_host', type=str)
    parser.add_argument('--db_user', type=str)
    parser.add_argument('--db_password', type=str)
    parser.add_argument('--db_name', type=str)
    args = parser.parse_args()
    pusher = TestPlacePusher(args.db_host, args.db_user, args.db_password, args.db_name)
    pusher.add_test_place('Moscow', 'Gemotest', 'Arbat 1', {'lat': 12.1, 'lon': 29.7}, "http://gemotest.ru", "1700", False)


if __name__ == '__main__':
    test_inserter()
