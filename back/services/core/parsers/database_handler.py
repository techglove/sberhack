import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    position_lat = Column(Float)
    position_lon = Column(Float)
    price = Column(String)
    url = Column(String)
    is_urgent = Column(Boolean)


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

    def add_test_place(self, city, med_org, address, position, url, price, is_urgent=False):
        city_id = self.get_or_add_city(city)
        org_id = self.get_or_add_med_org(med_org)
        test_place = TestPlace(
            org_id = org_id,
            city_id = city_id,
            address = address,
            position_lat = position['lat'],
            position_lon = position['lon'],
            url = url,
            price = price,
            is_urgent = is_urgent
        )

        self.session.add(test_place)
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
